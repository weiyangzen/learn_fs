# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 16639-18497

## Scope

- Repository subset: `Docs/research_subset_a.md` (`sources/os/illumos/illumos-gate` is in scope).
- Source span read completely: lines 16639-18497 of `usr/src/uts/common/sys/kiconv_hkscs_utf8.h`.
- This is chunk 3 of an oversized header. It covers the tail of the `kiconv_hkscs_utf8[]` static HKSCS-2004 to UTF-8 mapping table and the file's closing conditional guards.

## APIs and Data Structures

- The file declares `KICONV_HKSCS_UTF8_MAX` and `static kiconv_table_array_t kiconv_hkscs_utf8[]` near the top of the header, before this chunk.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`.
- Each row in this chunk is a table initializer mapping one BIG5-HKSCS code value to a UTF-8 byte sequence stored in `u8`.
- This chunk contributes 1,850 mapping rows, from key `0xf34c` at line 16639 through key `0xfefe` at line 18488.
- UTF-8 values include both three-byte BMP encodings and four-byte supplementary-plane encodings. In this chunk, 288 rows visibly contain a leading `0xF0` byte.

## Control Flow

- There is no executable control flow in this span. It is static data for conversion routines elsewhere.
- The chunk closes the table at line 18489, closes `_KERNEL` at line 18491, closes the C++ guard at lines 18493-18495, and closes `_SYS_KICONV_HKSCS_UTF8_H` at line 18497.

## State and Dependencies

- State is compile-time, read-only table content once linked into kernel consumers that include this header.
- Dependencies are `kiconv_table_array_t` from `usr/src/uts/common/sys/kiconv_cck_common.h`, kernel typedefs such as `uint32_t` and `uchar_t`, and the enclosing `_KERNEL` guard.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_hkscs_utf8.h`, so the header is part of the exported/common sys header set.

## Mapping Coverage

- Starts mid-`0xf3xx`: `0xf34c -> { 0xE8, 0xB6, 0xAA }`.
- Continues across `0xf4xx` through `0xfexx`, with expected BIG5/HKSCS gaps where low-byte values are invalid or unmapped.
- Ends at `0xfefe -> { 0xE7, 0xA7, 0x94 }`.
- Visible internal gaps near the tail include `0xfdf1`, `0xfe52`, `0xfe6f`, `0xfeaa`, and `0xfedd`.

## Risks and Cross-Chunk Notes

- Correctness risk is data integrity: a wrong byte literal or missing row silently corrupts conversion for that character.
- The fixed `uchar_t u8[4]` field requires consumers to handle three-byte and four-byte UTF-8 lengths correctly.
- Because the table is `static` in a header, each kernel translation unit that includes it may get a private copy.
- `KICONV_HKSCS_UTF8_MAX` is declared before this chunk as `18403`; row-count changes anywhere in the full table must stay synchronized.
- Prior chunks own the header preamble, constants, and earlier table rows. This chunk starts after `0xf34b` and owns the syntactic end of the table and file guards.
- No final per-file report was created.