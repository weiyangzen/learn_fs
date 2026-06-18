# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_uhc.h lines 13707-17137

## Scope

This chunk is the final segment of the kernel-only `static kiconv_table_t kiconv_utf8_uhc[]` mapping table declared near line 81. The requested range contains only table entries and the closing preprocessor/C++ guards; it does not define functions, macros, or executable branches.

## APIs And Data

- `kiconv_utf8_uhc[]`: continued UTF-8-to-UHC conversion table. Each row is a `{ key, value }` initializer for `kiconv_table_t`, where `key` is a packed UTF-8 byte sequence and `value` is the corresponding UHC code.
- The visible range starts at `0xECAEB6 -> 0xA893`, continues through late Hangul syllable mappings, then includes compatibility/private-use mappings such as `0xEFA480..0xEFA88B`, fullwidth ASCII/punctuation mappings `0xEFBC81..0xEFBD9E`, and final currency/symbol mappings `0xEFBFA0..0xEFBFA6`.
- The table is closed at line 17129, followed by `#endif /* _KERNEL */`, the `extern "C"` close for C++ inclusion, and the include guard close `_SYS_KICONV_UTF8_UHC_H`.

## Control Flow

There is no local control flow in this chunk. Runtime behavior is data-driven: conversion code elsewhere can binary-search `kiconv_utf8_uhc[]` and emit the `value` for a matched packed UTF-8 `key`. The table is sorted in ascending `key` order across this chunk, which is required by the shared `kiconv_binsearch()` API declared in `kiconv_cck_common.h`.

## State And Dependencies

- State is immutable static initializer data compiled only when `_KERNEL` is defined.
- The element type is `kiconv_table_t`, defined in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`.
- The table size contract is established outside this chunk by `KICONV_UTF8_UHC_MAX (17047)`. This chunk contributes the tail entries to that count.
- Header dependencies include kernel integer typedefs, the common CCK conversion declarations, and inclusion by whatever UHC conversion module instantiates this static table. Because the symbol is `static`, every translation unit that includes the header gets a private copy.

## Risks

- Generated table integrity matters more than local logic: a wrong pair silently corrupts UTF-8 to UHC conversion for that code point.
- Binary search users depend on strict ascending key order. Insertions or edits in this chunk must preserve sort order, including the non-Hangul compatibility ranges near the end.
- The table uses packed UTF-8 byte values rather than Unicode scalar values; maintainers must not normalize entries to code points without changing lookup code.
- The `KICONV_UTF8_UHC_MAX` constant must stay synchronized with the full table length. This final chunk closes the initializer, so omissions or extra rows here affect global bounds used by callers.
- Being a `static` large table in a header can duplicate data if included from multiple translation units, though that appears to be an established illumos kiconv pattern.

## Cross-Chunk References

- Earlier chunks contain the table declaration, license/include guards, `KICONV_UTF8_UHC_MAX`, the first sentinel mapping `0x0000 -> 0x003F`, and the preceding UTF-8/UHC entries.
- This chunk continues directly from line 13706 (`0xECAEB5 -> 0xA892`) and begins at line 13707 (`0xECAEB6 -> 0xA893`), so chunk merging should treat the mapping table as one continuous sorted array.
- The final per-file report should connect this header to the reverse table `kiconv_uhc_utf8.h` and the shared conversion contracts in `kiconv_cck_common.h`, especially `kiconv_table_t`, `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()`.