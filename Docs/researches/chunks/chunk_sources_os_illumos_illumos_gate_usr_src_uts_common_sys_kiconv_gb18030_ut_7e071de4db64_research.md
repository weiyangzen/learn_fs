# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 1-8450

## Scope

This report covers lines 1-8450 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for GB18030/GBK to UTF-8 conversion. This chunk includes the license notices, include guard, C++ linkage wrapper, `_KERNEL` guard, both maximum-count macros, and the first 8,367 rows of the two-byte GBK/GB18030 mapping table. It ends inside `kiconv_gbk_utf8[]` at key `0xAD45`; it does not include the end of the two-byte table, the four-byte `kiconv_gbk4_utf8[]` table, or the closing preprocessor structure.

The slice is exactly 8,450 lines and 262,121 bytes. The whole file is 63,457 lines, so later chunks must account for most of the table data and all closing guards.

## Public Surface And APIs

This chunk exposes kernel-only static data and constants when `_KERNEL` is defined:

- `KICONV_GBK_UTF8_MAX (23941)`: declared maximum item count for the two-byte GBK/GB18030-to-UTF-8 table.
- `KICONV_GBK4_UTF8_MAX (39421)`: declared maximum item count for the four-byte GB18030-to-UTF-8 table, although the table itself starts later at line 24027.
- `static kiconv_table_array_t kiconv_gbk_utf8[] = { ... }`: begins the two-byte mapping table.

The table element type is defined in `kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`. This header does not declare callable functions.

## Data Layout Visible In This Chunk

`kiconv_gbk_utf8[]` starts at line 83. The first row is `0x0000 -> EF BF BD`, the UTF-8 replacement character `U+FFFD`.

Within lines 1-8450:

- Mapping rows counted: 8,367.
- First key: `0x0000`.
- Last key: `0xAD45`.
- Duplicate keys found: none.
- Nonascending keys found: none.
- Explicit UTF-8 byte initializer widths: 158 rows with two bytes, 8,209 rows with three bytes.
- Rows containing `0xEE` UTF-8 bytes: 1,109.

The visible key ranges are regular GBK-style two-byte ranges. `0x8140` through `0xACFE` are complete lead-byte blocks, and `0xAD40` through `0xAD45` are the first six rows of the next block. The chunk boundary is clean at line 8450; line 8451 continues with `0xAD46`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by illumos kernel iconv code that consumes these CCK conversion tables:

1. GB18030/GBK input validation is handled outside this header, using Simplified Chinese byte macros from `kiconv_sc.h`.
2. A valid input sequence is assembled into a numeric key.
3. Generic lookup code such as `kiconv_binsearch()` can search sorted conversion tables.
4. On match in `kiconv_gbk_utf8[]`, the `u8` byte array supplies the UTF-8 output bytes.
5. Error handling, replacement policy, ASCII passthrough, and buffer accounting are external.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled into translation units that include this header under `_KERNEL`.

Direct or required dependencies:

- `_KERNEL`
- `kiconv_table_array_t` from `uts/common/sys/kiconv_cck_common.h`
- `uchar_t` and `uint32_t`
- `kiconv_sc.h` for GBK/GB18030 byte validation and length macros
- `kiconv_utf8_gb18030.h` as the companion reverse-direction table
- `uts/common/sys/Makefile`, which exports this and related kiconv headers

The conversion registry in `uts/common/os/kiconv.c` includes `"gb18030"`, plus `"gbk"`, `"cp936"`, and `"936"` aliases for the Simplified Chinese conversion surface.

## Risks And Invariants

Important invariants:

- `kiconv_gbk_utf8[]` must remain sorted by ascending `key` for binary search.
- Full table length must remain exactly `KICONV_GBK_UTF8_MAX`.
- The later four-byte table must remain exactly `KICONV_GBK4_UTF8_MAX`.
- UTF-8 byte arrays must contain valid output sequences and compatible zero padding.

Risks:

- Generated-data drift can silently change conversion semantics.
- This chunk validates only 8,367 of 23,941 two-byte rows.
- The table is `static` in a header, so broad inclusion can duplicate data.
- 158 rows depend on zero-filled trailing bytes in `u8[4]`.
- Private-use mappings using `0xEE...` bytes may be mistaken for invalid data by naive validators.

## Cross-Chunk References

The next chunk should resume at line 8451 with `0xAD46`. Later chunks must verify:

- Remaining two-byte rows through `0xFEFE` at line 24024.
- `kiconv_gbk4_utf8[]` starts at line 24027.
- Four-byte table closes at line 63449.
- Final guards close `_KERNEL`, C++ linkage, and `_SYS_KICONV_GB18030_UTF8_H`.
- Whole-file row counts remain `gbk_entries=23941` and `gbk4_entries=39421`.