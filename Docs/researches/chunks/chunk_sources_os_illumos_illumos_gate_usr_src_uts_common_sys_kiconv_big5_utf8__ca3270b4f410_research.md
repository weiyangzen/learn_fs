# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h lines 8445-13808

## Scope

This report covers lines 8445-13808 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h` for `learn_fs` subset A. The chunk is the final ordered segment of the kernel Big5-to-UTF-8 mapping table. It begins at the table entry for Big5 code `0xd7cc` and reaches EOF, including the closing initializer and header guards.

## Public Surface And APIs

This chunk does not introduce new APIs, macros, functions, typedefs, or exported declarations. It contributes data to the file-level static kernel table declared earlier as:

- `static kiconv_table_array_t kiconv_big5_utf8[]`
- `KICONV_BIG5_UTF8_MAX`, defined before this chunk as `13718`

Each visible table element has a 16-bit Big5 key and a three-byte UTF-8 payload stored in the `u8[4]` member of `kiconv_table_array_t`. The shared type comes from `kiconv_cck_common.h`:

- `uint32_t key`
- `uchar_t u8[4]`

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven in conversion code that includes this header: assemble Big5 key, search or index `kiconv_big5_utf8[]`, copy matching UTF-8 bytes, and handle misses outside this table.

## State And Dependencies

All state is static initializer data compiled only under `_KERNEL`. This chunk closes the array at line 13800, `_KERNEL` at line 13802, the C++ wrapper at lines 13804-13806, and the include guard at line 13808.

Dependencies are `kiconv_table_array_t`, `uint32_t`, `uchar_t`, and external kernel conversion code consuming the table.

## Risks And Cross-Chunk References

The chunk contains 5,355 ascending entries from `0xd7cc` to `0xf9dc`. Big5 trail-byte gaps and lead transitions such as `0xd7fe -> 0xd840` are intentional. The table must remain sorted, and `KICONV_BIG5_UTF8_MAX` must match the full table across chunks. Chunk 1 contains the declaration and earlier entries; this chunk supplies the final entries and closure.