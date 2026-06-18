# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 24892-32217

## Scope

This chunk is part of illumos `kiconv_euctw_utf8.h`, a kernel-only static conversion-table header for EUC-TW/CNS 11643 to UTF-8 conversion. The source tree `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`.

The line range contains no executable functions. It covers:

- The tail of `kiconv_cns4_utf8[]`, from CNS plane 4 key `0xD4F9` through the end of the table at `0xEEDC`.
- The start and middle of `kiconv_cns5_utf8[]`, including the replacement/sentinel row `0x0000 -> EF BF BD`, then CNS plane 5 keys from `0xA1A1` through `0xD5B4`.
- One table boundary: `kiconv_cns4_utf8[]` closes at line 27306, and `kiconv_cns5_utf8[]` starts at line 27309.

Within this exact range there are 7,322 mapping rows: 2,414 rows from plane 4 and 4,908 rows from plane 5. Of those rows, 5,837 encode four-byte UTF-8 sequences beginning with `0xF0`, and 1,485 encode shorter UTF-8 sequences stored in the same four-byte array field.

## APIs and Data Exposed

- `kiconv_cns4_utf8[]` and `kiconv_cns5_utf8[]` are `static kiconv_table_array_t` arrays, so they have translation-unit-local linkage in whichever kernel source includes this header.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- Each row maps a 16-bit CNS code key, written as a `uint32_t`, to up to four UTF-8 bytes.
- The plane 5 table starts with `0x0000, { 0xEF, 0xBF, 0xBD }`, matching the file's convention for a replacement-character row.
- The file-level maximums visible outside this chunk declare `KICONV_CNS4_UTF8_MAX` as 7,287 and `KICONV_CNS5_UTF8_MAX` as 8,602; the full arrays match those counts.

There are no callable APIs, macros, structs, or typedefs introduced inside this chunk.

## Control Flow

There is no control flow in the chunk itself. Conversion control flow is data-driven in consumers: a EUC-TW/CNS input key is expected to select the appropriate plane table, then locate the matching `key` row and copy the nonzero UTF-8 bytes from `u8`.

The only structural transition is the source-level array boundary:

1. Continue plane 4 mappings inherited from previous chunks.
2. Close `kiconv_cns4_utf8[]`.
3. Open `kiconv_cns5_utf8[]`.
4. Continue plane 5 mappings into the next chunk.

## State

The chunk contributes immutable static table data. It has no mutable state, locks, counters, allocation, initialization function, or teardown path.

Important state properties for consumers:

- Row order is ascending within each plane segment in this chunk.
- Plane 4 and plane 5 are separate lookup domains; the duplicate-looking CNS key space across arrays is intentional because the CNS plane number is external to the row key.
- UTF-8 byte arrays are fixed-width at four bytes. Three-byte mappings are represented by only three explicit initializer bytes; C zero-initialization fills the remaining byte.
- The sentinel/replacement row exists at the start of plane 5, not at the plane 4 continuation point in this chunk.

## Dependencies

This chunk depends on file-level context outside the range:

- `_SYS_KICONV_EUCTW_UTF8_H` include guard and `_KERNEL` guard wrap the whole table header.
- `kiconv_table_array_t` and `uchar_t` come from common kernel/iconv headers, especially `kiconv_cck_common.h`.
- The full header is listed for installation/build handling in `usr/src/uts/common/sys/Makefile`.
- Reverse-direction EUC-TW conversion data lives separately in `kiconv_utf8_euctw.h`.

No OS/VFS/block-storage APIs are used directly here despite the subset scope; this is kernel character-conversion data.

## Risks and Edge Cases

- Table count coupling: consumers or generated lookup metadata must keep `KICONV_CNS4_UTF8_MAX` and `KICONV_CNS5_UTF8_MAX` synchronized with the complete array lengths. This chunk includes the plane 4 close and plane 5 open, making off-by-one mistakes at the boundary easy to introduce if regenerated manually.
- Plane-key ambiguity: the same 16-bit key values can appear in different CNS plane arrays. Consumers must include plane selection in lookup state and cannot treat keys as globally unique.
- Variable UTF-8 length in fixed storage: rows with three explicit bytes rely on zero-filled trailing bytes. Consumers must know how output length is determined and avoid copying all four bytes blindly for shorter mappings.
- Sparse CNS ranges: keys are monotonically increasing in this chunk but are not a dense arithmetic range; index arithmetic based only on key deltas would be unsafe without a table/search layer.
- Generated-data review risk: thousands of hex rows provide little local semantic signal. Corruption in an individual mapping would compile cleanly and likely surface only as conversion mismatch.
- Header inclusion cost: because the arrays are `static` in a header, every including translation unit gets private copies unless the build intentionally includes it in only one converter implementation.

## Cross-Chunk References

- Earlier chunks define the top of the file, include guards, `KICONV_CNS*_UTF8_MAX` constants, and complete plane 1 through plane 3 tables.
- The immediately preceding chunk starts `kiconv_cns4_utf8[]` at line 20018 and supplies its first 4,873 rows through key `0xD4F8`.
- This chunk completes `kiconv_cns4_utf8[]` with 2,414 additional rows, ending at key `0xEEDC`.
- This chunk starts `kiconv_cns5_utf8[]` at line 27309 and covers its first 4,908 rows through key `0xD5B4`.
- The next chunk must continue `kiconv_cns5_utf8[]` from the row after `0xD5B4`, finish plane 5, and then cover later plane tables depending on its assigned range.
- Later chunks contain `kiconv_cns6_utf8[]`, `kiconv_cns7_utf8[]`, `kiconv_cns15_utf8[]`, and the closing `_KERNEL`/include-guard directives.