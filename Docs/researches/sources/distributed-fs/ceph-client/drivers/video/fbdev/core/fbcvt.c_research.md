<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c

## Purpose

`fbcvt.c` computes VESA Coordinated Video Timings for fbdev modes requested through the `M`/`R` modeline syntax. It turns resolution, refresh, margins, reduced blanking, and interlace flags into a `struct fb_videomode`. The file was read as a complete 368-line source.

## Important APIs, Types, and Functions

The public API is `fb_find_mode_cvt(struct fb_videomode *mode, int margins, int rb)`. Internal state is `struct fb_cvt_data`, which holds resolution, refresh, pixel clock, horizontal/vertical totals, blanking, margins, sync widths, aspect ratio, flags, and status. Helpers calculate horizontal period, ideal duty cycle, blanking, sync widths, vertical totals, pixel clock, aspect ratio, printable CVT name, and conversion into `fb_videomode`.

## Control Flow

The caller pre-fills `mode->xres`, `mode->yres`, `mode->refresh`, and `mode->vmode`. `fb_find_mode_cvt()` validates input, marks non-standard refresh/aspect cases, rounds x resolution to 8-pixel cells, doubles field refresh for interlace, computes optional margins, derives aspect-specific vsync, calculates totals/blanking/porches/clock, logs the CVT name, and writes timing fields back to `mode`.

## State and Persistence Behavior

All computation is stack-local. The only side effect outside the output mode is informational kernel logging for invalid, non-standard, advisory, and generated-name cases.

## Dependencies and Integration Points

`modedb.c` calls this from `fb_find_mode()` when parsing CVT mode strings. It uses fbdev macros such as `KHZ2PICOS` and flags like `FB_VMODE_INTERLACED`, `FB_SYNC_HOR_HIGH_ACT`, and `FB_SYNC_VERT_HIGH_ACT`.

## Risks and Edge Cases

The code uses integer arithmetic; overflow and truncation risk grows with very large resolutions or refresh rates. Reduced blanking is only advisory for non-60 Hz. Non-standard aspect ratios still compute timings but mark status.

## Test Signals

Test `fb_find_mode()` strings such as `1024x768M`, `1920x1080MR-32@60`, interlaced modes, margins, invalid zero dimensions, high refresh values, and compare generated timings with known CVT references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c -->
