# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 25456-33002

## Scope

This report covers lines 25456-33002 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The slice is entirely inside the `static kiconv_table_array_t kiconv_gbk4_utf8[]` initializer, which begins earlier at line 24027 and maps GB18030 four-byte keys to UTF-8 byte arrays.

The reviewed range contains 7,547 complete mapping rows. It starts at key `0x81319137 -> DA B1` and ends at key `0x81379033 -> E2 92 B7`. The chunk boundary is clean: line 25455 precedes this range with another table row, and line 33003 continues the same table with the next row.

## Public Surface And APIs

This chunk adds data to the kernel-only GB18030-to-UTF-8 conversion table. It introduces no new preprocessor guards, macros, structs, functions, or callable APIs within the line range.

The relevant public/static surface is defined outside the chunk:

- `KICONV_GBK4_UTF8_MAX (39421)` declares the total number of GB18030 four-byte mappings in this file.
- `kiconv_gbk4_utf8[]` is a `static kiconv_table_array_t` table, visible only to translation units that include this header under `_KERNEL`.
- `kiconv_table_array_t` is declared in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

Rows in this chunk initialize the `key` with a packed four-byte GB18030 code and initialize `u8` with either two or three UTF-8 bytes. The trailing bytes in `u8[4]` rely on normal static zero-fill.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the generic kernel kiconv machinery that consumes this table:

1. GB18030 byte validation is defined separately in `kiconv_sc.h`.
2. A valid four-byte GB18030 sequence is packed into a `uint32_t` key.
3. Conversion code searches `kiconv_gbk4_utf8[]`, using the sorted-key invariant required by `kiconv_binsearch()`.
4. On match, the row's `u8` array is copied to the UTF-8 output.
5. Error handling and replacement behavior are implemented outside this data header.

## State And Dependencies

State in this chunk is immutable static initializer data compiled into any kernel translation unit that includes this header. There is no mutable state, locking, allocation, or I/O.

Dependencies visible from adjacent file context and related headers:

- `_KERNEL` guard controls whether the table declarations are visible.
- `kiconv_table_array_t` and `kiconv_binsearch()` are declared by `uts/common/sys/kiconv_cck_common.h`.
- GB18030 validation and constants live in `uts/common/sys/kiconv_sc.h`.
- `uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` and companion `kiconv_utf8_gb18030.h`.
- `uts/common/os/kiconv.c` registers encoding names including `gb18030`, `gbk`, `cp936`, `936`, and `euccn`.

## Risks And Cross-Chunk References

Important invariants: every row must remain syntactically complete, keys must remain sorted for binary search, `KICONV_GBK4_UTF8_MAX` must match the complete table row count across all chunks, and UTF-8 byte arrays must remain valid with zero-filled padding.

Risks visible here include generated-data drift, mid-table chunk boundary mistakes, sparse Unicode ranges after `U+2000` being misread as gaps, and reliance on external validation to reject malformed GB18030 sequences before table lookup.

Previous chunk(s) must account for the file header, guards, macros, the complete two-byte `kiconv_gbk_utf8[]` table, and the start of `kiconv_gbk4_utf8[]`. Next chunk(s) must continue at line 33003 with `0x81379034 -> E2 92 B8`, cover the remaining table rows through line 63449, and verify the closing `_KERNEL`, C++ extern, and header guard structure.