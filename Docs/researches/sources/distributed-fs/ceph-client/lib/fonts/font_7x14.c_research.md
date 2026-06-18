# sources/distributed-fs/ceph-client/lib/fonts/font_7x14.c

## Purpose
Defines the built-in 7x14 bitmap console font, adapted from the 8x16 font lineage. It provides a medium-small 256-character glyph table and exports it as `font_7x14` for consoles and DRM panic output where the standard 8x16 font is too large.

## Important APIs, Types, And Functions
`FONTDATAMAX` is `3584`, matching `256 * 14` bytes. `fontdata_7x14` is a `static const struct font_data` containing the extra metadata words and a 14-byte-per-character glyph array. `font_7x14` is the public descriptor, with `.idx = FONT7x14_IDX`, `.name = "7x14"`, `.width = 7`, `.height = 14`, `.charcount = 256`, `.data = fontdata_7x14.data`, and `.pref = 0`. The file defines no executable functions.

## Control Flow
No local runtime control flow exists. The object is selected by `CONFIG_FONT_7x14` in `lib/fonts/Makefile`. When enabled, `fonts.c` inserts `&font_7x14` into the built-in font registry. `find_font("7x14")` returns the descriptor directly, while `get_default_font()` scores it against screen size, width/height support bitmaps, and its neutral preference value. Since its height is greater than eight, it is naturally favored less on very short screens and more viable on larger outputs.

## State And Persistence
The glyph table and descriptor are immutable static kernel data. There is no allocation, mutable module state, hardware programming, or durable persistence. The font remains available for the lifetime of the kernel image if compiled in.

## Dependencies And Integration Points
The file depends on local `font.h` for `struct font_data` and `FONT7x14_IDX`, and on the public `struct font_desc` contract in `include/linux/font.h`. Kconfig gates the font behind framebuffer console or DRM panic support and describes it as slightly smaller than the default. It integrates with `lib/fonts/fonts.c`, framebuffer console rendering, DRM panic text rendering, DRM client log paths, and font utility functions that export or rotate font data according to descriptor dimensions.

## Risks And Edge Cases
The descriptor and data must agree on 14 row bytes per glyph and 256 glyphs. Width seven still uses one byte per row, so the unused bit must not be treated as an eighth visible column by consumers. The file uses non-ASCII glyph labels in some comments for high-half characters; the comments document intent but the byte values are authoritative. Because it was adapted from a larger font, glyph edits can introduce vertical alignment or clipping mistakes if the 14-row baseline and top/bottom padding are not preserved. Changes to `.idx` or `.name` would break registry scoring or string lookups.

## Test Signals
Build with `CONFIG_FONT_7x14=y` should compile `font_7x14.o` and resolve `font_7x14` through `include/linux/font.h`. Static validation should check 3584 initializer bytes, exactly 256 glyphs, and fourteen bytes per glyph; this source was checked against those invariants. Runtime signals include `find_font("7x14")`, correct `get_default_font()` behavior when 7x14 dimensions are supported, successful font export sizing, and rendered framebuffer or DRM panic text with no shifted glyphs, clipped high-bit columns, or high-half character corruption.
