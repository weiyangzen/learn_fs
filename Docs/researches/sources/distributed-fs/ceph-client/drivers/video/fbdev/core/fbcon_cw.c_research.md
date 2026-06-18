<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c

## Purpose

`fbcon_cw.c` implements framebuffer console bitops for 90-degree clockwise software rotation. It maps logical console rows and columns into rotated framebuffer rectangles and renders from a cached rotated font buffer. The file was read as a complete 359-line source.

## Important APIs, Types, and Functions

The setup API is `fbcon_set_bitops_cw()`, which installs `cw_fbcon_bitops`. Core helpers are `cw_bmove`, `cw_clear`, `cw_putcs`, `cw_clear_margins`, `cw_cursor`, `cw_update_start`, and `cw_update_attr`. These operate through `struct fb_copyarea`, `struct fb_fillrect`, `struct fb_image`, `struct fb_cursor`, and `par->rotated`.

## Control Flow

Clockwise copy and clear calls translate logical y into mirrored framebuffer x using `GETVXRES()` and logical x into framebuffer y. `cw_putcs()` computes rotated glyph size from font height, batches glyphs by pixmap capacity, applies attributes into a temporary buffer, pads data, then issues `fb_imageblit()`. `cw_cursor()` mirrors the same geometry, rotates the cursor mask with `font_glyph_rotate_90()`, and falls back to `soft_cursor()` when hardware cursor support fails.

## State and Persistence Behavior

State lives in `fbcon_par`: cursor image/cmap/position cache, cursor data, cursor mask, display cursor shape, rotated font cache, and current panning var. There is no storage outside kernel memory.

## Dependencies and Integration Points

The file integrates with `fbcon_rotate_font()`, fbdev hardware callbacks (`fb_copyarea`, `fb_fillrect`, `fb_imageblit`, `fb_cursor`), `fb_pan_display()`, `fbcon_fill_cursor_mask()`, and font helpers.

## Risks and Edge Cases

Clockwise geometry must account for virtual x resolution only when panning can use it. Allocation failure for attribute or mask buffers drops an update. Pixmap alignment and `maxcnt` math are critical. The file returns early if rotated font data is unavailable.

## Test Signals

Test `rotate:1` on devices with and without xpan support, wide and narrow fonts, monochrome attributes, cursor shape changes, scrolling, sysfs rotation changes, and hardware cursor fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c -->
