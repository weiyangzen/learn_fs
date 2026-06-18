# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_cp950hkscs.h lines 13706-18477

This report covers ordered chunk 2 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_cp950hkscs.h`, lines 13706-18477, within `learn_fs` subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, table type, exported header list, and charset registry context.

## Role In The File

This chunk is the tail of an illumos kernel iconv data header for UTF-8-to-CP950-HKSCS conversion. It continues the static initializer opened earlier:

- `#define KICONV_UTF8_CP950HKSCS (18387)` declares the expected number of mappings.
- `static kiconv_table_t kiconv_utf8_cp950hkscs[] = { ... }` stores mappings as `{ uint32_t key; uint32_t value; }` entries from `kiconv_cck_common.h`.
- Keys are UTF-8 byte sequences packed into integers, not Unicode scalar values. Values are CP950-HKSCS code units.

Lines 13706-18477 contain 4,763 mapping entries, then close the table and the surrounding `_KERNEL`, C++, and include guards. The first entry in this chunk is:

```c
0xE8BC9F, 0xbdf9,
```

The last entry is:

```c
0xEFBFA5, 0xa244
```

The whole file contains 18,387 mapping entries, matching `KICONV_UTF8_CP950HKSCS`.

## APIs And Data Contracts

No callable API is declared in this chunk. Its externally relevant interface is the header-local static symbol `kiconv_utf8_cp950hkscs[]`, which can be included by kernel conversion code needing Windows-compatible UTF-8 to CP950-HKSCS lookup data.

The table contract visible from adjacent context is:

- `key`: packed UTF-8 byte sequence in ascending numeric order.
- `value`: CP950-HKSCS encoded output value.
- Lookup code elsewhere can use the ascending key order for binary search or ordered-table assumptions.
- Because the array is `static` in a header, every translation unit that includes it gets a private copy unless compiler/linker behavior removes unused data.

## Control Flow

There is no runtime control flow in this chunk: no functions, loops, branches, calls, allocation, locking, or error handling. Runtime behavior is indirect through conversion routines that include this table and search it.

The only structural flow is C preprocessing:

1. The table initializer continues from the previous chunk.
2. Line 18469 closes the array initializer with `};`.
3. Line 18471 closes `_KERNEL`.
4. Lines 18473-18475 close the optional C++ `extern "C"` block.
5. Line 18477 closes `_SYS_KICONV_UTF8_CP950HKSCS_H`.

## State And Data Shape

The chunk is immutable static conversion state. There is no per-call state and no mutation.

Observed key ranges in this chunk:

- `0xE8BC9F` through `0xE8BFBF`: 137 entries.
- `0xE98080` through `0xE9BEA5`: 2,670 entries.
- `0xEE8080` through `0xEEBAB7`: 1,432 entries.
- `0xEF8C83` through `0xEFBFA5`: 524 entries.

The chunk remains strictly ascending by key and has no duplicate keys. It includes ordinary CJK UTF-8 ranges, private-use-style packed UTF-8 ranges beginning with `0xEE`, and fullwidth/compatibility forms beginning with `0xEF`. CP950-HKSCS output values span many byte ranges, including compatibility/vendor extension-looking ranges such as `0x88xx` through `0x9fxx` and ordinary Big5/CP950 ranges such as `0xa1xx`, `0xc6xx`, `0xe8xx`, and `0xf9xx`.

Duplicate CP950-HKSCS output values are visible across the full file and some are introduced by this tail range, especially where private-use/compatibility Unicode forms map to the same CP950-HKSCS bytes as earlier Unicode keys. This is expected for a compatibility conversion table but means the reverse table cannot be inferred as a one-to-one mechanical inverse.

## Dependencies And Integration

Visible dependencies and integration points:

- `kiconv_cck_common.h` defines `kiconv_table_t` as two `uint32_t` fields and defines related CCK conversion types.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_utf8_cp950hkscs.h` for installation/export alongside the related CCK conversion headers.
- `uts/common/os/kiconv.c` registers normalized charset name `cp950hkscs` with code id `17`, tying this table family to the kernel iconv charset registry.
- `kiconv_cp950hkscs_utf8.h` is the companion CP950-HKSCS-to-UTF-8 table. Because duplicate target values exist in this UTF-8-to-CP950-HKSCS direction, the reverse table is a curated companion, not simply this table reversed.

A direct `.c` include of `kiconv_utf8_cp950hkscs.h` was not found by simple textual search under `usr/src`; consumers may be generated, indirect, platform-selected, or outside the searched direct-reference pattern.

## Risks And Maintenance Notes

- Table corruption risk is data-order sensitive. If entries are inserted out of ascending `key` order, lookup code relying on binary search or ordered traversal may fail silently.
- Count drift risk exists if entries are added or removed without updating `KICONV_UTF8_CP950HKSCS`; this chunk confirms the current full-file count matches 18,387.
- Header-static storage can duplicate a large table per including translation unit. That may be intentional for generated illumos kiconv headers, but it is worth preserving existing include patterns.
- Compatibility aliasing is intentional but risky for automated regeneration: multiple UTF-8 keys can map to the same CP950-HKSCS value, so round-trip behavior depends on direction-specific tables and chosen canonical mappings.
- The file is kernel-gated by `_KERNEL`; userland reuse would require different inclusion conditions or generated data export.

## Cross-Chunk References

The previous chunk must provide the CDDL/Unicode license blocks, include guard opening, C++ wrapper opening, `_KERNEL` guard opening, `KICONV_UTF8_CP950HKSCS`, the `kiconv_utf8_cp950hkscs[]` declaration, the replacement mapping `0x0000 -> 0x003f`, and all mappings before `0xE8BC9F`.

This chunk completes the table and the file. There is no later chunk for `kiconv_utf8_cp950hkscs.h` after line 18477. Any merged per-file report should combine the earlier declaration and first ranges with this chunk's proof that the table closes cleanly, remains ordered through the tail, and matches the declared mapping count.