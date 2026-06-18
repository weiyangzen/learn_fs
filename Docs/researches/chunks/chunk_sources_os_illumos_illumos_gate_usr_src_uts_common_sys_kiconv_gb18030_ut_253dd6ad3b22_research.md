# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 16907-25455

## Scope

This chunk is a contiguous slice of an illumos kernel GB18030/GBK-to-UTF-8 mapping header. It begins inside the two-byte `kiconv_gbk_utf8[]` table, closes that table at lines 24024-24025, and then starts the four-byte `kiconv_gbk4_utf8[]` table at line 24027. It contains no executable functions; runtime behavior is entirely data-driven by common kiconv lookup and copy code outside this header.

## APIs And Data Structures

- Provides the tail of `static kiconv_table_array_t kiconv_gbk_utf8[]` from line 16907 through line 24024, covering 7,118 two-byte GBK/GB18030 keys from `0xD9A7` through `0xFEFE`.
- Defines the beginning of `static kiconv_table_array_t kiconv_gbk4_utf8[]` from line 24027 through line 25455, covering 1,428 four-byte GB18030 keys from the sentinel `0x00000000` through `0x81319136`.
- The entry type is `kiconv_table_array_t` from `sys/kiconv_cck_common.h`: `uint32_t key; uchar_t u8[4];`. This chunk stores 2-byte and 3-byte UTF-8 sequences in the fixed four-byte `u8` field.
- The table-size constants declared near the top of this same file are the full-table contracts: `KICONV_GBK_UTF8_MAX` is `23941`, and `KICONV_GBK4_UTF8_MAX` is `39421`.

## Control Flow And State

There is no local control flow, allocation, locking, or mutable state in this line range. The arrays are `static` kernel-only read-mostly data under the surrounding `_KERNEL` guard.

At runtime, common kiconv code receives a mapping-table ID or converter-specific table pointer, computes or searches for a `key`, derives the UTF-8 output length from `u8_number_of_bytes[entry.u8[0]]`, checks output capacity, and copies the stored bytes. Invalid-input handling, `EILSEQ`/`E2BIG`, replacement-character policy, buffer advancement, and conversion descriptor state are all implemented outside this chunk.

## Data Shape

- Total entries in this chunk: 8,546.
- `kiconv_gbk_utf8[]` portion: 7,118 entries, all two-byte keys, all with 3-byte UTF-8 payloads.
- `kiconv_gbk4_utf8[]` portion: 1,428 entries. The first is the `0x00000000 -> EF BF BD` replacement-character sentinel; the remaining entries begin at `0x81308130` and continue through `0x81319136`.
- UTF-8 payload widths in this chunk: 7,119 three-byte entries and 1,427 two-byte entries. The 3-byte count includes the four-byte-table sentinel.
- Mechanical checks over each table segment found no duplicate keys and no descending key transitions.

## Dependencies

- `_KERNEL` guard in this header limits these arrays to kernel builds.
- `kiconv_table_array_t` and the `u8_number_of_bytes[]` declaration come from `sys/kiconv_cck_common.h`.
- `usr/src/uts/common/os/kiconv.c` contains the common conversion loops that use `u8_number_of_bytes` and table entries to validate length, handle output capacity, and copy UTF-8 bytes.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` with the other kernel iconv headers.
- Reverse-direction UTF-8-to-GB18030 mappings live in `sys/kiconv_utf8_gb18030.h`; this chunk covers only GB18030/GBK to UTF-8 data.

## Risks And Cross-Chunk References

- Count drift risk: edits to either table must keep `KICONV_GBK_UTF8_MAX` and `KICONV_GBK4_UTF8_MAX` aligned with the full arrays, not just this chunk.
- Ordering risk: lookup code can rely on sorted mapping tables; generated or manual changes must preserve monotonic order across chunk boundaries.
- Boundary risk: this chunk crosses a table boundary. The `kiconv_gbk_utf8[]` initializer closes at lines 24024-24025, and `kiconv_gbk4_utf8[]` starts at line 24027.
- Previous chunk should cover the earlier `kiconv_gbk_utf8[]` entries through key `0xD9A6`; this chunk continues at `0xD9A7`.
- Next chunk should continue `kiconv_gbk4_utf8[]` at line 25456 with key `0x81319137`, after this chunk ends at `0x81319136`.