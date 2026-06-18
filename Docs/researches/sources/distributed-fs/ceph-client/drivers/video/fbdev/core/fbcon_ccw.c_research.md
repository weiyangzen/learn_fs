<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c

## Purpose

`fbcon_ccw.c` implements framebuffer console bitops for 270-degree counter-clockwise software rotation. It lets the common fbcon engine draw logical text cells while mapping them into rotated framebuffer coordinates and rotated glyph data. The file was read as a complete 376-line source.

## Important APIs, Types, and Functions

The public handoff is `fbcon_set_bitops_ccw()`, which installs `ccw_fbcon_bitops`. Internal operations are `ccw_bmove`, `ccw_clear`, `ccw_putcs`, `ccw_clear_margins`, `ccw_cursor`, `ccw_update_start`, and `ccw_update_attr`. Drawing uses `fb_copyarea`, `fb_fillrect`, `fb_imageblit`, pixmap padding helpers, and `par->rotated.buf`.

## Control Flow

`fbcon.c` selects this table for `FB_ROTATE_CCW`. Copy/clear operations compute framebuffer rectangles with x based on logical rows and y mirrored from `GETVYRES()`. `ccw_putcs()` reverses the glyph order, batches cells to fit the pixmap scratch buffer, applies monochrome attributes when needed, pads glyph data, and calls `fb_imageblit()`. Cursor drawing rotates the cursor mask with `font_glyph_rotate_270()`, tries hardware `fb_cursor`, and falls back to `soft_cursor()`.

## State and Persistence Behavior

There is no file-local persistent state. The code mutates `par->cursor_state`, `par->cursor_data`, `par->p->cursor_shape`, and `par->var`. Temporary attribute buffers are allocated per draw or cursor update.

## Dependencies and Integration Points

The file depends on `fbcon.h`, `fbcon_rotate.h`, VT cursor/font state, font rotation helpers, and fbdev drawing callbacks. `ccw_update_start()` integrates with core panning by translating logical offsets into rotated `xoffset`/`yoffset`.

## Risks and Edge Cases

Coordinate transforms depend on virtual y resolution and scroll mode. Atomic allocation failure can skip cursor updates. Attribute rendering mainly applies to monochrome. If `par->rotated.buf` is absent, drawing returns without output.

## Test Signals

Use `fbcon=rotate:3` or sysfs rotation to verify text, scrolling, margins, cursor position, pan/wrap update, 256/512 glyph fonts, and hardware-cursor fallback under KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c -->
