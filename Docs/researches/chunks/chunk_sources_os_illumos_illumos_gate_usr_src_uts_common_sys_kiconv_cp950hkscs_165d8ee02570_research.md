# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 8440-16910

## Scope

This report covers lines 8440-16910 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h` for `learn_fs` subset A. The file is an illumos kernel iconv data header for CP950-HKSCS-to-UTF-8 conversion. This chunk is an interior slice of the static mapping table: it starts at CP950-HKSCS key `0xbf4d` and ends at key `0xf576`, without including the file header, macro definition, table declaration, closing initializer, or preprocessor guard closes.

The reviewed range contains 8,471 complete mapping rows. The whole file contains 18,322 rows, matching `KICONV_CP950HKSCS_UTF8_MAX`, so this chunk accounts for only the middle portion of the file-level table.

## Public Surface And APIs

This chunk introduces no new public functions, macros, typedefs, or declarations. It contributes initializer rows to the kernel-only table declared earlier in the file:

- `#define KICONV_CP950HKSCS_UTF8_MAX (18322)`
- `static kiconv_table_array_t kiconv_cp950hkscs_utf8[] = { ... }`

The table element type is defined in `usr/src/uts/common/sys/kiconv_cck_common.h` as:

- `uint32_t key`
- `uchar_t u8[4]`

Rows in this chunk use a two-byte CP950-HKSCS code value as `key` and a UTF-8 byte sequence as `u8`. Most rows have three explicit UTF-8 bytes; 78 rows have two explicit bytes and rely on C zero-initialization for the remaining `u8[4]` bytes.

## Data Layout Visible In This Chunk

The chunk is sorted table data. It begins immediately after line 8439's `0xbf4c` entry:

- line 8440: `0xbf4d -> { 0xE7, 0x87, 0x90 }`

It ends immediately before line 16911's `0xf577` entry:

- line 16910: `0xf576 -> { 0xE9, 0xB0, 0x89 }`

Measured properties for lines 8440-16910:

- Mapping rows counted: 8,471.
- First key: `0xbf4d`.
- Last key: `0xf576`.
- Duplicate keys in this chunk: none.
- Nonascending keys in this chunk: none.
- Explicit UTF-8 byte widths: 8,393 rows with three bytes, 78 rows with two bytes.
- Trail-byte validation: all keys use CP950/Big5-style trail bytes in `0x40-0x7e` or `0xa1-0xfe`; no rows use invalid trail bytes `0x7f-0xa0`.

The visible lead-byte coverage is `0xbf` through `0xf5`. Full lead-byte groups generally contain 157 rows, matching the valid Big5 trail-byte count after excluding `0x7f-0xa0`. Partial groups occur at the chunk boundaries: `0xbf` starts at trail `0x4d`, and `0xf5` ends at trail `0x76`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven and belongs to the kernel iconv conversion code that uses these CCK tables:

1. Caller-side conversion logic validates and combines a CP950-HKSCS byte pair into a table key.
2. The sorted `kiconv_table_array_t` table can be searched, typically through the shared `kiconv_binsearch()` helper declared in `kiconv_cck_common.h`.
3. On a match, the `u8` bytes are copied to the output buffer. Generic iconv code in `uts/common/os/kiconv.c` uses `u8_number_of_bytes[first_byte]` for table-driven UTF-8 output in analogous CCK-to-UTF-8 paths.
4. Missing or invalid input mappings are handled by caller policy; this header only supplies static mapping data.

The `cp950hkscs` name is registered in `uts/common/os/kiconv.c` with code ID `17`.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled under the file's `_KERNEL` guard. There is no allocation, locking, reference counting, I/O, filesystem state, or mutable global state.

Direct dependencies and adjacent integration points:

- `kiconv_table_array_t` from `usr/src/uts/common/sys/kiconv_cck_common.h`.
- Kernel/system integer and byte types such as `uint32_t` and `uchar_t`.
- `usr/src/uts/common/sys/Makefile`, which lists `kiconv_cp950hkscs_utf8.h` for installation/export.
- `kiconv_utf8_cp950hkscs.h`, the companion reverse-direction table.
- `kiconv_hkscs_utf8.h` and `kiconv_big5_utf8.h`, neighboring Traditional Chinese mapping tables.
- `uts/common/os/kiconv.c`, which registers the normalized charset name `cp950hkscs`.

A direct `.c` include or direct symbol reference to `kiconv_cp950hkscs_utf8` was not found by textual search in this checkout; build integration may be generated, indirect, or outside the searched direct-reference pattern.

## Risks And Invariants

The critical invariants are data-table invariants:

- The full table count must remain exactly `KICONV_CP950HKSCS_UTF8_MAX` entries. This chunk contributes 8,471 of the whole file's 18,322 rows.
- Keys must remain sorted for binary-search consumers. This chunk is strictly ascending from `0xbf4d` through `0xf576`.
- Duplicate keys would make conversion ambiguous. No duplicates were found in this chunk.
- Big5/CP950 trail-byte gaps are intentional. Automated table normalization must not insert or reinterpret invalid `0x7f-0xa0` trail positions.
- Two-byte UTF-8 payload rows depend on zero-filled trailing slots in `uchar_t u8[4]`.
- Generated-data drift is hard to review semantically; validation should prefer generated-source comparison, whole-table count/order checks, and conversion tests.
- Since the table is `static` in a header, every translation unit that includes it under `_KERNEL` receives a private copy.

## Cross-Chunk References

The previous chunk must provide the license, include guard, `_KERNEL` wrapper, `KICONV_CP950HKSCS_UTF8_MAX`, the opening `kiconv_cp950hkscs_utf8[]` declaration, the replacement row `0x0000 -> EF BF BD`, and all entries through line 8439/key `0xbf4c`.

This chunk starts cleanly at line 8440/key `0xbf4d` and ends cleanly at line 16910/key `0xf576`. The next chunk must resume at line 16911/key `0xf577`, continue through the final key `0xfefe`, and close the table initializer plus `_KERNEL`, C++ `extern "C"`, and `_SYS_KICONV_CP950HKSCS_UTF8_H` guards.