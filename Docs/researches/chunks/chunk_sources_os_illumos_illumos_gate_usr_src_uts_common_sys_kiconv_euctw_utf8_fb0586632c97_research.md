# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 46469-53594

## Scope

This chunk is part of illumos `kiconv_euctw_utf8.h`, a kernel-only static conversion-table header for EUC-TW/CNS 11643 to UTF-8 conversion. The source tree `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`.

The line range contains no executable functions. It covers:

- The tail of `kiconv_cns7_utf8[]`, from CNS plane 7 key `0xCDBD` through the end of the table at `0xE6D5`.
- The start and middle of `kiconv_cns15_utf8[]`, including the replacement/sentinel row `0x0000 -> EF BF BD`, then CNS plane 15 keys from `0xA1A1` through `0xD6E5`.
- One table boundary: `kiconv_cns7_utf8[]` closes at line 48844, and `kiconv_cns15_utf8[]` starts at line 48847.

Within this exact range there are 7,122 mapping rows: 2,375 rows from plane 7 and 4,747 rows from plane 15. Of those rows, 6,874 encode four-byte UTF-8 sequences beginning with `0xF0`, and 248 encode three-byte UTF-8 sequences stored in the same fixed four-byte array field.

## APIs and Data Exposed

- `kiconv_cns7_utf8[]` and `kiconv_cns15_utf8[]` are `static kiconv_table_array_t` arrays, so they have translation-unit-local linkage in whichever kernel source includes this header.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- Each row maps a CNS row/cell-style key, written as a `uint32_t`, to up to four UTF-8 bytes.
- The plane 15 table starts with `0x0000, { 0xEF, 0xBF, 0xBD }`, matching the file's replacement-character convention.
- The file-level maximums outside this chunk declare `KICONV_CNS7_UTF8_MAX` as 6,538 and `KICONV_CNS15_UTF8_MAX` as 6,722; full-array counts match those constants.

There are no callable APIs, macros, structs, typedefs, or include directives introduced inside this chunk.

## Control Flow

There is no control flow in the chunk itself. Runtime conversion is data-driven: EUC-TW parsing identifies the CNS plane and key, the converter selects the corresponding `kiconv_cns*_utf8[]` table, then lookup code emits the mapped UTF-8 byte sequence.

The only structural transition is the source-level array boundary:

1. Continue plane 7 mappings inherited from the previous chunk.
2. Close `kiconv_cns7_utf8[]`.
3. Open `kiconv_cns15_utf8[]`.
4. Continue plane 15 mappings into the next chunk.

## State

The chunk contributes immutable static table data. It has no mutable state, locking, reference counts, allocation, initialization function, or teardown path.

Important state properties for consumers:

- Row order is ascending within each plane segment in this chunk. The only key decrease is intentional at the plane boundary, where plane 7 ends at `0xE6D5` and plane 15 restarts with `0x0000`.
- Plane 7 and plane 15 are separate lookup domains. Many key values repeat across the two arrays, but the CNS plane number is external state and makes those mappings distinct.
- UTF-8 byte arrays are fixed-width at four bytes. Three-byte mappings rely on C zero-initialization for the unused trailing byte.
- The sentinel/replacement row appears at the start of plane 15, not at the plane 7 continuation point.

## Dependencies

This chunk depends on file-level and neighboring kiconv context outside the range:

- `_SYS_KICONV_EUCTW_UTF8_H` include guard and `_KERNEL` guard wrap the full table header.
- `kiconv_table_array_t` and `uchar_t` come from common kernel/iconv headers, especially `kiconv_cck_common.h`.
- EUC-TW byte/plane parsing helpers are declared in `kiconv_tc.h`, including the `0x8E` multibyte introducer and CNS plane mask constants.
- The broader kiconv framework advertises `euctw` as a supported code name in `uts/common/os/kiconv.c`.
- The full header is listed in `usr/src/uts/common/sys/Makefile`.
- Reverse-direction UTF-8 to EUC-TW conversion data lives separately in `kiconv_utf8_euctw.h`.

No OS/VFS/block-storage APIs are used directly here despite the subset scope; this is kernel character-conversion data.

## Risks and Edge Cases

- Table count coupling: `KICONV_CNS7_UTF8_MAX` and `KICONV_CNS15_UTF8_MAX` must stay synchronized with the complete generated arrays. This chunk includes a close/open boundary where manual regeneration errors can create off-by-one defects.
- Plane-key ambiguity: repeated key values across plane 7 and plane 15 are expected. Any consumer that ignores plane selection and treats the key as globally unique will return incorrect characters.
- Variable UTF-8 length in fixed storage: rows with three explicit bytes rely on zero-filled trailing bytes. Consumers must determine output length correctly and avoid blindly copying all four bytes for every row.
- Sparse CNS ranges: keys are monotonically increasing inside each plane segment but not dense. Lookup code must search table entries rather than derive an array offset directly from the key.
- Generated-data integrity: an individual hex mapping can be corrupted without a compile-time failure; verification needs data-level comparison against the intended Unicode/CNS source tables.
- Header inclusion cost: because these arrays are `static` in a header, every including translation unit gets private copies unless the build intentionally includes it in only one converter implementation.

## Cross-Chunk References

- Earlier chunks define the file header, include guards, `KICONV_CNS*_UTF8_MAX` constants, and complete plane 1 through plane 6 tables.
- The immediately preceding chunk starts `kiconv_cns7_utf8[]` at line 42305 and covers its first 4,163 rows through key `0xCDBC`.
- This chunk completes `kiconv_cns7_utf8[]` with 2,375 additional rows, ending at key `0xE6D5`.
- This chunk starts `kiconv_cns15_utf8[]` at line 48847 and covers its first 4,747 rows through key `0xD6E5`.
- The next chunk must continue `kiconv_cns15_utf8[]` from key `0xD6E6`, finish plane 15 through key `0xEDB9`, and then cover the closing `_KERNEL`, C++ linkage, and include-guard directives near the end of the file.