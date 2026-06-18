# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 1-13007

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h` lines 1-13007 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to confirm that line 13008 continues the same table initializer and to identify shared kiconv type/API declarations.

The chunk is generated/static kernel character-conversion data, not executable conversion logic. It begins the UTF-8 to EUC-TW/CNS 11643 mapping header and stops mid-initializer.

## APIs And Exported Data

This chunk defines the public header guard and kernel-only table data:

- `_SYS_KICONV_UTF8_EUCTW_H`: include guard for the header.
- `extern "C"` wrapping for C++ inclusion.
- `#ifdef _KERNEL`: all conversion declarations/data in this chunk are kernel-only.
- `KICONV_UTF8_EUCTW_MAX` as `55442`, the stated maximum mapping count for UTF-8 to EUC-TW.
- `static kiconv_table_t kiconv_utf8_euctw[]`: a file-local table when included into a kernel translation unit. The chunk starts the initializer at line 88 and includes 12,919 mapping rows through line 13007.

`kiconv_table_t` is defined in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`. In this table, `key` is a packed UTF-8 byte sequence represented as a hexadecimal integer, and `value` is a packed EUC-TW/CNS 11643 destination code. The first row is a special non-identical conversion entry:

- `0x0000 -> 0x0003F`, mapping the sentinel/non-identical input to ASCII question mark.

The table comment documents the data source and limitations: Unicode 3.2, `Unihan-3.2.0.txt`, CNS 11643 mapping, with some missing characters and no CNS11643-92 support.

## Data Shape

The included rows are sorted in nondecreasing packed UTF-8 key order, which matches the shared `kiconv_binsearch()` contract. The first and last entries in this chunk are:

- line 89: `0x0000 -> 0x0003F`
- line 13007: `0xE6AA85 -> 0x2DDB4`

The next chunk continues immediately at line 13008 with `0xE6AA86`, so this chunk does not close the array.

The chunk covers:

- Prologue, licensing, guard, and declaration setup on lines 1-88.
- Non-Han symbols and punctuation early in the table, including Greek, math symbols, arrows, box drawing, circled numbers, kana, and compatibility forms.
- CJK Extension A before the core CJK block.
- The transition into core CJK Unified Ideographs at line 6309 with `0xE4B880 -> 0x1C4A1`.
- Core CJK mappings through `0xE6AA85`.

Observed row counts and properties for lines 1-13007:

- 13,007 lines total.
- 12,919 table rows.
- Values are all five hex digits after `0x` in this range, including the sentinel `0x0003F`.
- Destination high nibbles observed: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, and `F`, indicating this chunk already spans multiple CNS/EUC-TW destination groups and compatibility/private mapping cases.
- One duplicate key is visible: `0xE58D84` appears on lines 7519 and 7520 with two different destination values, `0x1A4BF` and `0x3A1B8`.

## Control Flow

There are no functions, branches, loops, allocations, locks, or runtime side effects in this chunk. Runtime behavior is indirect:

1. A UTF-8 to CCK/EUC-TW converter reads bytes and packs a valid UTF-8 sequence into a `uint32_t` key.
2. The converter searches `kiconv_utf8_euctw` with the shared `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)` API declared in `kiconv_cck_common.h`.
3. If found, the packed destination value is emitted as EUC-TW bytes by the including conversion module.
4. If absent, the common wrapper path handles invalid or unmappable input according to kiconv flags and errno behavior.

The chunk itself only provides the data needed by that lookup path.

## State And Dependencies

All state in this chunk is static compiled data. Because the array is declared `static` in a header, each including translation unit gets its own internal-linkage copy rather than a single external symbol.

Direct dependencies visible or confirmed from adjacent common headers:

- `_KERNEL` controls whether the table is visible.
- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- `uint32_t` as the storage type for packed keys and values.
- Common CCK conversion APIs: `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()`.
- Kernel encoding registry recognizes `"euctw"` as code id `16` in `uts/common/os/kiconv.c`.
- `uts/common/sys/Makefile` installs/lists both `kiconv_utf8_euctw.h` and the reverse `kiconv_euctw_utf8.h`.

Licensing dependencies are also explicit: CDDL for illumos/Sun code and Unicode data-file permission text.

## Risks And Edge Cases

The table is data-critical: a wrong key or value silently corrupts character conversion rather than producing an obvious compile-time failure.

Important risks visible in this chunk:

- Binary search requires sorted keys. This chunk is sorted in nondecreasing order, but duplicate key `0xE58D84` can make selected output depend on `kiconv_binsearch()` duplicate handling.
- `KICONV_UTF8_EUCTW_MAX` must remain synchronized with the complete array length across all chunks. This chunk alone has 12,919 rows and does not validate the full count.
- The source comment says some characters are missing and CNS11643-92 is unsupported; callers must tolerate unmappable Unicode input.
- The array is mutable (`static kiconv_table_t`, not `const`), even though it is lookup data. Accidental writes in an including translation unit would affect conversion behavior.
- Since this is a generated table in a header, edits can increase kernel object size in every translation unit that includes it.

## Cross-Chunk References

This is chunk 1 for the file. It opens `kiconv_utf8_euctw[]` but does not close it. The next chunk must continue the same initializer starting at line 13008 with key `0xE6AA86` and should verify continued sortedness, eventual array closure, `_KERNEL`/C++ guard closure, and total entry count against `KICONV_UTF8_EUCTW_MAX`.

The reverse-direction file `kiconv_euctw_utf8.h` is related but separate: it maps CNS/EUC-TW plane tables back to UTF-8 and helps interpret this chunk's packed destination values.