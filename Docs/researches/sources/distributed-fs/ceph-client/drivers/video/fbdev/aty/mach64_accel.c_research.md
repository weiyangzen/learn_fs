# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_accel.c

## Purpose

`mach64_accel.c` implements Mach64 2D acceleration for the `atyfb` framebuffer driver. It resets and initializes the GUI engine, sets the standard drawing context, and provides accelerated fbdev `copyarea`, `fillrect`, and `imageblit` callbacks with software fallbacks when acceleration is unavailable or inappropriate.

## Important APIs, Types, and Functions

The externally used functions are `aty_reset_engine()`, `aty_init_engine()`, `atyfb_copyarea()`, `atyfb_fillrect()`, and `atyfb_imageblit()`. `rotation24bpp()` computes Mach64's 24-bpp byte-rotation control for left-to-right or right-to-left operations because the engine operates in 8-bpp units for 24-bpp modes. `reset_GTC_3D_engine()` resets the RagePro/GTC 3D block for chips carrying `M64F_RESET_3D`. `draw_rect()` writes `DST_Y_X` and `DST_HEIGHT_WIDTH` and marks `par->blitter_may_be_busy`.

The file depends on FIFO/idle helpers from `atyfb.h`, register names and bit definitions from `<video/mach64.h>`, and fbdev software helpers `cfb_copyarea()`, `cfb_fillrect()`, and `cfb_imageblit()`.

## Control Flow

`aty_init_engine()` derives pitch and virtual width from `fb_info`; in 24-bpp it multiplies horizontal quantities by three. It optionally resets the 3D engine, resets the GUI engine, initializes VGA page pointers, then writes a standard context: destination/source pitch, source/destination defaults, host and pattern state, scissor bounds, foreground/background colors, write mask, mix mode, source selection, color compare, pixel width, chain mask, and miscellaneous 3D/interrupt/trajectory controls. It finishes with `wait_for_idle()`.

`atyfb_copyarea()` rejects sleeping devices and empty rectangles, falls back if `par->accel_flags` is zero, adjusts 24-bpp coordinates, chooses copy direction for overlap safety, computes 24-bpp rotation when needed, writes source/destination state, and starts the rectangle blit. `atyfb_fillrect()` resolves the fill color through `pseudo_palette` for true/direct color visuals, adjusts 24-bpp width and rotation, writes foreground and source/mix controls, then starts a rectangle fill. `atyfb_imageblit()` accelerates 1-bpp monochrome and same-depth image uploads, configures host pixel width and colors, starts the destination rectangle, and streams image data through `HOST_DATA0`; unsupported depth combinations fall back to `cfb_imageblit()`.

## State and Persistence Behavior

The persistent runtime state is in hardware registers plus `par->fifo_space` and `par->blitter_may_be_busy`. Engine reset clears cached FIFO accounting. Drawing operations set `blitter_may_be_busy` so `atyfb_sync()` or later mode-setting can wait for idle before touching state that must not race with the blitter. No file-backed state is maintained.

## Dependencies and Integration Points

This file is called from `atyfb_base.c` through `atyfb_ops` and from mode setup via `aty_init_engine()`. Correctness depends on `par->crtc.dp_pix_width`, `par->crtc.dp_chain_mask`, `info->fix.line_length`, `info->var.bits_per_pixel`, and `par->accel_flags` being prepared by `atyfb_set_par()`. The code also relies on endian-safe image reads via `get_unaligned_le32()` and writes through the driver's MMIO accessors.

## Risks and Edge Cases

24-bpp support is the most fragile path: coordinates are tripled, rotations depend on direction, and monochrome image expansion either uses `DP_HOST_TRIPLE_EN` only for aligned widths or manually triples bits. The manual expansion loop is easy to regress around non-byte-aligned widths. None of the accelerated paths clip rectangles locally; fbdev core is expected to provide valid regions, unlike the Radeon helpers that clamp. If acceleration is invoked while asleep, operations are silently ignored. FIFO waits must match the number of following register writes.

## Test Signals

Test mode switches into 8, 15, 16, 24, and 32 bpp with acceleration on and off; overlapping copy left/right and up/down; zero-size operations; truecolor and pseudocolor fills; monochrome imageblits with widths not divisible by 8; same-depth image uploads; 24-bpp glyph rendering with and without hardware triple support; sync after operations; and suspend paths that call drawing functions while `par->asleep` is set.
