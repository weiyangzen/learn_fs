# sources/distributed-fs/ceph-client/drivers/tty/vt/ucs.c

## Purpose
`ucs.c` provides compact Unicode helper lookups for the virtual terminal. It classifies zero-width and double-width code points using generated interval tables, recomposes a base code point plus combining mark using a generated recomposition table, and returns fallback display substitutions for characters missing from the current console font.

## Important APIs, Types, And Functions
- `struct ucs_interval16` and `struct ucs_interval32` define generated width intervals included from `ucs_width_table.h`.
- `ucs_is_zero_width(u32 cp)` and `ucs_is_double_width(u32 cp)` dispatch BMP and non-BMP lookups through binary search.
- `struct ucs_recomposition` and `ucs_recompose(u32 base, u32 mark)` use `ucs_recompose_table.h` plus generated min/max macros.
- `struct ucs_page_desc`, `struct ucs_page_entry`, and `ucs_get_fallback(u32 cp)` implement a two-level BMP fallback table from `ucs_fallback_table.h`.
- Local comparators support `__inline_bsearch()` for interval, recomposition, page, and page-entry lookup.

## Control Flow And State
Width classification first rejects code points outside the first/last interval in the relevant generated array, then binary-searches for a containing interval. Recomposition rejects base/mark values outside generated boundary macros before bsearching the sorted pair table. Fallback lookup rejects non-BMP, handles fullwidth ASCII `U+FF01..U+FF5E` algorithmically, finds a page descriptor by high byte, and then finds an offset or range marker within that page.

## State And Persistence Behavior
The file has no mutable runtime state. All data is static generated tables compiled into the kernel object. Behavior changes only when the generated headers or Python Unicode-generation inputs change, or when `CONFIG_CONSOLE_TRANSLATIONS` controls whether these helpers are declared as real functions versus stubs in `consolemap.h`.

## Dependencies And Integration Points
It depends on `linux/bsearch.h`, `linux/array_size.h`, `linux/minmax.h`, and `linux/consolemap.h`. `vt.c` uses the width helpers in `vc_process_ucs()` for cursor advancement and zero-width behavior, uses `ucs_recompose()` for combining marks, and uses `ucs_get_fallback()` in `vc_get_glyph()` when font glyph lookup fails. The generated headers are produced by scripts in the same directory and wired by the VT `Makefile`.

## Risks And Edge Cases
`cp_in_range16()` and `cp_in_range32()` index `ranges[0]` and `ranges[size - 1]`, so generated arrays must never be empty. `ucs_recompose()` stores 32-bit inputs into 16-bit search keys after boundary checks; correctness depends on BMP-only generated bounds. Fallbacks are BMP-only and intentionally approximate display, not semantic equivalence. Range-marker entries in the fallback table require a following entry; malformed generated data could make lookup read the wrong fallback.

## Test Signals
Unit-style checks should cover BMP and non-BMP width ranges, boundary values before the first and after the last interval, known combining marks, CJK double-width characters, emoji width overrides, common recompositions, fullwidth ASCII fallback, table range-marker fallback, and no-fallback returns. Integration signals include proper cursor movement and `/dev/vcsu*` Unicode retrieval for double-width, zero-width, and fallback-rendered characters.
