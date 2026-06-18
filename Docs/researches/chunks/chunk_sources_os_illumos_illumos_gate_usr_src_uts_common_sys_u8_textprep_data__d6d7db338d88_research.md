# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 13204-19890

## Scope

This report covers lines 13204-19890 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h` for `learn_fs` subset A. The file is generated Unicode text-preparation data. This chunk begins in the middle of `u8_decomp_b4_tbl[0][27]`, covers the remainder of the Unicode 3.2.0 decomposition b4 table from table 28 through table 117, crosses into the Unicode 5.0.0 half at line 16361, and ends in the middle of `u8_decomp_b4_tbl[1][100]`.

The chunk contains no executable functions or preprocessor declarations; its semantics come from:

`static const uchar_t u8_decomp_b4_tbl[2][118][257]`.

## Public Surface And APIs

No new public API is declared here. The data supports `u8_validate()`, `u8_strcmp()`, and `u8_textprep_str()` from `u8_textprep.h`.

Relevant flags include `U8_STRCMP_NFD`, `U8_STRCMP_NFC`, `U8_STRCMP_NFKD`, `U8_STRCMP_NFKC`, and `U8_TEXTPREP_*` aliases. `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST` select the first table dimension.

Visible downstream users include ZFS ZAP name normalization, ZFS vnode name validation/comparison, pcfs long-name case folding, and SMB string comparison/validation paths.

## Data Layout

This is the 8-bit decomposition fourth-level offset table. Each b4 row has 257 entries because lookup reads `entry[byte4]` and `entry[byte4 + 1]` as a half-open range into `u8_decomp_final_tbl`.

Within this range:

- Lines 13204-13209 finish Unicode 3.2.0 fourth byte table 27.
- Lines 13210-16359 cover complete Unicode 3.2.0 tables 28-117.
- Lines 16360-16361 close version group 0 and open version group 1.
- Lines 16362-19861 cover complete Unicode 5.0.0 tables 0-99.
- Lines 19862-19890 start Unicode 5.0.0 table 100.

Values are monotonically nondecreasing offsets within each row. Repeated values represent empty decomposition ranges.

## Control Flow

There is no local control flow. Runtime lookup is table-driven:

1. Textprep code selects b1/b2/b3 tables from UTF-8 bytes.
2. `u8_decomp_b3_tbl` selects a b4 table id.
3. This table supplies `start_index` and `end_index`.
4. Non-empty ranges index bytes in `u8_decomp_final_tbl`.
5. Other tables handle 16-bit offsets, composition, validation, and case mapping.

The data is immutable and has no locks, allocation, mutation, or error handling.

## State, Dependencies, Risks

State is static read-only kernel data. Correctness depends on cross-table alignment among `u8_common_b1_tbl`, `u8_decomp_b2_tbl`, `u8_decomp_b3_tbl`, `u8_decomp_b4_tbl`, `u8_decomp_b4_16bit_tbl`, and `u8_decomp_final_tbl`.

Key risks:

- A shifted or corrupted initializer can silently alter filesystem name normalization.
- Both chunk endpoints split initializer rows, so this chunk is not standalone C.
- The 8-bit offset representation requires values to remain <= 255; larger rows must use `u8_decomp_b4_16bit_tbl`.
- Version dimensions must remain aligned with `U8_UNICODE_320 == 0` and `U8_UNICODE_500 == 1`.

## Cross-Chunk References

Earlier chunks cover the header, type definitions, common/decomposition b1-b3 tables, and the start of `u8_decomp_b4_tbl` through table 27. Later chunks must cover the rest of table 100, tables 101-117, `u8_decomp_b4_16bit_tbl`, `u8_decomp_final_tbl`, and later case-conversion tables.