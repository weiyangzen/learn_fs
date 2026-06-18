# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 16876-24891

## Scope

This chunk is a contiguous slice of the illumos kernel EUC-TW-to-UTF-8 mapping header. It begins inside `kiconv_cns3_utf8[]`, ends inside `kiconv_cns4_utf8[]`, and contains no executable functions or local control-flow branches. Its behavior is entirely data-driven: kernel iconv code indexes or searches static `kiconv_table_array_t` entries to translate CNS 11643/EUC-TW code points into UTF-8 byte sequences.

## APIs And Data Structures

- Provides part of `static kiconv_table_array_t kiconv_cns3_utf8[]` from lines 16876-20015, covering 3,139 entries from key `0xC3DC` through `0xE7AA`.
- Provides the start and middle of `static kiconv_table_array_t kiconv_cns4_utf8[]` from lines 20018-24891, covering 4,873 entries from the sentinel `0x0000` through key `0xD4F8`.
- The entry type comes from `kiconv_cck_common.h`: `uint32_t key; uchar_t u8[4];`. The `u8[4]` payload supports both 3-byte BMP UTF-8 and 4-byte supplementary-plane UTF-8.
- The maximum-count constants declared near the file top remain the table-level contract for this chunk: `KICONV_CNS3_UTF8_MAX` is `6395`, and `KICONV_CNS4_UTF8_MAX` is `7287`.

## Control Flow And State

There is no direct control flow in this line range. Runtime behavior depends on the conversion layer selecting the correct CNS plane table, locating an entry by `key`, using `u8_number_of_bytes[first_byte]` to determine output length, checking output capacity, and copying the stored UTF-8 bytes.

The chunk is stateless read-only kernel data. It allocates no memory, mutates no globals, and performs no locking. Any conversion state, error handling, replacement-character policy, and buffer advancement live in the kiconv conversion wrappers and plane-selection code outside this chunk.

## Data Shape

- `kiconv_cns3_utf8[]` portion: 3,139 entries, key range `0xC3DC` to `0xE7AA`, with 3,118 three-byte entries and 21 four-byte entries.
- `kiconv_cns4_utf8[]` portion: 4,873 entries, key range `0x0000` sentinel then `0xA1A1` to `0xD4F8`, with 2,619 three-byte entries and 2,254 four-byte entries.
- Ordering checks over both portions found no descending or duplicate key transitions.
- `kiconv_cns4_utf8[]` starts with `0x0000 -> EF BF BD`, matching the replacement-character sentinel pattern used by other tables in this header.

## Dependencies

- `_KERNEL` guard: the arrays are only exposed for kernel builds.
- `kiconv_table_array_t` from `sys/kiconv_cck_common.h`.
- UTF-8 byte-length validation/copying depends on `u8_number_of_bytes[]`, declared in common kiconv headers and provided by Unicode textprep code.
- EUC-TW plane parsing is related to macros in `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and valid EUC-TW byte checks.
- Reverse-direction mapping lives in `sys/kiconv_utf8_euctw.h`; this chunk is for CNS/EUC-TW to UTF-8 direction only.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_euctw_utf8.h` as an exported kernel header.

## Risks And Cross-Chunk References

- Count drift risk: if entries are added or removed, `KICONV_CNS3_UTF8_MAX` and `KICONV_CNS4_UTF8_MAX` must stay aligned with the full arrays.
- Sort-order risk: binary-search users require monotonically increasing keys within each table; edits must preserve ordering across chunk boundaries.
- Boundary risk: this chunk crosses the plane #3/#4 array boundary at lines 20015-20018.
- Previous chunk should cover the beginning of `kiconv_cns3_utf8[]` up to key `0xC3DB`; this chunk continues at `0xC3DC`.
- Next chunk must continue `kiconv_cns4_utf8[]` at line 24892, key `0xD4F9`, after this chunk ends at key `0xD4F8`.