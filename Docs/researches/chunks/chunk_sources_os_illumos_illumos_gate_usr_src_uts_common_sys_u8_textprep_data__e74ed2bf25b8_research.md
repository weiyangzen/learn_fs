# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 6877-13203

## Scope

This chunk is a generated Unicode text-preparation data slice inside illumos `u8_textprep_data.h`. It contains no functions or public entry points; it is immutable table payload consumed by the UTF-8 textprep implementation described in the file header and implemented outside this header, primarily in `u8_textprep.c`.

The range starts in the middle of `u8_composition_b4_tbl[2][41][257]`, closes the byte-sized composition index table, includes the full 16-bit composition index table and full composition final-byte table, then begins decomposition lookup data through `u8_decomp_b4_tbl` table 27. The chunk ends before `u8_decomp_b4_tbl` table 27 is complete.

## APIs And Symbols

- `u8_composition_b4_tbl[2][41][257]`: tail of first Unicode-version subarray table 31 through table 40, then complete second Unicode-version subarray tables 0 through 40.
- `u8_composition_b4_16bit_tbl[2][5][257]`: fully defined here for composition final-table offsets that do not fit in `uchar_t`.
- `u8_composition_final_tbl[2][6623]`: fully defined here; packed UTF-8 bytes plus `FIL_` delimiters.
- `u8_decomp_b2_tbl[2][2][256]`: fully defined here; maps second byte to decomposition third-byte table ids or `N_`.
- `u8_decomp_b3_tbl[2][8][256]`: fully defined here as `u8_displacement_t { tbl_id, base }`.
- `u8_decomp_b4_tbl[2][118][257]`: starts here and continues after the chunk; this chunk ends mid-table 27.

## Control Flow And State

There is no executable control flow in this chunk. External consumers select Unicode version `[0]` or `[1]`, traverse b1/b2/b3/b4 tables, read adjacent b4 entries as `[start, end)` ranges, then decode bytes from the final table. High-bit b3 ids such as `0x8000` through `0x801D` route lookups to later 16-bit b4 tables.

All data is `static const`; there is no allocation, locking, mutation, reference counting, or runtime ownership.

## Dependencies

Depends on `uchar_t`, `uint16_t`, `u8_displacement_t`, `N_`, and `FIL_` from earlier in the header. It must stay synchronized with earlier composition b1/b2/b3 tables and later decomposition b4 16-bit/final tables. Runtime behavior is in `u8_textprep.c`.

## Risks And Invariants

The 257-entry b4-table width is critical because lookups read `index` and `index + 1`. Byte-sized b4 offsets must not exceed `uchar_t` capacity; larger offset ranges require the `0x8000` 16-bit-table convention. `N_` is valid only in index/displacement tables, while `FIL_` is an internal final-table delimiter, not string termination.

A single generated-data edit can silently alter Unicode normalization/composition behavior, so validation should come from regeneration and Unicode conformance tests rather than visual review.

## Cross-Chunk References

Earlier chunks define guards, sentinels, common b1 tables, combining-class data, and the start of composition tables. This chunk begins inside `u8_composition_b4_tbl` table 31 and ends inside `u8_decomp_b4_tbl` table 27. Later chunks continue decomposition b4 data and define `u8_decomp_b4_16bit_tbl`, `u8_decomp_final_tbl`, case conversion tables, and the header close.