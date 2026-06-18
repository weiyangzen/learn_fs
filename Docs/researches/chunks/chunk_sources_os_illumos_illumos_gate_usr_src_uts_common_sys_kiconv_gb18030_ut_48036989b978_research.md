# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 47981-55469

## Scope

This chunk is a contiguous middle slice of the illumos kernel GB18030-to-UTF-8 mapping header. It is entirely inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the table for GB18030 four-byte sequences. The range contains no function bodies, macros, branches, allocation, or synchronization; its runtime effect is data-driven through the kernel iconv conversion routines that consume this table.

## APIs And Data Structures

- Provides 7,489 `kiconv_table_array_t` entries from GB18030 key `0x82398232` through `0x8334F930`.
- Maps those packed four-byte GB18030 keys to UTF-8 byte sequences from `EB 8B 93` through `ED 80 93`, i.e. Unicode code points `U+B2D3` through `U+D013`.
- The entry type is defined in `sys/kiconv_cck_common.h` as `uint32_t key; uchar_t u8[4];`. In this chunk each initializer supplies a three-byte UTF-8 payload; the fourth byte is zero-filled by C aggregate initialization and is not copied by consumers.
- The table-level count contract is `KICONV_GBK4_UTF8_MAX` near the top of the file, declared as `39421` for the full `kiconv_gbk4_utf8[]` array.

## Control Flow And State

There is no direct control flow in this line range. Runtime control flow is in the kiconv conversion code outside the header: the selected table entry is found by key, `u8_number_of_bytes[first_utf8_byte]` determines how many bytes to copy, output capacity is checked, and then the stored UTF-8 bytes are emitted.

The chunk is stateless read-only kernel data. It does not allocate memory, mutate global state, acquire locks, or retain per-conversion state. Error handling for invalid input, `E2BIG`, replacement characters, and buffer advancement belongs to the conversion routines, not to this table segment.

## Data Shape

- Exact entries read in this chunk: 7,489.
- Key ordering is strictly increasing with no duplicate keys found in this range.
- The GB18030 four-byte key sequence is dense across the chunk: each key follows the previous one by the expected GB18030 four-byte successor rule over digit bytes `0x30`-`0x39` and trail bytes `0x81`-`0xFE`.
- UTF-8 payloads are valid three-byte sequences and increase by exactly one Unicode code point per entry.
- UTF-8 lead-byte transitions visible in the chunk:
  - Line 51354: key `0x8331D735` starts `EC 80 80` (`U+C000`).
  - Line 55450: key `0x8334F731` starts `ED 80 80` (`U+D000`).

## Dependencies

- The header content is only exposed under `_KERNEL`.
- `kiconv_table_array_t` comes from `sys/kiconv_cck_common.h`.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` with the other kernel iconv headers.
- Runtime consumers depend on `u8_number_of_bytes[]` from the common Unicode support code to derive the copy length from the first stored UTF-8 byte.
- Reverse-direction UTF-8-to-GB18030 mapping is separate, in `sys/kiconv_utf8_gb18030.h`; this chunk is only for GB18030 four-byte input to UTF-8 output.

## Risks And Cross-Chunk References

- Count drift risk: changing any entries in the full array requires keeping `KICONV_GBK4_UTF8_MAX` aligned with the generated table.
- Ordering risk: lookup code relies on sorted mapping tables; any manual insertion or deletion must preserve monotonic key order across chunk boundaries.
- UTF-8 validity risk: consumers trust table payloads and use only the first byte to decide copy length, so malformed byte triples would propagate directly to callers.
- Boundary continuity: the previous line before this chunk is key `0x82398231` mapping to `U+B2D2`; this chunk starts at `0x82398232` mapping to `U+B2D3`.
- Next chunk continuity: line 55470 continues with key `0x8334F931` mapping to `U+D014`, immediately after this chunk's final key `0x8334F930` mapping to `U+D013`.
- Full-array context: `kiconv_gbk4_utf8[]` begins at line 24027 with a replacement-character sentinel `0x00000000 -> EF BF BD` and the first real key `0x81308130`; it ends near line 63449 before the `_KERNEL` guard closes.