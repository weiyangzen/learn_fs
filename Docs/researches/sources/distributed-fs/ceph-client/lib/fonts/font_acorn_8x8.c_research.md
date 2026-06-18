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
