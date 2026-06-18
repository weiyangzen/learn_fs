# sources/distributed-fs/ceph-client/lib/fonts/font_6x11.c

## Purpose
Defines the built-in 6x11 ProFont/Mac-style bitmap console font. It supplies a 256-character fixed-size glyph table and exports it as `font_vga_6x11`, giving the font subsystem a compact console font whose high-half glyphs are intended for Macintosh-style usage.

## Important APIs, Types, And Functions
`FONTDATAMAX` is `(11*256)`, or `2816` bytes. `fontdata_6x11` is a `static const struct font_data` with the standard four-word `extra` prefix and an 11-byte-per-character glyph array. The exported descriptor is `font_vga_6x11`, with `.idx = VGA6x11_IDX`, `.name = "ProFont6x11"`, `.width = 6`, `.height = 11`, `.charcount = 256`, `.data = fontdata_6x11.data`, and `.pref = -2000`. The negative preference is an intentional selection hint: comments state the font should be avoided when possible unless on Mac.

## Control Flow
This file has no executable control flow beyond static initialization. Build inclusion is controlled by `CONFIG_FONT_6x11` in `lib/fonts/Makefile`. Runtime registration happens in `lib/fonts/fonts.c`, where `&font_vga_6x11` is included in the `fonts[]` array under the same Kconfig symbol. `find_font("ProFont6x11")` can return this exact descriptor. `get_default_font()` starts from the descriptor preference, applies architecture-specific m68k Mac preference logic that can raise `VGA6x11_IDX`, then filters by supported dimensions and screen geometry.

## State And Persistence
The glyph data and descriptor are immutable `const` data compiled into the kernel image. No dynamic memory, durable storage, runtime counters, or device-owned state are introduced. The only persistent behavioral effect is the descriptor's presence in the built-in font table when the font is selected by configuration.

## Dependencies And Integration Points
The source depends on local `font.h` for `struct font_data` and `VGA6x11_IDX`, and on `include/linux/font.h` for the public `font_desc` ABI and `extern const struct font_desc font_vga_6x11`. `lib/fonts/Kconfig` gates the font behind framebuffer console, STI console, or DRM panic support and defaults it on for non-SPARC Mac builds when the manual font menu is not used. It integrates with `fonts.c` default selection, `find_font`, framebuffer console drawing, DRM panic/log drawing, and any code that constrains supported font widths or heights through `get_default_font()`.

## Risks And Edge Cases
The table must remain exactly 256 glyphs with 11 row bytes each. Because `.pref` is `-2000`, changing preference or `.idx` can alter default console font selection on small displays or Mac systems. The 6-pixel logical width is packed into a byte row; consumers must use `.width`, not assume all eight bits are visible. This file contains generated bitmap comments with mixed visual conventions, so hand-edited comments are not reliable validation of the data itself. Name compatibility matters because callers must use `"ProFont6x11"` rather than a generic `"6x11"` string.

## Test Signals
Build with `CONFIG_FONT_6x11=y` should produce `font_6x11.o` and satisfy the public `font_vga_6x11` declaration. Static checks should verify 2816 initializer bytes, glyph comments numbered 0 through 255, and eleven data rows per glyph; this source was checked against those invariants. Runtime checks include `find_font("ProFont6x11")`, default-font behavior on m68k Mac-style configurations where `VGA6x11_IDX` receives a preference boost, and rendering paths that show no row skew or missing high-half glyphs.
