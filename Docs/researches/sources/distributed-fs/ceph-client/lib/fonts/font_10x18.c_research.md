# sources/distributed-fs/ceph-client/lib/fonts/font_10x18.c

## Purpose
Defines the built-in 10x18 bitmap console font. The file is mostly static glyph data adapted from `font_sun12x22.c`, plus a `struct font_desc` that registers the font with the kernel font library.

## Important APIs, Types, and Functions
The main data object is `static const struct font_data fontdata_10x18`, with `FONTDATAMAX` set to 9216 bytes. It stores 256 glyphs, each 10 pixels wide by 18 rows high, encoded as two bytes per row with comments showing the 10-bit bitmap. The exported descriptor is `const struct font_desc font_10x18` with `.idx = FONT10x18_IDX`, `.name = "10x18"`, `.width = 10`, `.height = 18`, `.charcount = 256`, `.data = fontdata_10x18.data`, and `.pref` of `5` on SPARC or `-1` elsewhere.

## Control Flow
There is no executable control flow. When `CONFIG_FONT_10x18` is selected, kbuild links this object, and the font library can discover/use `font_10x18` through compiled-in font descriptors.

## State and Persistence
All state is read-only compiled data in the kernel image or module object. No allocation, mutation, locking, or persistence beyond the selected kernel build exists.

## Dependencies and Integration Points
Depends on `font.h`, `struct font_desc` from `linux/font.h`, the `FONT10x18_IDX` index, Kconfig symbol `FONT_10x18`, and Makefile object selection. Consumers are framebuffer/DRM panic console font paths that render fixed-width bitmap glyphs.

## Risks
Data-size consistency is the main risk: 256 glyphs * 18 rows * 2 bytes = 9216 bytes, matching `FONTDATAMAX`. Any glyph-data truncation, row-count drift, or width/height mismatch would corrupt rendering. The SPARC preference affects default font selection. Because most of the file is literal bitmap data, accidental edits are hard to review visually.

## Test Signals
Build with `CONFIG_FONT_10x18`, verify `font_10x18` is linked and selectable, render representative ASCII/control/high-half glyphs on framebuffer or DRM panic paths, and check that glyph stride matches width/height. Static checks should confirm data length equals `FONTDATAMAX`.
