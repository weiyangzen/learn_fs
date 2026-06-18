# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 1-8428

## Scope And Role

This chunk is the first 8,428 lines of the oversized kernel header `kiconv_euctw_utf8.h`. It contains the license/header guard, kernel-only macro declarations for CNS 11643 plane table sizes, the complete CNS plane #1 to UTF-8 mapping table, and the first 2,464 entries of the CNS plane #2 to UTF-8 mapping table. The file documents that the mapping source is Unicode 3.2 / `Unihan-3.2.0.txt`.

The chunk is data, not executable logic. It provides file-scope `static kiconv_table_array_t` arrays for EUC-TW/CNS-to-UTF-8 conversion code that can include this header in a kernel build.

## Visible APIs And Data

- Header guard: `_SYS_KICONV_EUCTW_UTF8_H`.
- Kernel gate: all conversion declarations in this chunk are inside `#ifdef _KERNEL`.
- Plane size macros visible at lines 78-85 include `KICONV_CNS1_UTF8_MAX = 5868` and `KICONV_CNS2_UTF8_MAX = 7651`, plus plane #3, #4, #5, #6, #7, and #15 sizes.
- `static kiconv_table_array_t kiconv_cns1_utf8[]` starts at line 92 and is complete in this chunk.
- `static kiconv_table_array_t kiconv_cns2_utf8[]` starts at line 5964 and continues beyond this chunk.

Each table row maps a CNS/EUC-TW two-byte key to a UTF-8 byte array. Both visible arrays begin with key `0x0000` mapped to UTF-8 replacement character bytes `{ 0xEF, 0xBF, 0xBD }`.

## Control Flow

There are no functions, branches, loops, or conversion routines in this chunk. Runtime behavior is indirect: conversion code is expected to select a plane table, search or index by `key`, and emit the populated UTF-8 bytes from `u8`.

The visible tables are `static` definitions in a header, so any translation unit including it under `_KERNEL` receives private table storage.

## State And Dependencies

The arrays are mutable static data, though they appear intended as generated immutable mapping tables. They depend on `kiconv_table_array_t` from `kiconv_cck_common.h`, which stores a `uint32_t key` and `uchar_t u8[4]`.

Related visible integration points include EUC-TW validation macros in `kiconv_tc.h`, `euctw` code-name registration in `kiconv.c`, and installation/export listing in `usr/src/uts/common/sys/Makefile`. A repository search found no direct C include/reference to `kiconv_cns1_utf8` or `kiconv_cns2_utf8` outside this header.

## Risks And Cross-Chunk References

- Plane #1 has 5,868 rows, matching `KICONV_CNS1_UTF8_MAX`; plane #2 cannot be fully validated until later chunks.
- `kiconv_cns2_utf8[]` continues after line 8428 through its close at line 13616.
- Rows with two-byte UTF-8 sequences rely on zero-initialized trailing bytes in `uchar_t u8[4]`.
- The arrays are not `const`, increasing writable kernel data footprint and accidental mutation risk.
- Later chunks contain the rest of plane #2, planes #3/#4/#5/#6/#7/#15, and closing preprocessor guards.
- Whole-file merge should verify every `KICONV_CNS*_UTF8_MAX` macro against completed array counts.