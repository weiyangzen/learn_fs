<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c

## Purpose

`fbcon_ud.c` implements framebuffer console bitops for 180-degree upside-down software rotation. It mirrors logical console output across both framebuffer axes while preserving the common fbcon rendering API. The file was read as a complete 410-line source.

## Important APIs, Types, and Functions

`fbcon_set_bitops_ud()` installs `ud_fbcon_bitops`. Internal helpers include `ud_bmove`, `ud_clear`, `ud_putcs`, `ud_putcs_aligned`, `ud_putcs_unaligned`, `ud_clear_margins`, `ud_cursor`, `ud_update_start`, and `ud_update_attr`. It uses generic fbdev copy/fill/image/cursor helpers, padding helpers, `fb_pan_display`, and `font_glyph_rotate_180()`.

## Control Flow

Copy and clear mirror both x and y using `GETVXRES()` and `GETVYRES()`. `ud_putcs()` starts from the last character because upside-down rendering reverses order, builds framebuffer image batches, and chooses aligned or unaligned padding based on font width modulo 8. `ud_cursor()` mirrors the glyph and cursor mask, sets changed cursor fields, and falls back to `soft_cursor()`. `ud_update_start()` translates logical pan offsets into mirrored offsets.

## State and Persistence Behavior

Persistent state is in `fbcon_par`: rotated font buffer, cursor cache, cursor data/mask, cursor shape, and copied `var`. Temporary attribute buffers are per operation.

## Dependencies and Integration Points

The file integrates with rotated font cache creation, common cursor mask generation, fbdev drawing/panning callbacks, and VT font/cursor metadata.

## Risks and Edge Cases

The unaligned glyph path is sensitive to shift and stride math. Mirrored pan offsets can go negative and require correction. Allocation failure skips cursor updates. No glyph output occurs if `par->rotated.buf` is absent.

## Test Signals

Use `rotate:2` with odd-width fonts, 512-character fonts, accelerated and non-accelerated devices, cursor shape changes, bottom/right margin clears, and pan/scroll operations under KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c -->
