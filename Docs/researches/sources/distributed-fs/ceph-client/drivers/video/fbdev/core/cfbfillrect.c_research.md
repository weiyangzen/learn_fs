# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbfillrect.c

## Purpose

This file exports `cfb_fillrect()`, the generic I/O-memory packed-pixel rectangle-fill helper for fbdev drivers. The complete 36-line source was read.

## Important APIs, Types, and Functions

The sole runtime API is `cfb_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`. It uses `cfbmem.h` and `fb_fillrect.h`, with optional reverse-pixel support through `CONFIG_FB_CFB_REV_PIXELS_IN_BYTE`.

## Control Flow

The wrapper checks `FBINFO_STATE_RUNNING`, warns once if the framebuffer is not I/O memory, calls `fb_sync()` when the driver provides it, and then delegates to inline `fb_fillrect()`.

## State and Persistence Behavior

No independent state is stored. It modifies framebuffer memory according to the requested rectangle, color, and raster operation.

## Dependencies and Integration Points

It integrates with drivers that use `cfb_fillrect()` fallback or default I/O-memory draw macros, and with the shared packed-pixel fill implementation in `fb_fillrect.h`.

## Risks and Edge Cases

The wrapper itself is simple; risks lie in memory-type mismatch, invalid rectangles passed by callers, low-bpp color packing, endian/byte reversal, and XOR versus copy raster operation correctness.

## Test Signals

Test copy and XOR fills for 1/2/4/8/16/24/32 bpp, unaligned rectangles, out-of-bounds clipping by upper layers, `fb_sync()` call ordering, stopped framebuffer state, and virtual-memory warning paths.
