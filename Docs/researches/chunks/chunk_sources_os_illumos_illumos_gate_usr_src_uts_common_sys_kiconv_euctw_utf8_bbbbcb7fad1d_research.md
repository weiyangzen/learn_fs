# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 53595-55578

## Scope

This report covers lines 53595-55578 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The chunk is generated/static conversion data, not executable filesystem logic. It is the tail of the file: the final segment of the CNS 11643 plane #15 to UTF-8 table, followed by the closing initializer, `_KERNEL` guard, C++ linkage guard, and header include guard.

Adjacent context shows that this chunk belongs to:

- `static kiconv_table_array_t kiconv_cns15_utf8[]`, declared at line 48847.
- `KICONV_CNS15_UTF8_MAX (6722)`, the declared maximum mapping count for plane #15.
- `kiconv_table_array_t`, defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

## Public Surface And APIs

This chunk does not define functions, macros, or callable APIs. Its public surface is the continuation and closure of the file-local static table `kiconv_cns15_utf8[]`, compiled only under `_KERNEL`.

The visible table entries map CNS 11643 plane #15 two-byte row/cell keys to UTF-8 byte arrays. The chunk contributes 1,975 mappings from key `0xD6E6` through `0xEDB9`. Values are stored directly as 3-byte or 4-byte UTF-8 sequences in a fixed four-byte array; shorter 3-byte values rely on normal zero-initialization of the remaining byte in the aggregate.

Across the complete plane #15 table, adjacent context confirms 6,722 entries, matching `KICONV_CNS15_UTF8_MAX`.

## Control Flow

There is no executable control flow in this chunk. Runtime control flow is external to this header: kernel iconv EUC-TW conversion code selects the table for the active CNS plane, searches by `key`, and copies the `u8` bytes to the UTF-8 output buffer.

## State And Dependencies

State is immutable static kernel data. There are no locks, counters, heap allocations, device references, VFS objects, or filesystem state transitions.

Dependencies include `_KERNEL`, `kiconv_table_array_t` from `kiconv_cck_common.h`, illumos kernel/common C types such as `uchar_t` and `uint32_t`, and Unicode 3.2 / `Unihan-3.2.0.txt` mapping data noted near the file top.

## Risks And Cross-Chunk References

Primary risks are entry-count drift from `KICONV_CNS15_UTF8_MAX`, sorted-key breakage for lookup code, accidental loss of sparse gaps, and misreading `u8[4]` as four meaningful bytes for every entry.

Earlier chunks define the shared header, constants, and plane #1, #2, #3, #4, #5, #6, #7, plus the beginning and middle of plane #15. This chunk is the final merge segment for `kiconv_cns15_utf8[]` and closes the whole header.