# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 3891-7950

## Scope

This chunk is the middle of ReactOS ext2's generated CP950/Big5 NLS conversion source. It contains only static Unicode-to-charset lookup data, plus the tail of the previous table and the declaration line for the next table. It does not define exported APIs, driver entry points, locking, allocation, I/O, or filesystem metadata logic.

The active data in this range is part of `page_uni2charset[]`'s backing table set used later by `uni2char()`. Each `u2c_XX` table maps Unicode code points with high byte `0xXX` to two CP950 bytes. A pair of `0x00, 0x00` means unmappable.

## APIs And Entry Points

- No functions or public APIs are declared in this chunk.
- The chunk contributes `static unsigned char u2c_XX[512]` arrays, which are private translation tables for the file-local NLS implementation.
- Adjacent lookup code outside this chunk wires these arrays into `page_uni2charset[256]` and exposes them through the file's `static struct nls_table table` callbacks:
  - `uni2char()` for Unicode to CP950 conversion.
  - `char2uni()` for CP950 to Unicode conversion, using separate `c2u_*` tables from earlier chunks.
  - module registration through `register_nls(&table)` and alias `big5`.

## Data Covered

The chunk starts at line 3891 inside the prior `u2c_51` table and includes its final entries before `u2c_52` begins at line 3920. It then contains these complete or visible table declarations:

- Complete in this chunk: `u2c_52` through `u2c_8D`.
- Starts at the final line of this chunk: `u2c_8E`.
- Partial before this chunk: `u2c_51`.

The complete tables correspond to Unicode high-byte pages `0x52xx` through `0x8Dxx`, mostly CJK mapping ranges. Several arrays have fewer explicit initializers than their 512-byte capacity; C zero-fills the remaining bytes, preserving the unmappable `0x00, 0x00` sentinel behavior.

## Control Flow

There is no direct control flow in lines 3891-7950. Runtime use is later:

1. `uni2char()` splits `wchar_t uni` into high byte `ch` and low byte `cl`.
2. It selects `page_uni2charset[ch]`.
3. For pages in this chunk, entries `0x52` through `0x8D` point to the corresponding `u2c_*` tables.
4. It reads two bytes at `cl * 2`.
5. `0x00, 0x00` returns `-EINVAL`; otherwise the conversion emits two CP950 bytes.

## State, Dependencies, Risks

All data here has internal linkage through `static`, but the arrays are not `const`, so they occupy writable static storage despite being lookup data. There is no locking, allocation, or mutable runtime state in this chunk.

Dependencies are structural: these arrays rely on the generated two-byte-per-entry layout, `page_uni2charset[]`, and `uni2char()`'s zero-pair invalid-marker contract. Risks are table corruption, malformed regeneration, or chunk-boundary misunderstanding around partial `u2c_51` and `u2c_8E`.

## Cross-Chunk References

- Previous chunk contains the start of `u2c_51`, earlier `u2c_*` tables, the reverse `c2u_*` tables, and `page_charset2uni[]`.
- This chunk completes the visible tail of `u2c_51`, defines `u2c_52` through `u2c_8D`, and starts `u2c_8E`.
- Next chunk continues `u2c_8E`, defines later `u2c_*` pages, and contains `page_uni2charset[]`, case tables, conversion functions, and NLS registration.