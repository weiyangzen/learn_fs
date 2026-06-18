# Research: sources/distributed-fs/ceph-client/fs/nls/nls_euc-jp.c

## Purpose

This file implements the Linux NLS table for Japanese `euc-jp` by translating through the existing `cp932` table. It is not a generated Unicode mapping table by itself; it is a conversion adapter that maps EUC-JP byte sequences to Shift-JIS/CP932 byte sequences, calls the loaded CP932 NLS callbacks, and maps CP932 output back to EUC-JP. The implementation includes support for JIS X 0208, JIS X 0201 kana, user-defined characters, IBM extensions, and NEC/IBM extension remapping according to the referenced OSF/JVC EUC/SJIS conversion specification.

## Important APIs, Types, and Functions

The module-level dependency is `static struct nls_table *p_nls`, loaded with `load_nls("cp932")` during init. The registered `struct nls_table table` exposes `.charset = "euc-jp"`, `.uni2char`, and `.char2uni`; the case-folding tables are borrowed from the CP932 table.

Key macros classify and translate byte ranges: `IS_SJIS_LOW_BYTE`, `IS_SJIS_JISX0208`, `IS_SJIS_JISX0201KANA`, `IS_SJIS_UDC_LOW`, `IS_SJIS_UDC_HI`, `IS_SJIS_IBM`, `IS_SJIS_NECIBM`, `MAP_SJIS2EUC`, `SS2`, `SS3`, `IS_EUC_BYTE`, `IS_EUC_JISX0208`, `IS_EUC_JISX0201KANA`, `IS_EUC_UDC_LOW`, `IS_EUC_UDC_HI`, and `MAP_EUC2SJIS`.

Static tables `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` handle IBM extension areas that are not simple arithmetic transforms. Helper functions `sjisibm2euc()`, `euc2sjisibm_jisx0212()`, `euc2sjisibm_g3upper()`, `euc2sjisibm()`, and `sjisnec2sjisibm()` isolate those special cases.

## Control Flow

`uni2char()` first delegates Unicode-to-CP932 conversion to `p_nls->uni2char()`. One-byte CP932 kana output is expanded to `SS2` plus kana. Two-byte output is optionally normalized from NEC/IBM extension rows to IBM extension rows, then transformed into EUC-JP: user-defined low rows map arithmetically, user-defined high rows become a three-byte `SS3` sequence, IBM extensions are table-mapped to two or three bytes, and ordinary JIS X 0208 rows use the standard SJIS-to-EUC arithmetic conversion. Unrecognized two-byte CP932 output returns `-EINVAL`.

`char2uni()` performs the inverse. ASCII bytes pass through as JIS X 0201 Roman. EUC two-byte sequences are decoded as kana, user-defined low rows, or JIS X 0208. `SS3` three-byte sequences handle high user-defined rows and IBM extension tables; other JIS X 0212-like input is rejected. After translating to a temporary CP932 byte sequence, the function calls `p_nls->char2uni()` and returns the number of EUC bytes consumed.

## State and Persistence Behavior

The file has one persistent module reference, `p_nls`, which is loaded at init and unloaded at exit. Static mapping tables are read-only. There is no per-mount mutable state, but conversion behavior is persistent for any filesystem using the `euc-jp` NLS table, so mapping changes affect filename interoperability.

## Dependencies and Integration Points

The file depends on the Linux NLS core, errno values, module lifecycle macros, and the CP932 NLS module. `init_nls_euc_jp()` loads CP932, borrows its case tables, and calls `register_nls()`. `exit_nls_euc_jp()` unregisters EUC-JP and unloads CP932. Filesystems interact only through the generic `struct nls_table` callbacks.

## Risks

The main risk is semantic drift in the many byte-range formulas and extension tables. Off-by-one errors in index calculations can remap large ranges. `sjisibm2euc()` computes an array index from lead/trail bytes and relies on callers to restrict inputs to IBM ranges. `char2uni()` returns `-EINVAL` rather than `-ENAMETOOLONG` for some truncated multibyte paths, which is observable behavior. Changes must preserve CP932 dependency handling so the borrowed case tables remain valid.

## Test Signals

Build the module with CP932 enabled, load/unload it, and verify `register_nls("euc-jp")` succeeds only when CP932 is available. Conversion tests should cover ASCII, JIS X 0201 kana, JIS X 0208 punctuation/kana/kanji, `SS3` high user-defined rows, IBM extensions from both G3 upper and JIS X 0212 maps, NEC/IBM special rows, invalid lead/trail bytes, and truncated two- and three-byte sequences.
