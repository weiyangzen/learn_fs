# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.h

## Purpose

`zstd_opt.h` is the internal declaration header for the optimal-parser block compressors. It provides the enabled/disabled macro surface used by compressor dispatch and declares `ZSTD_updateTree()` for dictionary-table preparation.

## Important APIs, Types, and Functions

When bt/lazy or optimal families are enabled, `ZSTD_updateTree()` is declared for `ZSTD_loadDictionaryContent()` and related setup code. The btopt group declares normal, dictionary match state, and external dictionary variants and maps `ZSTD_COMPRESSBLOCK_BTOPT*` macros to those functions or `NULL`. The btultra group declares normal, dictionary match state, external dictionary, and btultra2 variants and maps `ZSTD_COMPRESSBLOCK_BTULTRA*` macros similarly.

## Control Flow

The header has compile-time control flow only. It centralizes `ZSTD_EXCLUDE_BTOPT_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_BTULTRA_BLOCK_COMPRESSOR`, and `ZSTD_EXCLUDE_BTLAZY2_BLOCK_COMPRESSOR` conditionals so the compressor selector can use one macro name for each strategy slot. It also documents that btultra2 has no extDict or dictMatchState variant because it is intended only for the first block without dictionaries or prefix history.

## State and Persistence Behavior

The declared functions mutate `ZSTD_MatchState_t`, `SeqStore_t`, and `rep[]`, but the header stores no runtime state. Macro values affect dispatch-table state by making disabled compressor slots `NULL`.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h` for internal type definitions. It is consumed by `zstd_opt.c`, dictionary-loading code that needs `ZSTD_updateTree()`, and central block-compressor selection. It must remain synchronized with `zstd_opt.c` exports and with the strategy enum support in compressor parameters.

## Risks

The main risks are build matrix drift and unsupported dispatch. If macros are wrong, a strategy can become selectable while its implementation is excluded, or a valid implementation can be hidden as `NULL`. The comment indentation around btultra2 is harmless but makes the special-case contract easy to miss.

## Test Signals

Build tests should compile with btopt excluded, btultra excluded, and both enabled. Runtime selection tests should verify that `ZSTD_btopt`, `ZSTD_btultra`, and `ZSTD_btultra2` map to non-`NULL` functions only when compiled in, and that dictionary modes never request a btultra2 variant.
