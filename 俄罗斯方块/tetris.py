import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 设置字体
font = pygame.font.SysFont("SimHei", 30)

# 定义俄罗斯方块形状
SHAPES = [
    # I 形
    [[1, 1, 1, 1]],
    # J 形
    [[1, 0, 0], [1, 1, 1]],
    # L 形
    [[0, 0, 1], [1, 1, 1]],
    # O 形
    [[1, 1], [1, 1]],
    # S 形
    [[0, 1, 1], [1, 1, 0]],
    # T 形
    [[0, 1, 0], [1, 1, 1]],
    # Z 形
    [[1, 1, 0], [0, 1, 1]]
]

# 方块颜色
SHAPE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class TetrisGame:
    def __init__(self):
        self.reset()
        self.clock = pygame.time.Clock()
        self.fall_speed = 0.5
        self.last_fall_time = pygame.time.get_ticks()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.game_started = False  # 添加游戏是否开始的标志
    
    def reset(self):
        # 初始化游戏网格
        self.board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        # 生成新方块
        self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.game_started = False
    
    def new_piece(self):
        # 随机选择方块形状
        self.piece_shape = random.choice(SHAPES)
        self.piece_color = SHAPE_COLORS[SHAPES.index(self.piece_shape)]
        # 设置方块初始位置
        self.piece_x = GRID_WIDTH // 2 - len(self.piece_shape[0]) // 2
        self.piece_y = 0
        # 检查游戏是否结束
        if not self.is_valid_position():
            self.game_over = True
    
    def is_valid_position(self):
        # 检查方块位置是否有效
        for y, row in enumerate(self.piece_shape):
            for x, cell in enumerate(row):
                if cell:
                    if (y + self.piece_y >= GRID_HEIGHT or 
                        x + self.piece_x < 0 or 
                        x + self.piece_x >= GRID_WIDTH or 
                        self.board[y + self.piece_y][x + self.piece_x] != BLACK):
                        return False
        return True
    
    def rotate_piece(self):
        # 旋转方块
        # 保存当前形状
        current_shape = self.piece_shape
        # 计算旋转后的形状（转置矩阵并反转每一行）
        rows, cols = len(current_shape), len(current_shape[0])
        rotated_shape = [[current_shape[rows-j-1][i] for j in range(rows)] for i in range(cols)]
        # 应用旋转
        self.piece_shape = rotated_shape
        # 如果旋转后位置无效，则恢复原形状
        if not self.is_valid_position():
            self.piece_shape = current_shape
    
    def move(self, dx, dy):
        # 移动方块
        self.piece_x += dx
        self.piece_y += dy
        # 如果移动后位置无效，则恢复原位置
        if not self.is_valid_position():
            self.piece_x -= dx
            self.piece_y -= dy
            return False
        return True
    
    def drop(self):
        # 尝试下落方块
        if not self.move(0, 1):
            # 如果无法下落，将方块固定到游戏板上
            self.lock_piece()
            # 检查是否有完整的行
            self.check_lines()
            # 生成新方块
            self.new_piece()
            return False
        return True
    
    def hard_drop(self):
        # 硬下落，直接落到底部
        while self.drop():
            pass
    
    def lock_piece(self):
        # 将方块固定到游戏板上
        for y, row in enumerate(self.piece_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[y + self.piece_y][x + self.piece_x] = self.piece_color
    
    def check_lines(self):
        # 检查并消除完整的行
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            # 检查当前行是否全满
            if all(cell != BLACK for cell in self.board[y]):
                # 消除当前行
                del self.board[y]
                # 在顶部添加空行
                self.board.insert(0, [BLACK for _ in range(GRID_WIDTH)])
                # 增加消除行数
                lines_cleared += 1
                # 由于删除了一行，y保持不变继续检查新移上来的行
            else:
                y -= 1
        
        # 根据消除行数增加分数
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared == 4:
            self.score += 800 * self.level
        
        # 更新关卡
        self.level = self.score // 1000 + 1
        # 调整下落速度
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def draw_board(self):
        # 计算游戏区域位置（居中显示）
        board_x = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
        board_y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2
        
        # 绘制游戏区域边框
        pygame.draw.rect(screen, WHITE, (board_x - 2, board_y - 2, 
                                        GRID_WIDTH * GRID_SIZE + 4, 
                                        GRID_HEIGHT * GRID_SIZE + 4), 2)
        
        # 绘制游戏网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, self.board[y][x], 
                                (board_x + x * GRID_SIZE, 
                                board_y + y * GRID_SIZE, 
                                GRID_SIZE, GRID_SIZE))
                # 绘制网格线
                pygame.draw.rect(screen, GRAY, 
                                (board_x + x * GRID_SIZE, 
                                board_y + y * GRID_SIZE, 
                                GRID_SIZE, GRID_SIZE), 1)
        
        # 绘制当前方块
        for y, row in enumerate(self.piece_shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.piece_color, 
                                    (board_x + (self.piece_x + x) * GRID_SIZE, 
                                    board_y + (self.piece_y + y) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                    (board_x + (self.piece_x + x) * GRID_SIZE, 
                                    board_y + (self.piece_y + y) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE), 1)
    
    def draw_info(self):
        # 绘制游戏信息（分数、关卡等）
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        level_text = font.render(f"关卡: {self.level}", True, WHITE)
        
        # 计算信息显示位置
        info_x = (SCREEN_WIDTH + GRID_WIDTH * GRID_SIZE) // 2 + 20
        info_y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2
        
        screen.blit(score_text, (info_x, info_y))
        screen.blit(level_text, (info_x, info_y + 40))
        
        # 绘制操作说明
        controls = [
            "操作说明:",
            "← →: 左右移动",
            "↑: 旋转方块",
            "↓: 加速下落",
            "空格: 硬下落",
            "P: 暂停游戏",
            "R: 重新开始"
        ]
        
        for i, text in enumerate(controls):
            control_text = font.render(text, True, WHITE)
            screen.blit(control_text, (info_x, info_y + 120 + i * 35))
    
    def draw_game_over(self):
        # 绘制游戏结束画面
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # 半透明黑色覆盖
        screen.blit(overlay, (0, 0))
        
        game_over_text = font.render("游戏结束", True, RED)
        final_score_text = font.render(f"最终分数: {self.score}", True, WHITE)
        restart_text = font.render("按 R 键重新开始", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 - 50))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2,
                                     SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2 + 50))
    
    def draw_pause(self):
        # 绘制暂停画面
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # 半透明黑色覆盖
        screen.blit(overlay, (0, 0))
        
        pause_text = font.render("游戏暂停", True, WHITE)
        continue_text = font.render("按 P 键继续", True, WHITE)
        
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 25))
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 + 25))
    
    def handle_events(self):
        # 处理用户输入事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # 如果游戏未开始，按任意键开始游戏
                if not self.game_started:
                    self.game_started = True
                    self.last_fall_time = pygame.time.get_ticks()
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                            self.score += 1  # 软下落加分
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                            self.score += 2  # 硬下落额外加分
        return True
    
    def update(self):
        # 更新游戏状态
        if not self.game_started or self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fall_time > self.fall_speed * 1000:
            self.drop()
            self.last_fall_time = current_time
    
    def draw_start_screen(self):
        # 绘制游戏开始界面
        screen.fill(BLACK)
        
        title_text = font.render("俄罗斯方块", True, WHITE)
        start_text = font.render("按任意键开始游戏", True, WHITE)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 50))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    def draw(self):
        # 绘制游戏画面
        if not self.game_started:
            self.draw_start_screen()
            return
        
        screen.fill(BLACK)
        self.draw_board()
        self.draw_info()
        
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
        
        pygame.display.flip()
    
    def run(self):
        # 游戏主循环
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 主程序入口
if __name__ == "__main__":
    game = TetrisGame()
    game.run()
