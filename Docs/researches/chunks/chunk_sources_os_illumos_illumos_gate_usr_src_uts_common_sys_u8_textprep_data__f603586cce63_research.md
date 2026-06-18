# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 25441-31356

## Scope

This report covers lines 25441-31356 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h` for `learn_fs` subset A. The file is generated Unicode text-preparation data used by illumos UTF-8 normalization and case-mapping routines. The exact requested range was read completely.

This chunk is not syntactically standalone C. It starts in the middle of `u8_decomp_final_tbl[1]`, crosses complete case-mapping selector tables, and ends in the middle of `u8_tolower_final_tbl[1]`.

## Public Surface And APIs

No public API is declared here. The chunk provides static read-only data behind the public interfaces declared in `u8_textprep.h`:

- `u8_validate(char *, size_t, char **, int, int *)`
- `u8_strcmp(const char *, const char *, size_t, int, size_t, int *)`
- `u8_textprep_str(char *, size_t *, char *, size_t *, int, size_t, int *)`

The visible API selectors relevant to this chunk are `U8_TEXTPREP_TOLOWER`, `U8_TEXTPREP_NFD`, `U8_TEXTPREP_NFC`, `U8_TEXTPREP_NFKD`, `U8_TEXTPREP_NFKC`, and the Unicode-version selectors `U8_UNICODE_320 == 0`, `U8_UNICODE_500 == 1`, and `U8_UNICODE_LATEST == U8_UNICODE_500`.

Visible filesystem consumers in subset A include ZFS ZAP name normalization through `zap_normalize()` in `zap_micro.c` and pcfs long filename case folding in `pc_vnops.c`. Those callers invoke `u8_textprep_str()` and do not address this header's tables directly.

## Data Layout

The chunk covers these enclosing declarations:

- Lines 25441-27451: continuation and close of `static const uchar_t u8_decomp_final_tbl[2][19370]`, specifically the Unicode 5.0.0 final decomposition payload.
- Lines 27453-27597: complete `static const uchar_t u8_case_common_b2_tbl[2][2][256]`.
- Lines 27599-28264: complete `static const u8_displacement_t u8_tolower_b3_tbl[2][5][256]`.
- Lines 28266-30791: complete `static const uchar_t u8_tolower_b4_tbl[2][36][257]`.
- Lines 30793-31356: start and most of `static const uchar_t u8_tolower_final_tbl[2][2299]`, covering all of version 0 and most of version 1 before the array closes just after this chunk.

The final-table bytes are UTF-8 replacement payloads. `0xF6` appears as an in-band separator between mapped UTF-8 characters in final tables. The file-level comments define `0xF7` as `U8_TBL_ELEMENT_FILLER`, but this chunk's final payloads mainly use raw UTF-8 bytes plus `0xF6` separators.

The `u8_case_common_b2_tbl` table is a second-byte selector shared by lower- and upper-case conversion. It maps UTF-8 byte 2 to a compact b3-table id or `N_` (`0xff`) for no case mapping.

The `u8_tolower_b3_tbl` entries are `u8_displacement_t { tbl_id, base }` pairs. `tbl_id == N_` means no lower-case mapping for that third-byte position. Otherwise the id selects a row in `u8_tolower_b4_tbl`, while `base` participates in computing the final-table range.

The `u8_tolower_b4_tbl` rows each have 257 entries so lookup can read both `[byte4]` and `[byte4 + 1]`. Adjacent offset values define a half-open slice into `u8_tolower_final_tbl[version]`; repeated adjacent offsets mean no payload for that byte value.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven:

1. A caller asks `u8_textprep_str()` or `u8_strcmp()` for normalization, case folding, or comparison.
2. For decomposition, earlier b1/b2/b3/b4 tables select a byte range in `u8_decomp_final_tbl`; this chunk supplies the latter part of the Unicode 5.0.0 payload.
3. For lowercase mapping, `u8_common_b1_tbl` and `u8_case_common_b2_tbl` select a lower-case b3 row.
4. `u8_tolower_b3_tbl` supplies a b4 table id and base for the third byte.
5. `u8_tolower_b4_tbl` supplies adjacent offsets for the fourth byte.
6. The implementation copies bytes from `u8_tolower_final_tbl[version][start..end)` into the output stream, interpreting final-table separators according to the generated table format.

The chunk has no locks, allocations, branches, or error handling. Errors surface in consumers only when the surrounding textprep code encounters invalid UTF-8, unsupported mappings, or insufficient output space.

## State And Dependencies

All state here is `static const` kernel data. Correctness depends on cross-table alignment:

- `u8_case_common_b2_tbl`, `u8_tolower_b3_tbl`, and `u8_tolower_b4_tbl` must agree on table ids for both Unicode versions.
- Each `u8_tolower_b4_tbl` row must have exactly 257 monotonic, in-range offsets so `[byte4 + 1]` is valid.
- Offsets produced by `u8_tolower_b4_tbl` must remain within `u8_tolower_final_tbl[2][2299]`.
- Decomposition offsets from earlier chunks must remain within `u8_decomp_final_tbl[2][19370]`.
- The first dimension must continue to match `U8_UNICODE_320` and `U8_UNICODE_500`.
- `N_` depends on the earlier macro `U8_TBL_ELEMENT_NOT_DEF == 0xff`, and b3 entries depend on the earlier `u8_displacement_t` typedef.

The data ultimately derives from Unicode data files noted in the header comments and accompanying Unicode third-party license files.

## Risks And Invariants

The primary risk is generated-data drift. A shifted byte in `u8_decomp_final_tbl` or `u8_tolower_final_tbl` would keep the C initializer valid while changing filesystem name normalization or case-insensitive matching behavior.

Boundary risk is high because the chunk starts and ends inside final payload arrays. Earlier chunks must provide the beginning of `u8_decomp_final_tbl[1]`; the next chunk must provide the tail and closing brace of `u8_tolower_final_tbl[1]` plus the following upper-case tables.

Offset-table invariants are critical. If a b4 row is not monotonic, if it lacks the 257th sentinel entry, or if an offset exceeds the final table length, lookup can produce wrong output or out-of-bounds reads in low-level textprep code.

Compatibility risk is filesystem-visible. ZFS and pcfs can use these mappings when comparing or folding names, so changing data generation can affect on-disk name lookup semantics even though this header has no executable code.

## Cross-Chunk References

Earlier chunks should cover the header comments, `u8_displacement_t`, `N_`, common b1 tables, decomposition selector tables, and the start of `u8_decomp_final_tbl`. This chunk closes decomposition final data and introduces lower-case mapping tables.

The following chunk must finish `u8_tolower_final_tbl[1]` and cover `u8_toupper_b3_tbl`, `u8_toupper_b4_tbl`, and `u8_toupper_final_tbl`. The final per-file report should merge this chunk with both adjacent chunks because the selector tables in this chunk are only meaningful when paired with the final-table bytes that begin before and continue after this range.