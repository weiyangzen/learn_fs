# sources/distributed-fs/ceph-client/lib/fonts/font_ter16x32.c

## Purpose
`font_ter16x32.c` provides the compiled-in Terminus 16x32 console bitmap font. It is almost entirely static glyph data: 256 glyphs, each 16 pixels wide by 32 pixels high, stored in the kernel console font format and exposed through a `struct font_desc`.

## Important APIs, Types, and Functions
The file defines `FONTDATAMAX` as 16384 bytes, `static const struct font_data fontdata_ter16x32`, and the exported descriptor `const struct font_desc font_ter_16x32`. The descriptor sets `.idx = TER16x32_IDX`, `.name = "TER16x32"`, `.width = 16`, `.height = 32`, `.charcount = 256`, and `.data = fontdata_ter16x32.data`. On sparc, `.pref` is `5`; elsewhere it is `-1`.

## Control Flow, State, and Persistence
There is no runtime control flow. The byte array is immutable static data linked into the kernel image when `CONFIG_FONT_TER16x32` includes it. Runtime font selection code consumes the descriptor through the font registry in `fonts.c`.

## Dependencies and Integration Points
It includes `<linux/module.h>` and local `font.h` for `struct font_data`, `struct font_desc`, and font indexes. The main integration point is `fonts.c`, which conditionally adds `&font_ter_16x32` to the `fonts[]` lookup table.

## Risks and Test Signals
Risks are data integrity and geometry consistency: `FONTDATAMAX` must match 256 glyphs * 32 rows * 2 bytes per row, and descriptor width/height must match the byte layout. Since this is static asset data, useful signals are build coverage with `CONFIG_FONT_TER16x32`, console/font lookup tests that select `TER16x32`, and visual or checksum validation of rendered glyphs.
