# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 37912-49826

This chunk is part of learn_fs subset A because `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`. I read the full requested range, lines 37912-49826, and used adjacent context only to identify the enclosing table declaration, shared table type, and neighboring table boundaries.

The source file is a generated-style illumos kernel iconv mapping header for UTF-8 to EUC-TW/CNS 11643 conversion. This chunk contains only initializer rows inside `static kiconv_table_t kiconv_utf8_euctw[]`; it has no function definitions, local branches, loops, calls, allocation, locking, or direct filesystem/block-storage behavior.

## APIs and Data Surface

- Enclosing declaration: `static kiconv_table_t kiconv_utf8_euctw[]`, opened at line 88 under `_KERNEL`.
- Count contract: `KICONV_UTF8_EUCTW_MAX (55442)`, defined before the array and applying to the complete table, not this chunk alone.
- Entry type: `kiconv_table_t` from `sys/kiconv_cck_common.h`, with `uint32_t key` and `uint32_t value`.
- This chunk contributes 11,915 complete rows.
- First row in this chunk: `0xF0A4AD91 -> 0x5BAB3`.
- Last row in this chunk: `0xF0A8AB8B -> 0xFE1B9`.

Every key in this slice is an encoded four-byte UTF-8 value beginning with `0xF0`, so the chunk covers supplementary-plane Unicode code points represented in the table's packed-UTF-8 key format. Values are packed CNS/EUC-TW destinations. In this slice, destination prefixes distribute as: prefix `0x3` has 4 rows, `0x4` has 1,446 rows, `0x5` has 3,356 rows, `0x6` has 2,147 rows, `0x7` has 2,702 rows, and `0xF` has 2,260 rows.

## Control Flow and Runtime Use

There is no executable control flow in the chunk. Runtime behavior is indirect:

1. Common UTF-8-to-CCK conversion code accumulates an input UTF-8 scalar into the packed integer key format.
2. The EUC-TW converter searches `kiconv_utf8_euctw[]`, using the sorted key table contract exposed by `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.
3. On a hit, the 32-bit `value` is decoded by conversion code outside this chunk into the output EUC-TW/CNS bytes.
4. Buffer accounting, invalid-sequence handling, replacement behavior, and errno propagation live in shared kiconv code, not in this table slice.

The key column in this chunk is strictly ascending, with no duplicate keys detected in the requested range.

## State and Dependencies

The chunk defines static header data only. It introduces no mutable runtime state beyond the `static` array object created in each translation unit that includes the header. It performs no synchronization and has no lifecycle hooks.

Direct dependencies visible from adjacent context:

- `_KERNEL` guard and `_SYS_KICONV_UTF8_EUCTW_H` include guard.
- `kiconv_table_t`, `uint32_t`, and common UTF-8-to-CCK conversion prototypes from `sys/kiconv_cck_common.h`.
- EUC-TW byte-shape and plane constants from `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE` and `KICONV_TC_EUCTW_PMASK`.
- Registration context in `uts/common/os/kiconv.c`, where encoding name `"euctw"` is mapped to code id `16`.
- Export context in `uts/common/sys/Makefile`, which lists `kiconv_utf8_euctw.h` as an installed/exported sys header.
- Reverse-direction consistency with `sys/kiconv_euctw_utf8.h`, which has per-plane `kiconv_cnsN_utf8[]` tables.

## Risks and Maintenance Notes

- Table ordering is part of the functional contract. Reordering or inserting rows incorrectly can break binary-search lookup even though the C syntax still compiles.
- `KICONV_UTF8_EUCTW_MAX` must remain aligned with the complete table length.
- The header comment says the data supports Unicode 3.2 / `Unihan-3.2.0.txt`, includes plane 1/2/14 mappings, and supports CNS11643-86 but not CNS11643-92.
- The table is not declared `const`; accidental writes by including code would mutate conversion behavior for that translation unit.
- Round-trip behavior depends on consistency with `kiconv_euctw_utf8.h`.
- The `0x0000 -> 0x0003F` special non-identical-conversion entry is outside this chunk.

## Cross-Chunk References

- Previous chunk(s) provide the file prologue, guards, `KICONV_UTF8_EUCTW_MAX`, the `kiconv_utf8_euctw[]` declaration, the non-identical-conversion sentinel, and all rows before key `0xF0A4AD91`.
- This chunk continues the same single `kiconv_utf8_euctw[]` table from `0xF0A4AD91` through `0xF0A8AB8B`; it does not open or close any declarations.
- Later chunk(s) must continue the same table after line 49826, eventually closing the array near the end of the file and then closing the `_KERNEL`, C++, and include guards.