# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 40492-47980

## Scope

This chunk is within `sources/os/illumos/illumos-gate`, which is included by `Docs/research_subset_a.md`. The requested line range was read completely.

The range is entirely initializer data inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the kernel GB18030 four-byte to UTF-8 mapping table declared earlier in this header. It contains 7,489 mapping entries, starting at line 40492 with packed GB18030 key `0x82338933` mapped to UTF-8 bytes `{ 0xE4, 0x8F, 0x8B }` (`U+43CB`) and ending at line 47980 with key `0x82398231` mapped to `{ 0xEB, 0x8B, 0x92 }` (`U+B2D2`).

## APIs And Data Structures

- No functions, macros, typedefs, or external entry points are defined in this chunk.
- The data extends `kiconv_gbk4_utf8[]`, declared at line 24027 as a `static kiconv_table_array_t` array under the file's `_KERNEL` guard.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- The full four-byte table size contract is `KICONV_GBK4_UTF8_MAX` with value `39421`, declared near the top of this same header.
- All entries in this chunk use three-byte UTF-8 payloads stored in the first three slots of `u8[4]`; the fourth array slot is implicit zero-initialized padding.

## Control Flow

There is no executable control flow, allocation, locking, error handling, or buffer movement in this chunk. Runtime behavior is supplied by the kernel kiconv conversion machinery that includes or is generated with these mapping headers.

The relevant runtime flow outside this data is: validate/pack a GB18030 four-byte input sequence, locate the packed key in the sorted `kiconv_gbk4_utf8[]` table, derive output length from the first UTF-8 byte via common UTF-8 length tables, check output capacity, then copy the stored UTF-8 bytes. Invalid input, replacement-character policy, `EILSEQ`/`E2BIG`, and descriptor state are handled outside this chunk.

## State And Data Flow

- Input state represented here is a packed 32-bit GB18030 key in the byte pattern `0x82 0x33..0x39 0x81..0xFE 0x30..0x39`.
- Output state is a fixed inline UTF-8 byte array. In this range the encoded Unicode scalar span is mostly ascending from `U+43CB` through `U+B2D2`.
- A mechanical pass over all 7,489 lines found zero malformed rows and zero GB18030 key-order breaks.
- The GB18030 keys are contiguous according to four-byte GB18030 digit/byte progression: fourth byte `0x30..0x39`, then third byte `0x81..0xFE`, then second byte `0x30..0x39`.
- Unicode scalar values are not perfectly contiguous. There are 21 intentional-looking jumps/skips, including the boundary from `0x82358F32 -> U+4DFF` to `0x82358F33 -> U+9FA6`, which transitions from CJK Extension A-era values into the CJK Unified Ideographs range.

## Dependencies

- Depends on the surrounding header context for CDDL/Unicode licensing, include guards, `_KERNEL`, and optional C++ `extern "C"` wrapping.
- Depends on `sys/kiconv_cck_common.h` for `kiconv_table_array_t`, `uint32_t`, `uchar_t`, `kiconv_binsearch()`, and UTF-8 byte-length helper declarations.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_gb18030_utf8.h` for installation/export with the other kernel iconv headers.
- `usr/src/uts/common/os/kiconv.c` contains the generic kernel iconv registration and common conversion wrappers; it registers the `"gb18030"` encoding name, while this chunk supplies only table data.
- Reverse-direction mapping is separate in `sys/kiconv_utf8_gb18030.h`; this chunk is GB18030/GBK four-byte to UTF-8 only.

## Risks And Cross-Chunk References

- Table ordering is a functional contract. Any edit that breaks sorted key order can break binary-search-style consumers.
- Count drift is a file-level risk: generated or manual edits must keep `KICONV_GBK4_UTF8_MAX` aligned with the full `kiconv_gbk4_utf8[]` table, not this chunk alone.
- Consumers must not assume Unicode scalar contiguity from GB18030 key contiguity; this chunk has visible scalar gaps and jumps.
- Since the table is `static` in a header, each translation unit that includes it can receive a private copy unless build structure constrains inclusion.
- Previous chunk ends at key `0x82338932 -> U+43CA`; this chunk continues immediately at `0x82338933`.
- Next chunk starts at line 47981 with key `0x82398232 -> U+B2D3`, continuing the same table.