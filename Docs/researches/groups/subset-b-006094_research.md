# subset-b-006094 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x10.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_6x10.c

## Purpose
Defines the built-in 6x10 bitmap console font for the Ceph-client kernel source tree's `lib/fonts` subsystem. The file is entirely data-oriented: it provides a 256-character, fixed-width font table and publishes it through a `struct font_desc` named `font_6x10` so framebuffer console, DRM panic/log, and other font consumers can select and render the glyphs.

## Important APIs, Types, And Functions
The local `FONTDATAMAX` constant is `2560`, matching `256` glyphs times `10` byte rows per glyph. `fontdata_6x10` is a `static const struct font_data` containing the `extra[4]` metadata prefix followed by the glyph bytes. `font_6x10` is the externally visible descriptor declared in `include/linux/font.h`; it sets `.idx = FONT6x10_IDX`, `.name = "6x10"`, `.width = 6`, `.height = 10`, `.charcount = 256`, `.data = fontdata_6x10.data`, and `.pref = 0`. There are no functions or callbacks in this file.

## Control Flow
There is no runtime control flow inside this source file. At build time, `lib/fonts/Makefile` compiles `font_6x10.o` when `CONFIG_FONT_6x10` is enabled. At runtime, `lib/fonts/fonts.c` conditionally inserts `&font_6x10` into its `fonts[]` table. Consumers reach the descriptor through `find_font("6x10")` or through `get_default_font()`, then compute each glyph address as `font->data + character * font->height` because the 6-pixel width fits in one byte per row.

## State And Persistence
All state is immutable static kernel data. `fontdata_6x10` and `font_6x10` are `const`; rendering callers do not mutate the font. There is no filesystem persistence, allocation, reference counting, or device state in this file. Persistence is limited to the built-in object being present in the kernel image when selected by Kconfig.

## Dependencies And Integration Points
The file includes local `font.h`, which wraps `include/linux/font.h`, defines `struct font_data`, and provides `FONT6x10_IDX`. The descriptor is declared externally in `include/linux/font.h` and is registered by `lib/fonts/fonts.c` only under `CONFIG_FONT_6x10`. Kconfig describes it as a medium-size 6x10 font suitable for small embedded displays such as 320x240 framebuffer consoles. Downstream integrations include framebuffer console font rendering, DRM panic text rendering, DRM client log text, STI console paths when supported by the selected font set, and rotation/export helpers that rely on the `struct font_desc` dimensions and byte layout.

## Risks And Edge Cases
The critical invariant is that the byte table length equals `.height * .charcount` for a one-byte glyph pitch. A mismatch between `FONTDATAMAX`, the initializer length, and the descriptor height would make consumers read the wrong glyph rows or fail bounds checks in helpers such as `font_data_export()`. Width is six pixels but each row is stored in an `unsigned char`; renderers must honor `.width` and ignore unused low-order padding bits. Manual bitmap edits can silently damage glyph shapes or character ordering because glyphs are selected by byte offset rather than by named fields. The `.idx` value must stay synchronized with `font.h` and the `fonts.c` table expectations.

## Test Signals
Useful build signals are successful compilation with `CONFIG_FONT_SUPPORT=y` and `CONFIG_FONT_6x10=y`, plus absence of undefined references to `font_6x10`. Static validation should check 256 glyph comment blocks, exactly 2560 initializer bytes, and ten row bytes per glyph; this source was checked against those invariants. Runtime signals are successful `find_font("6x10")`, correct default-font selection when constraints allow 6x10, visible framebuffer/DRM text without shifted rows, and `font_data_export()` accepting `charcount * height` bytes without `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x11.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x8.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_6x8.c

## Purpose
Defines the built-in 6x8 OLED-oriented bitmap console font. The file contributes a compact 256-character glyph table and publishes it as `font_6x8`, letting the font subsystem render readable text on very small displays and low-height framebuffer or DRM panic outputs.

## Important APIs, Types, And Functions
`FONTDATAMAX` is `2048`, matching `256 * 8` bytes. `fontdata_6x8` is a `static const struct font_data` with the standard `extra[4]` prefix followed by eight row bytes for each character. The exported `font_6x8` descriptor uses `.idx = FONT6x8_IDX`, `.name = "6x8"`, `.width = 6`, `.height = 8`, `.charcount = 256`, `.data = fontdata_6x8.data`, and `.pref = 0`. No functions are defined.

## Control Flow
There is no local runtime branching. `CONFIG_FONT_6x8` causes `lib/fonts/Makefile` to include `font_6x8.o`; `fonts.c` then conditionally appends `&font_6x8` to the font registry. Consumers either look it up by name with `find_font("6x8")` or let `get_default_font()` score it. The generic default selector gives fonts with height at most eight a boost for screens below 400 pixels tall, which makes this font relevant for small displays.

## State And Persistence
All data is immutable and built in. The file does not allocate memory, record runtime choices, or persist state outside the compiled kernel object. The `font_desc` points directly at static glyph storage and remains valid for the lifetime of the kernel.

## Dependencies And Integration Points
This source includes local `font.h`, uses `FONT6x8_IDX`, and satisfies the public `font_6x8` declaration in `include/linux/font.h`. Kconfig describes it as an OLED 6x8 font gated by framebuffer console or DRM panic support. It integrates with framebuffer console, DRM panic, DRM client log, font rotation/export utilities, and any consumer that uses the generic `font_desc` data pointer and dimensions to draw glyphs.

## Risks And Edge Cases
The highest-risk invariant is the exact packed layout: 256 characters, eight bytes per character, one byte per row, logical width six. Any insertion or deletion in the table shifts every later character because lookup is offset-based. The small height means glyph edits can easily affect legibility or lose distinguishing rows for punctuation and high-half characters. Because unused bits exist in each row byte, visual comments showing six columns are helpful but the renderer still receives full bytes and must mask or clip by `.width`.

## Test Signals
Build coverage should include `CONFIG_FONT_SUPPORT=y` and `CONFIG_FONT_6x8=y`, with `font_6x8` resolving through the public header. Static checks should confirm 2048 initializer bytes, glyph comment coverage from 0 to 255, and eight rows per glyph; this source was checked against those invariants. Runtime signals are `find_font("6x8")`, default selection on low-resolution displays when supported by the target driver, successful `font_data_export()` sizing, and rendered text that does not bleed into unused byte columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_6x8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_7x14.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_7x14.c -->
