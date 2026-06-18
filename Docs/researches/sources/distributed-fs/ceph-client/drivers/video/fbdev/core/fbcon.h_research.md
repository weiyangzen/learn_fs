<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h

## Purpose

`fbcon.h` is the private interface shared by fbcon core, normal/rotated/tile bitops, and `softcursor.c`. It defines the per-console display cache, per-framebuffer console private state, bitops dispatch table, attribute decoding helpers, scrolling constants, and coordinate helpers. The file was read as a complete 236-line header.

## Important APIs, Types, and Functions

Key types are `struct fbcon_display`, `struct fbcon_bitops`, and `struct fbcon_par`. The display cache stores font data, scroll state, virtual rows, cursor shape, rotation, cached var fields, bitfields, and current `fb_videomode`. The bitops table provides `bmove`, `clear`, `putcs`, `clear_margins`, `cursor`, `update_start`, and optional `rotate_font`. `fbcon_par` stores cursor work/state, active display, owner `fb_info`, current console, cursor buffers, blank/graphics/rotation state, and rotated-font cache.

## Control Flow

The header has no standalone execution. Runtime dispatch flows from `fbcon.c` into whichever bitops table was installed by normal, clockwise, upside-down, counter-clockwise, or tile setup. Inline helpers `real_y()`, `get_attribute()`, `mono_col()`, `fb_scrollmode()`, and `FBCON_SWAP()` are used by drawing, scrolling, and rotation paths.

## State and Persistence Behavior

The header owns no storage. Its structures describe in-memory state that persists while a console is mapped to a framebuffer. Rotation buffers, cursor image/mask buffers, and font references must be managed by implementation files.

## Dependencies and Integration Points

It depends on Linux font, VT buffer, VT kernel, workqueue, I/O, fbdev, and console data types. It exposes `soft_cursor()` and `fbcon_fill_cursor_mask()` to rotated cursor paths and shares scroll constants with `fbcon_rotate.h`.

## Risks and Edge Cases

Shared private structure layout makes mismatched assumptions across bitops risky. `FBCON_SWAP()` relies on compatible operand types. `get_attribute()` only reports underline/reverse/bold for 1-bit color depth, so rotated attribute rendering depends on fb depth classification.

## Test Signals

Build with normal fbcon, rotation, legacy acceleration, and tileblitting configs. Runtime signals include correct scroll mode selection, rotated drawing, 512-glyph font handling, monochrome attributes, and cursor shape changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h -->
