# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/bitblit.c

## Purpose

This file implements the standard pixel-based framebuffer-console bitblit operations. It adapts console character cells to fbdev `fb_copyarea`, `fb_fillrect`, `fb_imageblit`, and cursor operations for drivers using packed-pixel drawing. The complete 394-line source was read.

## Important APIs, Types, and Functions

Key functions are `update_attr()`, `bit_bmove()`, `bit_clear()`, `bit_putcs_aligned()`, `bit_putcs_unaligned()`, `bit_putcs()`, `bit_clear_margins()`, `bit_cursor()`, `bit_update_start()`, and `fbcon_set_bitops_ur()`. The exported behavior is through the local `struct fbcon_bitops bit_fbcon_bitops` assigned to `struct fbcon_par`.

## Control Flow

Fbcon selects these bitops for unrotated pixel consoles. Character movement maps cell coordinates to pixel rectangles and calls the driver copyarea operation. Clear maps cell rectangles to fillrect with the background color. `bit_putcs()` chunks glyphs into `info->pixmap`, applies underline/bold/reverse attributes when needed, handles byte-aligned and unaligned font widths, clips against visible x/y resolution, and submits a 1-bit `fb_image` to the driver. Cursor handling tracks cached cursor image, colors, position, size, hot spot, and mask in `fbcon_par`; it calls the driver cursor callback when available and falls back to `soft_cursor()` on error.

## State and Persistence Behavior

State is held in `fbcon_par` cursor caches, `info->pixmap`, and transient kmalloc buffers for attributed glyphs and cursor masks. There is no persistent storage. Console screen contents remain owned by the console layer, while this file translates them into framebuffer drawing calls.

## Dependencies and Integration Points

The file depends on fbcon internals, virtual console state, `scr_readw()`, font metadata, `fb_pad_aligned_buffer()`, `fb_pad_unaligned_buffer()`, `fb_get_buffer_offset()`, driver fbops, and soft cursor support. It is built into `fb.o` when `CONFIG_FRAMEBUFFER_CONSOLE=y`.

## Risks and Edge Cases

Risks include atomic allocation failures causing skipped glyph/cursor updates, reliance on driver `fb_imageblit()` clipping correctness after local clipping, attribute expansion overhead, handling high fonts through `vc_hi_font_mask`, and cursor cache lifetime around font changes. `bit_putcs()` computes `maxcnt = info->pixmap.size / cellsize`; malformed pixmap sizing or zero cellsize would be serious, though fbcon normally validates fonts.

## Test Signals

Exercise console scrolling, clear, margins, putcs with aligned and unaligned font widths, underline/bold/reverse attributes, high-font characters, cursor shape/position/color changes, hardware cursor failure fallback, panning update_start, and small pixmap chunking.
