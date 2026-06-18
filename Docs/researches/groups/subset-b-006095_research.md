# Research: subset-b-006095

Grouped research report for the console font data files in `sources/distributed-fs/ceph-client/lib/fonts/`. Each section is source-tree aligned and is intended to be split into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_8x16.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_8x16.c

## Purpose

`font_8x16.c` provides the built-in VGA 8x16 bitmap console font. It is a generated static data file, marked as produced by `cpi2fnt`, and contributes one `const struct font_desc` named `font_vga_8x16` for the Linux console/font subsystem. The descriptor identifies the font as `VGA8x16`, with 8 pixel columns, 16 pixel rows, and 256 glyphs.

The file is data-heavy rather than algorithmic. Its primary job is to keep the descriptor metadata and the static glyph byte stream in lockstep so that consumers can calculate each glyph as `data + character * height` for an 8-pixel-wide font.

## Important APIs, Types, and Symbols

- `FONTDATAMAX` is set to `4096`, matching `256 * 16` bytes of glyph payload.
- `static const struct font_data fontdata_8x16` embeds four leading `extra` words `{ 0, 0, FONTDATAMAX, 0 }` followed by the glyph byte array.
- `const struct font_desc font_vga_8x16` is the public descriptor:
  - `.idx = VGA8x16_IDX`
  - `.name = "VGA8x16"`
  - `.width = 8`
  - `.height = 16`
  - `.charcount = 256`
  - `.data = fontdata_8x16.data`
  - `.pref = 0`
- `EXPORT_SYMBOL(font_vga_8x16)` exports this descriptor for module users that resolve the symbol directly.

The file includes `<linux/module.h>` for `EXPORT_SYMBOL()` and local `"font.h"` for `struct font_data`, `struct font_desc` via `<linux/font.h>`, and the `VGA8x16_IDX` index constant.

## Data Layout and Control Flow

There is no runtime control flow in this file. Initialization is entirely static:

1. The compiler emits `fontdata_8x16` into read-only data.
2. The `font_vga_8x16` descriptor points at `fontdata_8x16.data`, skipping the packed `extra` header.
3. When `CONFIG_FONT_8x16` includes this object, `fonts.c` conditionally adds `&font_vga_8x16` to its `fonts[]` table.
4. Runtime callers reach it through `find_font("VGA8x16")`, `get_default_font()`, or direct symbol linkage.

Each glyph is represented by 16 bytes. For an 8-wide font each row fits in one byte, with bits corresponding to left-to-right pixels. The table covers byte values 0 through 255 in order. The file starts with control-character glyphs, includes ordinary ASCII in the middle, and ends with high-half graphical and extended glyphs.

## State and Persistence Behavior

The font has no mutable state, allocation, locking, I/O, persistence, or teardown. Its data is immutable kernel image or module data. The only state-like behavior is selection metadata: `.pref = 0`, meaning default-font preference comes from the generic scoring in `fonts.c` rather than a special boost in this file.

The four `extra` words are part of the import/export-compatible `struct font_data` representation used by `fonts.c`; this file initializes them statically and never reads or mutates them.

## Dependencies and Integration Points

- Built only when `CONFIG_FONT_8x16` selects `font_8x16.o` in `lib/fonts/Makefile`.
- `CONFIG_FONT_AUTOSELECT` selects `FONT_8x16` if no other compiled-in font is selected, making this file a common fallback font.
- Registered in `fonts.c` under `#ifdef CONFIG_FONT_8x16`.
- Externally declared as `font_vga_8x16` in `include/linux/font.h`.
- Consumed by framebuffer console, panic/DRM log display, and other font users through the common font lookup APIs.

## Risks and Edge Cases

- The central invariant is `FONTDATAMAX == width-row-bytes * height * charcount`. Here that is `1 * 16 * 256 = 4096`; a stripped initializer count confirms 4096 glyph bytes.
- Descriptor drift is the main risk. Changing `.width`, `.height`, `.charcount`, or the byte table independently would cause glyph indexing errors or visual corruption.
- The raw source contains many `0x..` values in comments, so simple hex counting must strip comments to avoid false byte-count results.
- Only this file among the four includes and uses `EXPORT_SYMBOL`; removing `<linux/module.h>` or the export would affect direct module symbol users even though `fonts.c` can still reference the descriptor internally.
- Visual regressions are easy to introduce because the compiler will accept semantically wrong glyph bytes if the initializer size still matches.

## Test Signals

- Build with `CONFIG_FONT_SUPPORT=y` and `CONFIG_FONT_8x16=y`; verify `font_8x16.o` compiles and links.
- Assert or script-check the data initializer contains exactly 4096 glyph bytes after comment stripping.
- Exercise `find_font("VGA8x16")` and verify descriptor fields match 8x16, 256 glyphs, and a non-null data pointer.
- Use console/framebuffer smoke tests to render representative ranges: control graphics, ASCII letters/digits, box-drawing, and high-half glyphs.
- If direct symbol users matter, inspect exported symbols for `font_vga_8x16`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_8x16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_8x8.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_8x8.c

## Purpose

`font_8x8.c` provides the built-in VGA 8x8 bitmap console font. Like the 8x16 VGA file, it is generated by `cpi2fnt` and exposes one descriptor, `font_vga_8x8`, for the shared console font registry. The font is intended for higher text density on displays that can use 8-pixel-high glyphs.

The Kconfig help notes that this is the high-resolution VGA framebuffer text-mode font and also warns that the 8x16 font is usually more readable. That matches the descriptor: this file prioritizes compact 8x8 glyph geometry over readability.

## Important APIs, Types, and Symbols

- `FONTDATAMAX` is `2048`, matching `256 * 8` bytes.
- `static const struct font_data fontdata_8x8` contains the packed `font_data` header `{ 0, 0, FONTDATAMAX, 0 }` and the glyph byte stream.
- `const struct font_desc font_vga_8x8` is the exported-by-header descriptor:
  - `.idx = VGA8x8_IDX`
  - `.name = "VGA8x8"`
  - `.width = 8`
  - `.height = 8`
  - `.charcount = 256`
  - `.data = fontdata_8x8.data`
  - `.pref = 0`

The file includes only local `"font.h"` because it does not call `EXPORT_SYMBOL()`. It relies on build-time linkage and the `fonts.c` registry rather than declaring a symbol export locally.

## Data Layout and Control Flow

There is no executable logic. Static initialization is the complete behavior:

1. The `fontdata_8x8` object stores glyph rows in character-code order.
2. Each glyph has 8 rows and each row is one byte because the width is exactly 8 pixels.
3. `font_vga_8x8.data` points to the first glyph byte.
4. If `CONFIG_FONT_8x8` is enabled, `fonts.c` includes `&font_vga_8x8` in its `fonts[]` lookup table.

The table covers all 256 byte values, with comments labelling each glyph. The early rows define PC/VGA control-character glyphs, the middle region covers printable ASCII, and the end covers extended symbols such as mathematical marks and block graphics.

## State and Persistence Behavior

The file has no mutable runtime state. The data is read-only and is never imported, freed, or modified by this file. Persistence is simply the compiled-in or module-resident font table.

The `.pref = 0` setting means default selection is governed by `fonts.c` scoring. In `get_default_font()`, short fonts can receive a resolution-based boost when `yres < 400`, so this 8-pixel-high font may be selected on low vertical resolution displays when supported by the caller's width/height masks.

## Dependencies and Integration Points

- Built through `lib/fonts/Makefile` when `CONFIG_FONT_8x8` is enabled.
- Kconfig allows it for framebuffer console, STI console, or DRM panic users, with a default when fonts are not explicitly selected on non-SPARC builds.
- Registered in `fonts.c` under `#ifdef CONFIG_FONT_8x8`.
- Declared in `include/linux/font.h` as `extern const struct font_desc font_vga_8x8`.
- Used by `find_font("VGA8x8")`, default font selection, and console renderers that consume `struct font_desc`.

## Risks and Edge Cases

- The size invariant is `1 byte per row * 8 rows * 256 glyphs = 2048` bytes; a comment-stripped initializer count confirms 2048 glyph bytes.
- Descriptor/table mismatch would create incorrect glyph strides. For example, changing `.height` without regenerating exactly 8 bytes per glyph would desynchronize every character after the first mismatch.
- Because this file does not call `EXPORT_SYMBOL()`, direct loadable module users depend on whether the broader build exports or links the symbol elsewhere. In-tree registry use through `fonts.c` is the expected integration path.
- Rendering quality is inherently constrained by 8-pixel height; visual tests should distinguish expected compactness from corruption.
- Generated comments contain binary representations and character labels; these can mislead ad hoc byte-count tools unless comments are ignored.

## Test Signals

- Build with `CONFIG_FONT_SUPPORT=y` and `CONFIG_FONT_8x8=y`.
- Verify `find_font("VGA8x8")` returns an 8x8 descriptor with `charcount == 256`.
- Script-check that the glyph initializer has exactly 2048 bytes after stripping comments.
- Render smoke tests across ASCII, control graphics, high-half symbols, and edge glyphs 0 and 255.
- Test default-font selection on a low-height display mode with width/height masks that permit 8x8 fonts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_8x8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_acorn_8x8.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_acorn_8x8.c

## Purpose

`font_acorn_8x8.c` provides an Acorn-style 8x8 console font with PC graphics characters. It is much more compact in source formatting than the generated VGA files, but it serves the same font subsystem role: define a 256-glyph byte table and expose a `struct font_desc` named `font_acorn_8x8`.

The file supports Acorn/ARM-specific preference behavior. On `CONFIG_ARCH_ACORN`, its descriptor preference is raised so `get_default_font()` can prefer this font over otherwise similar candidates.

## Important APIs, Types, and Symbols

- `FONTDATAMAX` is `2048`, exactly `256 * 8` bytes.
- `static const struct font_data acorndata_8x8` stores the glyph payload after the standard four-word `font_data` header.
- `const struct font_desc font_acorn_8x8` describes the font:
  - `.idx = ACORN8x8_IDX`
  - `.name = "Acorn8x8"`
  - `.width = 8`
  - `.height = 8`
  - `.charcount = 256`
  - `.data = acorndata_8x8.data`
  - `.pref = 20` under `CONFIG_ARCH_ACORN`, otherwise `.pref = 0`

The file includes local `"font.h"` for the packed data wrapper, descriptor type, and `ACORN8x8_IDX`.

## Data Layout and Control Flow

The file has no functions and no runtime branches except compile-time selection of `.pref`.

The glyph table is ordered by byte value from `0x00` to `0xff`, with eight row bytes per glyph. The first region includes control glyphs and placeholders, printable ASCII starts at `0x20`, and the extended range includes accented glyphs, line/box-drawing characters, block fills, arrows, and placeholders. Several unused or unsupported code points are represented by repeated simple block-like patterns, which appears intentional for a small Acorn-like character set with PC graphics coverage.

Build/runtime flow:

1. Kconfig enables `CONFIG_FONT_ACORN_8x8`.
2. `Makefile` includes `font_acorn_8x8.o`.
3. `fonts.c` includes `&font_acorn_8x8` in the `fonts[]` array under the same config.
4. `find_font("Acorn8x8")` can return it by name, and `get_default_font()` considers it during scoring.

## State and Persistence Behavior

All state is immutable static data. There is no persistence beyond the compiled font payload and descriptor. The only conditional behavior is compile-time descriptor preference:

- Acorn builds set `.pref = 20`, nudging this font upward in default selection.
- Non-Acorn builds set `.pref = 0`, making it a normal selectable font if configured.

No glyph data is generated at runtime, imported, or cached by this file.

## Dependencies and Integration Points

- `CONFIG_FONT_ACORN_8x8` controls compilation through `lib/fonts/Makefile`.
- Kconfig defaults this font on non-SPARC ARM Acorn systems when explicit font selection is off.
- `CONFIG_ARCH_ACORN` controls the descriptor preference boost.
- `fonts.c` registers the descriptor under `#ifdef CONFIG_FONT_ACORN_8x8`.
- `include/linux/font.h` declares `font_acorn_8x8` for in-tree users.

## Risks and Edge Cases

- The data-size invariant is `1 * 8 * 256 = 2048` bytes; a comment-stripped scan confirms 2048 glyph bytes.
- The compile-time `.pref` branch is easy to lose in refactors; doing so would change default font selection specifically on Acorn builds.
- Many extended glyph slots are placeholders rather than fully distinct characters. That may be expected but can surprise tests that compare against VGA-like extended glyphs.
- There is no local `EXPORT_SYMBOL()`, so direct external module use is not signaled here; normal consumers should use the central font API.
- Any table reformatting should preserve byte order exactly, because glyph identity is positional rather than keyed by labels.

## Test Signals

- Build with `CONFIG_FONT_ACORN_8x8=y` and verify registration in `fonts.c`.
- Build or preprocess both with and without `CONFIG_ARCH_ACORN` and confirm `.pref` resolves to 20 or 0 respectively.
- Check `find_font("Acorn8x8")` descriptor fields: 8 width, 8 height, 256 glyphs, non-null data.
- Script-check exactly 2048 initializer bytes after comments are removed.
- Visual smoke tests should include ASCII, Acorn-specific printable shapes, box-drawing range around `0xb0`-`0xdf`, and placeholder-heavy high ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_acorn_8x8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_mini_4x6.c -->
# sources/distributed-fs/ceph-client/lib/fonts/font_mini_4x6.c

## Purpose

`font_mini_4x6.c` provides the built-in `MINI4x6` console font, a very small hand-composed 4x6 bitmap font. The file comments describe it as the "Minuscule" 4x6 font by Kenneth Albanowski, public domain, with binary data generated from annotated patterns by an embedded Perl stub.

This font trades detail for density. It is suitable for constrained displays or situations where fitting many characters matters more than conventional glyph quality.

## Important APIs, Types, and Symbols

- `FONTDATAMAX` is `1536`, matching `256 * 6` row bytes.
- `static const struct font_data fontdata_mini_4x6` stores the standard `font_data` header plus 1536 glyph bytes.
- `const struct font_desc font_mini_4x6` describes the font:
  - `.idx = MINI4x6_IDX`
  - `.name = "MINI4x6"`
  - `.width = 4`
  - `.height = 6`
  - `.charcount = 256`
  - `.data = fontdata_mini_4x6.data`
  - `.pref = 3`

The file includes only local `"font.h"`. It does not export the descriptor with `EXPORT_SYMBOL()`.

## Data Layout and Control Flow

The C file has no runtime functions. Its notable control-flow-like element is the commented Perl regeneration script:

1. Human-readable row comments use four-character `[* ]` patterns.
2. The Perl stub converts those patterns into byte values.
3. For each row, the generated byte repeats the 4 useful bits in both nibbles.
4. Runtime consumers still receive one byte per row, matching the generic font-data convention.

Each glyph has six bytes. Since the descriptor width is 4, only four pixels are semantically meaningful in each row, but the data byte duplicates the nibble so generic byte-oriented renderers have stable row storage. The table covers 256 character positions. Printable ASCII has hand-shaped miniature glyphs; many control or extended positions are simple repeated fallback patterns such as `0xee` rows with a blank final row. Character 254 has a small block-like glyph, while many high slots remain placeholders.

## State and Persistence Behavior

The font is immutable static data. There is no allocation, caching, lock, I/O, runtime generation, or persistence beyond the compiled object. The embedded Perl block is documentation and regeneration tooling only; it is inside a C comment and has no build-time effect unless a maintainer runs it manually as described in the file header.

The `.pref = 3` descriptor gives this font a small positive default-selection bias compared with zero-preference fonts, but `fonts.c` still applies display-size and supported-dimension scoring.

## Dependencies and Integration Points

- Controlled by `CONFIG_FONT_MINI_4x6`; Kconfig requires `!SPARC && FONTS`.
- `lib/fonts/Makefile` includes `font_mini_4x6.o` under `CONFIG_FONT_MINI_4x6`.
- `fonts.c` registers `&font_mini_4x6` under `#ifdef CONFIG_FONT_MINI_4x6`.
- `include/linux/font.h` declares `font_mini_4x6`.
- Generic font import/export/rotation helpers in `fonts.c` and `font_rotate.c` consume the descriptor's width, height, charcount, and data pointer.

## Risks and Edge Cases

- The invariant is `1 row byte * 6 rows * 256 glyphs = 1536` bytes; a comment-stripped initializer count confirms 1536 glyph bytes.
- The four-bit duplicated-nibble format is easy to misunderstand. A maintainer might try to pack two rows or two glyphs per byte because the font is 4 pixels wide, but generic consumers expect one byte per row.
- Regenerating with the Perl stub can alter many rows mechanically; review should compare rendered glyphs or normalized byte counts, not just compile success.
- Many non-printable and extended characters are placeholders. That is expected for this tiny font but can be mistaken for missing coverage.
- Since the file has no `EXPORT_SYMBOL()`, direct external module lookup is not declared here; normal usage should go through the font registry when enabled.

## Test Signals

- Build with `CONFIG_FONT_MINI_4x6=y` and confirm `font_mini_4x6.o` is included.
- Verify `find_font("MINI4x6")` returns width 4, height 6, charcount 256, `.pref = 3`.
- Script-check exactly 1536 glyph bytes after stripping comments.
- Render representative glyphs: digits `0`-`9`, uppercase/lowercase ASCII, punctuation, fallback high-half glyphs, and character 254.
- Test renderer paths that handle widths below 8 pixels, including rotation if `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/fonts/font_mini_4x6.c -->
