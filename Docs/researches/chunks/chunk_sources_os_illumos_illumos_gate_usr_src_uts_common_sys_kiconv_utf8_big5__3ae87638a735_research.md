# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h lines 13700-13801

## Scope

This report covers lines 13700-13801 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h` for `learn_fs` subset A. The chunk is the final ordered segment of the kernel UTF-8-to-Big5 mapping table. It begins at the row for UTF-8 byte sequence `0xEFB9A5` and reaches EOF, including the closing table initializer and preprocessor guard closures.

## Public Surface And APIs

This chunk does not introduce new callable APIs, macros, typedefs, or exported symbols. It contributes data to the file-level static kernel table declared earlier as:

- `#define KICONV_UTF8_BIG5_MAX (13711)`
- `static kiconv_table_t kiconv_utf8_big5[] = { ... }`

The table element type is `kiconv_table_t` from `kiconv_cck_common.h`, with two `uint32_t` fields:

- `key`: UTF-8 bytes packed into a scalar table key.
- `value`: destination Big5 code unit stored as a 16-bit value inside the 32-bit field.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven in kernel iconv code that includes this header: UTF-8 input is packed into a key, `kiconv_utf8_big5[]` is searched, and the matching Big5 value is emitted. Invalid, unmapped, or replacement behavior is handled outside this data header.

## State And Dependencies

All state in this range is immutable static initializer data compiled only under `_KERNEL`. The chunk contains 93 mapping rows, from `0xEFB9A5 -> 0xa1e1` through `0xEFBDA4 -> 0xa14e`, then closes:

- `kiconv_utf8_big5[]` at line 13793
- `_KERNEL` at line 13795
- C++ wrapper at lines 13797-13799
- `_SYS_KICONV_UTF8_BIG5_H` at line 13801

Dependencies include `_KERNEL`, `_SYS_KICONV_UTF8_BIG5_H`, `kiconv_table_t`, `uint32_t`, and external kiconv conversion logic.

## Risks And Cross-Chunk References

The chunk’s main risks are generated-data drift, table count mismatch with `KICONV_UTF8_BIG5_MAX`, and preserving sorted key order. The visible mappings remain ascending despite intentional gaps such as `0xEFBC81 -> 0xEFBC83`.

Earlier chunk(s) contain the license, include guard, macro definition, table declaration, special hold entry `0x0000 -> 0x003f`, and preceding mappings through `0xEFB9A4 -> 0xa1e0`. This chunk supplies the final 93 rows and file closure; the per-file merge should verify full initializer length, ascending keys, and the final guard order.