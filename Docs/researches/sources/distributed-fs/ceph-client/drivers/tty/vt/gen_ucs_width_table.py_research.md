# sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_width_table.py

## Purpose
`gen_ucs_width_table.py` generates `ucs_width_table.h`, the interval tables used by `ucs.c` and then `vt.c` to classify Unicode code points as zero-width or double-width for Linux console rendering. It combines Unicode category/East Asian Width data with terminal-oriented overrides for emoji, variation selectors, tag characters, and regional indicators.

## Important APIs, Types, And Functions
- `KNOWN_ZERO_WIDTH`, `EMOJI_ZERO_WIDTH`, `REGIONAL_INDICATORS`, and `EMOJI_RANGES` define policy overrides before and after Unicode-property classification.
- `create_width_tables()` builds `width_map` for all Unicode scalar positions through `0x10ffff`, assigns width 0 to marks and format controls, width 2 to EAW `F`/`W`, width 1 to narrow/neutral/ambiguous classes, then forces emoji ranges to width 2 unless already zero-width.
- The nested `ranges_optimize()` compacts individual code points into sorted inclusive ranges.
- `write_tables()` splits ranges into BMP `struct ucs_interval16` and non-BMP `struct ucs_interval32` arrays and writes C comments from `unicodedata.name()`.
- The CLI accepts `-o/--output`, writes the table, and prints range/count/version summary.

## Control Flow And State
Generation first applies zero-width emoji modifiers and single-width regional indicators, then walks Unicode in `0x1000`-sized blocks and assigns widths to unprocessed code points. Emoji ranges are applied last so many neutral pictographs become double-width while zero-width modifiers remain zero-width. The output order is zero-width BMP, zero-width non-BMP, double-width BMP, and double-width non-BMP, matching the symbols expected by `ucs.c`.

## State And Persistence Behavior
The script writes a generated header and embeds the active Python Unicode database version. It keeps no persistent state. The generated table is deterministic for a fixed script and Python Unicode version, but it can change when `unicodedata` changes or when terminal policy overrides are edited.

## Dependencies And Integration Points
It depends on Python `unicodedata`, `argparse`, and `pathlib`. The VT `Makefile` can use it to generate `ucs_width_table.h` when `GENERATE_UCS_TABLES` is set; otherwise shipped generated headers are used. `ucs.c` includes the generated arrays after defining `struct ucs_interval16` and `struct ucs_interval32`; `vt.c` ultimately consumes the lookups via `ucs_is_zero_width()` and `ucs_is_double_width()`.

## Risks And Edge Cases
The policy deliberately treats ambiguous-width characters as single-width, which is important for Linux console compatibility but differs from some CJK terminal settings. Regional indicators are width 1 individually so flag pairs combine to width 2 conceptually, but the VT renderer does not implement full grapheme clustering. Emoji modifiers such as gender signs are forced zero-width, which may hide standalone characters. The script catches broad exceptions in comment generation, so invalid-name cases degrade to code-point comments. It also imports `sys` but does not use it.

## Test Signals
Generate into a temporary path and compile `ucs.c` against it. Inspect that combining marks and format controls land in zero-width ranges, CJK ideographs and emoji pictographs land in double-width ranges, regional indicators do not become double-width, and variation selectors stay zero-width. Runtime signals include Linux console rendering of combining marks, VS16, emoji, and CJK characters with expected cursor advancement.
