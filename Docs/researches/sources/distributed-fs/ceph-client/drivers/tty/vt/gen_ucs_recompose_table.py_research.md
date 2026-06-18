# sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_recompose_table.py

## Purpose
`gen_ucs_recompose_table.py` generates `ucs_recompose_table.h`, a C include file consumed by `ucs.c` to map a base Unicode BMP character plus a combining mark to a precomposed BMP code point. The default mode intentionally emits a small common table for Latin, Greek, and Cyrillic pairs; `--full` emits every canonical two-code-point BMP decomposition discoverable through Python `unicodedata`.

## Important APIs, Types, And Functions
- `COMMON_RECOMPOSITION_PAIRS` is the curated default table, stored as `(base, combining, recomposed)` integer triples.
- `collect_all_recomposition_pairs()` scans code points `0..0xffff`, skips unassigned/control entries, rejects compatibility decompositions containing `<...>`, accepts simple two-part canonical decompositions, and returns sorted triples.
- `validate_common_pairs()` verifies the curated list is a subset of the generated full list with matching results.
- `generate_recomposition_table(use_full_list=False, out_file=DEFAULT_OUT_FILE)` selects the list, calculates min/max base and mark bounds, and writes the static C table plus `UCS_RECOMPOSE_*` boundary macros.
- CLI handling uses `argparse` for `--full` and `-o/--output`.

## Control Flow And State
On execution, arguments are parsed and `generate_recomposition_table()` is called. Both default and full modes first build the full table so the default table can be validated against the active Python Unicode database. The emitted table is sorted by base then mark, matching the binary-search comparator in `ucs.c`. Boundary macros allow `ucs_recompose()` to reject impossible searches before bsearch.

## State And Persistence Behavior
The script has no persistent runtime state beyond the output header. Reproducibility depends on Python's `unicodedata.unidata_version`, which is embedded in the generated header. The default curated table is stable in source; the `--full` table can change when the host Python Unicode database changes.

## Dependencies And Integration Points
It depends on the Python standard library: `unicodedata`, `argparse`, `textwrap`, and `pathlib`. The VT `Makefile` can regenerate `ucs_recompose_table.h` when `GENERATE_UCS_TABLES` is enabled, passing `--full` when `GENERATE_UCS_TABLES := 2`. `ucs.c` includes the generated file after defining `struct ucs_recomposition`.

## Risks And Edge Cases
The full scan is BMP-only because the generated C type uses `u16`; non-BMP recomposition pairs are omitted by design. The script imports `sys` but does not use it. An empty selected table would make `min()`/`max()` fail, though both current modes produce entries. Unicode-version drift can change `--full` output and validation expectations. The generated file is not guarded by include guards because it is intended as a private include inside `ucs.c`.

## Test Signals
Run `python3 gen_ucs_recompose_table.py -o /tmp/ucs_recompose_table.h` and check that it reports common mode, writes sorted triples, and emits min/max macros. Run `python3 gen_ucs_recompose_table.py --full -o /tmp/ucs_recompose_table_full.h` and confirm the full output compiles through `ucs.c`. A useful unit check is verifying that common pairs such as `A + U+0301 -> U+00C1`, Greek tonos pairs, and Cyrillic breve pairs are present and that default validation fails if a curated triple is corrupted.
