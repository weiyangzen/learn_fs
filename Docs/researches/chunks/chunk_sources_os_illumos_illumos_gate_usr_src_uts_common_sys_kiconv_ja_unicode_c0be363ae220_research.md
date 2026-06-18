# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_unicode_to_jis.h lines 1-7089

## Scope

This chunk covers the opening 7,089 lines of `kiconv_ja_unicode_to_jis.h`, an illumos kernel-only Japanese Unicode-to-JIS/EUC lookup header. It includes the license/header guard, kernel gating, dependencies, the `NODEST` alias, and nearly all `static const kiconv_ja_euc16_t` UCS-2 high-byte lookup blocks from block `00` through the beginning of block `E7`.

The chunk ends inside `kiconv_ja_ucs2_to_euc16_block_E7`; the final entries of that block, the high-byte block index, the EUC-JP-MS/CP932 compatibility macro, `#undef NODEST`, and closing preprocessor guards are outside this chunk.

## APIs And Exports

- Header identity: `_SYS_KICONV_JA_UNICODE_TO_JIS_H`.
- C++ compatibility: wraps declarations in `extern "C"` when compiled as C++.
- Dependencies: `<sys/kiconv.h>` and `<sys/kiconv_ja.h>`.
- Kernel-only scope: all conversion data in this chunk is inside `#ifdef _KERNEL`.
- Local macro: `NODEST` aliases `KICONV_JA_NODEST`, defined in adjacent context as `0xffff`.
- Static lookup data includes blocks `00`-`04`, `20`-`26`, `30`, `32`, `33`, `4E`-`9F`, `E0`-`E6`, and the start of `E7`.

## Control Flow And State

There is no executable function body in this chunk. Runtime flow is implied by table lookup: split UCS-2 into high/low bytes, select a high-byte block from the later index table, index by the low byte, and receive either an EUC/JIS-family 16-bit destination code or `NODEST`.

All arrays are `static const`, so they are immutable per-including-translation-unit data. There is no dynamic allocation, locking, mutable state, or per-conversion state here. Correctness depends on every complete block preserving exactly 256 positional entries.

## Dependencies And Integration

`kiconv_ja.h` supplies `KICONV_JA_NODEST`, Japanese table IDs used later, and `kiconv_ja_euc16_t` (`ushort_t`). The sibling `kiconv_ja_jis_to_unicode.h` contains reverse-direction mappings and MS-extension compatibility macros. `usr/src/uts/common/sys/Makefile` lists this header for installation/export.

A repository search found no direct in-tree textual consumer of the later index or macro outside this header, so use may be generated, external to the searched focus, or via installed kernel headers.

## Risks

- Unsized arrays make table length mistakes possible at compile time without an explicit 256-entry assertion.
- Any shifted initializer corrupts all later low-byte mappings in that block.
- `0xffff` must always be treated as the unmappable sentinel, not a valid output.
- `static const` tables in a header can duplicate storage across including objects.
- The chunk cannot validate the completed `E7` block or high-byte index correspondence.

## Cross-Chunk References

- Next chunk must finish `kiconv_ja_ucs2_to_euc16_block_E7`, then cover blocks `F9`, `FA`, and `FF`.
- Next chunk must cover `kiconv_ja_ucs2_to_euc16_index[]`.
- Next chunk must cover `KICONV_JA_CNV_U2_TO_EUCJPMS(id, e, u)`, the EUC-JP-MS/CP932 override macro.
- Merge should verify every complete block from this chunk is referenced at its exact high-byte slot and eliminated blocks are represented by `NULL`.