# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 13008-25996

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h` lines 13008-25996 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to confirm that the range is a middle slice of the same `kiconv_utf8_euctw[]` initializer opened earlier and continued after line 25996.

The chunk is static kernel character-conversion data, not executable conversion logic. It contains no declarations, preprocessor directives, comments, or array boundaries.

## APIs And Exported Data

This chunk contributes 12,989 rows to `static kiconv_table_t kiconv_utf8_euctw[]`.

`kiconv_table_t` is the common CCK conversion table type declared in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`. Here, `key` is a packed UTF-8 byte sequence encoded as a hexadecimal integer, and `value` is a packed CNS 11643/EUC-TW destination code.

No new API, macro, type, or symbol is introduced in this chunk. Runtime users depend on the table-level API and constants declared outside this line range, especially `KICONV_UTF8_EUCTW_MAX`, `kiconv_utf8_euctw[]`, and the shared `kiconv_binsearch()` contract.

## Data Shape

The first and last rows in this chunk are:

- line 13008: `0xE6AA86 -> 0x3D5A1`
- line 25996: `0xF0A09B8D -> 0x6A3E6`

Decoded as Unicode scalar values, this chunk spans from `U+6A86` through `U+206CD`. It covers later BMP CJK Unified Ideographs, then enters supplementary-plane CJK data encoded as four-byte UTF-8.

Observed properties:

- 12,989 table rows.
- 11,811 rows use three-byte UTF-8 keys.
- 1,178 rows use four-byte UTF-8 keys.
- No non-table lines.
- No duplicate UTF-8 keys within this chunk.
- Strictly ascending packed UTF-8 key order within this chunk.
- Destination range: `0x1A1A2` through `0xFECC9`.

## Control Flow

There is no direct control flow in this chunk: no functions, branches, loops, locking, allocation, or error handling.

Runtime behavior is indirect: UTF-8-to-EUC-TW conversion parses a UTF-8 sequence, packs it into a `uint32_t` key, searches `kiconv_utf8_euctw[]` through shared lookup logic such as `kiconv_binsearch()`, and emits the packed CNS/EUC-TW value on success. Misses and invalid input are handled by common kiconv wrapper code outside this header.

Because lookup is binary-search based, sorted key order is a functional invariant. This chunk preserves that invariant internally and across visible boundaries: line 13007 is `0xE6AA85`, this chunk starts at `0xE6AA86`, this chunk ends at `0xF0A09B8D`, and line 25997 continues with `0xF0A09B8E`.

## State And Dependencies

All state here is compiled static data. The parent array is declared `static` in a kernel header, so including translation units receive internal-linkage copies rather than referencing one external object.

Dependencies include `_KERNEL`, `kiconv_table_t`, `uint32_t`, common UTF-8-to-CCK wrappers, `kiconv_binsearch()`, EUC-TW/CNS constants in `sys/kiconv_tc.h`, `"euctw"` registration in `uts/common/os/kiconv.c`, and header listing in `uts/common/sys/Makefile`.

## Risks And Edge Cases

- Incorrect literals silently corrupt character conversion output.
- Binary search depends on strict key ordering at both chunk boundaries.
- `KICONV_UTF8_EUCTW_MAX` is a file-level count contract; this chunk contributes 12,989 entries but cannot validate the full table alone.
- The parent table is mutable (`static kiconv_table_t`, not `const`) despite being lookup data.
- File-level comments state that some characters are missing and CNS11643-92 is unsupported.
- Packed destination values require external EUC-TW/CNS interpretation logic.
- Four-byte UTF-8 keys appear in this chunk, so consumers must not assume all mappings are three-byte BMP UTF-8.

## Cross-Chunk References

This is chunk 2 for `kiconv_utf8_euctw.h`. It continues the array opened in the previous chunk:

- Previous visible row: line 13007, `0xE6AA85 -> 0x2DDB4`.
- This chunk starts: line 13008, `0xE6AA86 -> 0x3D5A1`.

The next chunk must continue the same initializer:

- This chunk ends: line 25996, `0xF0A09B8D -> 0x6A3E6`.
- Next visible row: line 25997, `0xF0A09B8E -> 0x4A3C1`.

Later chunks must verify final array closure, guard closure, and complete entry count against `KICONV_UTF8_EUCTW_MAX`.