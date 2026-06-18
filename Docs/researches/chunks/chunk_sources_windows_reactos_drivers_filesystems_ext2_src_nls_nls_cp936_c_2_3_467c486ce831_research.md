# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 3841-7884

## Scope

This chunk is the middle of the generated CP936/GB2312 NLS conversion table used by the ReactOS ext2 filesystem driver copy of `linux/fs/nls_cp936.c`. It is in subset A because `sources/windows/reactos` is included by `Docs/research_subset_a.md`.

The chunk contains generated static lookup data only. It does not define executable functions, module registration, or exported symbols. Adjacent context shows the source file is a Linux NLS table implementation with `uni2char()`, `char2uni()`, `struct nls_table table`, `register_nls()`, and `unregister_nls()` later in the file.

## APIs And Exports

- No public APIs or exports are declared in this chunk.
- Visible static data contributes to the private implementation of the file-local NLS callbacks:
  - `char2uni()` uses `page_charset2uni[ch]` to decode a CP936 lead byte plus trail byte into a `wchar_t`.
  - `uni2char()` uses `page_uni2charset[ch]` to encode a Unicode `wchar_t` into one or two CP936 bytes.
- The chunk defines or partially defines lookup arrays, all with internal linkage:
  - Tail of `static wchar_t c2u_ED[256]`, which starts before the chunk.
  - Full `static wchar_t c2u_EE[256]` through `static wchar_t c2u_FE[256]`.
  - `static wchar_t *page_charset2uni[256]`, the first-level dispatch table for CP936 lead bytes.
  - Full `static unsigned char u2c_01[512]`, `u2c_02[512]`, `u2c_03[512]`, `u2c_04[512]`, `u2c_20[512]` through `u2c_26[512]`, `u2c_30[512]` through `u2c_33[512]`, and `u2c_4E[512]` through `u2c_75[512]`.
  - Beginning of `static unsigned char u2c_76[512]`, which continues past the chunk.

## Data Layout

The `c2u_*` arrays are two-byte CP936-to-Unicode pages. The high byte selects a page through `page_charset2uni[]`; the low byte indexes the selected 256-entry `wchar_t` array. Entries with `0x0000` are unmapped/invalid for two-byte decoding. In this chunk, most `c2u_EE` through `c2u_FE` pages reserve low byte ranges `0x00-0x3F`, include valid mappings for `0x40-0x7E`, skip `0x7F`, and continue valid mappings for much of `0x80-0xFE`, matching CP936 trail-byte shape.

`page_charset2uni[256]` is the central dispatch array for decoding. It maps lead bytes `0x81-0xFE` to `c2u_81` through `c2u_FE` and leaves unsupported lead bytes as `NULL`. The file intentionally leaves `0xFF` as `NULL`.

The `u2c_*` arrays are Unicode-to-CP936 pages. The Unicode high byte selects a page through `page_uni2charset[]` later in the file; the Unicode low byte indexes a 512-byte page as `low * 2`. Each entry pair is the CP936 byte sequence for that Unicode code point. A pair of `0x00, 0x00` marks an unmapped Unicode value. This chunk covers low Unicode pages and a large contiguous block from Unicode high byte `0x4E` through part of `0x76`, including many CJK Unified Ideograph ranges.

## Control Flow

There is no control flow inside the chunk. Runtime behavior is table-driven:

1. Decode path: `char2uni()` reads the first input byte as `ch`. If only one byte is available, it returns that byte as a single-byte character. Otherwise it looks up `page_charset2uni[ch]`; when the page pointer exists and the second byte is nonzero, it returns `page[cl]` unless that entry is `0x0000`. If no page exists, it falls back to a one-byte character.
2. Encode path: `uni2char()` splits `wchar_t uni` into high byte `ch` and low byte `cl`, looks up `page_uni2charset[ch]`, and reads two bytes at `cl * 2`. A `0x00, 0x00` pair is invalid. If no page exists and `ch == 0 && cl != 0`, it emits the low byte as a single-byte character.

The chunk’s `page_charset2uni[]` is directly used by the decode path; the chunk’s `u2c_*` tables are used indirectly after `page_uni2charset[]` is defined in a later chunk.

## State And Dependencies

All data in this chunk is immutable static storage. There is no allocation, locking, reference counting, mutation, or per-open filesystem state.

The data depends on Linux NLS types and callback contracts from the includes at the top of the file: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. The surrounding file binds these tables into a `struct nls_table` named `cp936` with alias `gb2312`.

## Risks

- The generated arrays are positional. Any insertion, deletion, or misordered initializer silently changes character mappings.
- `page_charset2uni[]` and the `c2u_*` declarations must remain synchronized; a wrong pointer maps an entire CP936 lead-byte page to unrelated Unicode code points.
- `u2c_*` pages must remain synchronized with the later `page_uni2charset[]` dispatch table; wrong high-byte dispatch corrupts Unicode-to-CP936 encoding.
- Invalid mappings are represented by sentinel zeros. Accidental nonzero data can make invalid byte sequences appear valid; accidental zeros can reject valid filenames.
- The chunk starts inside `c2u_ED` and ends inside `u2c_76`, so complete validation of those two arrays requires adjacent chunks.
- File names on ext2 volumes mounted through this NLS table can be mis-decoded or become unroundtrippable if either direction is edited inconsistently.

## Cross-Chunk References

- Earlier chunk content defines the beginning of the file, all `c2u_81` through most of `c2u_ED`, and the comments identifying this as an automatically generated Microsoft CP936 table.
- This chunk defines `page_charset2uni[]`, which references many `c2u_*` arrays from both earlier lines and this chunk.
- Later chunk content completes `u2c_76`, defines `u2c_77` and later Unicode-to-charset pages, defines `page_uni2charset[]`, adds ASCII case-conversion tables, and defines the `uni2char()`, `char2uni()`, NLS table, and module init/exit routines that consume the data.