# sources/distributed-fs/ceph-client/lib/fonts/font_ter10x18.c

## Purpose
`font_ter10x18.c` provides the built-in Terminus 10x18 console bitmap font. It embeds a complete 256-glyph bitmap table and exports a `struct font_desc` named `font_ter_10x18` so the common kernel font subsystem can make the font available as `TER10x18`. The font is intended as a readable high-resolution fixed-width console font between normal 8x16 fonts and larger Terminus sizes.

## Important APIs, types, and functions
The file has no executable APIs or functions. Its important exported object is `font_ter_10x18`, a `const struct font_desc` with `idx = TER10x18_IDX`, `name = "TER10x18"`, `width = 10`, `height = 18`, `charcount = 256`, and `data = fontdata_ter10x18.data`. The backing storage is `static const struct font_data fontdata_ter10x18`, with an `extra` header `{ 0, 0, FONTDATAMAX, 0 }` and a flexible byte array. `FONTDATAMAX` is 9216, matching `256 * 18 * 2` bytes because each 10-pixel row occupies two bytes.

## Control flow
There is no runtime control flow in this source file. At build time, `lib/fonts/Makefile` compiles it when `CONFIG_FONT_TER10x18` is selected. At runtime, `lib/fonts/fonts.c` conditionally adds `&font_ter_10x18` to the global built-in `fonts[]` table. Lookup and selection are handled externally: `find_font("TER10x18")` performs a name match, and `get_default_font()` scores the descriptor using preference, display resolution, and optional supported width and height bitmaps.

## State and persistence
All state is read-only kernel image data. The descriptor points into the static bitmap object and has no lifecycle beyond normal kernel image lifetime. There is no dynamic allocation, mutable cache, I/O persistence, or teardown path. The only conditional state is `pref`: `5` on `__sparc__` and `-1` elsewhere. That makes TER10x18 selectable on SPARC but gives SUN8x16 a stronger default preference when both are present.

## Dependencies and integration points
The file includes `<linux/module.h>` and local `font.h`; the latter supplies `struct font_data` and the `TER10x18_IDX` index. The descriptor is declared for other code in `include/linux/font.h`. Kconfig exposes this font as `FONT_TER10x18`, depending on framebuffer console or DRM panic support and allowing SPARC builds. The Makefile maps the config option to `font_ter10x18.o`. Runtime integration is through `fonts.c`, framebuffer console rendering, DRM panic/log text rendering, and any caller that chooses a font by name or default scoring.

## Risks and test signals
The primary risks are descriptor/table consistency bugs. A 10-pixel-wide glyph row must consume two bytes, so every glyph must be 36 bytes and the whole table must remain 9216 bytes. If `width`, `height`, `charcount`, or `FONTDATAMAX` drift from the data layout, glyph address calculations will render corrupted characters or read the wrong bytes. If the name or index changes, explicit lookup and table ordering behavior can regress. Because this larger font is not supported by all drivers, callers must honor font width and height capability checks before selecting it.

Useful test signals are successful builds with `CONFIG_FONT_TER10x18=y`, `find_font("TER10x18")` returning 10x18 dimensions with 256 characters, `get_default_font()` selecting or rejecting it according to supported font bitmaps, DRM panic and framebuffer console rendering without row alignment artifacts, and static verification that the data length remains `256 * 18 * 2`.
