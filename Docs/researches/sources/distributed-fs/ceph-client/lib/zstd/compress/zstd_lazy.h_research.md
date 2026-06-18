# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.h

## Purpose

`zstd_lazy.h` is the internal header for the greedy/lazy family of Zstd block compressors. It publishes the block-compressor functions implemented in `zstd_lazy.c`, exposes dictionary/table update helpers used while loading dictionaries, and maps excluded compressor families to `NULL` so the central compressor selector can compile against one stable interface.

## Important APIs, Types, and Functions

The header defines `ZSTD_LAZY_DDSS_BUCKET_LOG`, the bucket multiplier for the dedicated dictionary search structure, and `ZSTD_ROW_HASH_TAG_BITS`, the number of tag bits used by row hashing. When any greedy/lazy/btlazy compressor family is enabled, it declares `ZSTD_insertAndFindFirstIndex()`, `ZSTD_row_update()`, `ZSTD_dedicatedDictSearch_lazy_loadDictionary()`, and `ZSTD_preserveUnsortedMark()`.

The main exported surface is grouped by strategy. The greedy group declares normal, row, dictionary match state, dedicated dictionary search, and external dictionary variants. The lazy and lazy2 groups declare the same broad set. The btlazy2 group declares normal, dictionary match state, and external dictionary variants because btlazy2 does not have the full dedicated dictionary/row suffix matrix here. Each group also defines `ZSTD_COMPRESSBLOCK_*` macros that resolve to the real function when enabled or `NULL` when a `ZSTD_EXCLUDE_*` build flag removes it.

## Control Flow

This header does not implement runtime control flow, but it controls compile-time dispatch. `ZSTD_selectBlockCompressor()` can use the `ZSTD_COMPRESSBLOCK_*` macros without scattering preprocessor conditionals through the compressor selection table. When a family is excluded, the macro becomes `NULL`, which preserves the selector layout while preventing references to missing functions.

## State and Persistence Behavior

All declared functions operate on caller-owned state. `ZSTD_MatchState_t` owns the persistent hash, chain, row, dictionary, and window tables. `SeqStore_t` receives generated sequences for the current block. `rep[ZSTD_REP_NUM]` stores the repeat-offset history across blocks. The header itself stores no state, but its macros determine which strategy functions may appear in dispatch state.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h`, so it is tightly coupled to internal compression types rather than the public Zstd API. It is consumed by `zstd_lazy.c` and by central compression code that selects block compressors. Dictionary-loading code uses `ZSTD_row_update()` and `ZSTD_dedicatedDictSearch_lazy_loadDictionary()` to prebuild matchfinder tables before block compression.

## Risks

The primary risks are interface drift and build-configuration mismatches. If an implementation is renamed or excluded without updating the macro matrix, compressor selection may call the wrong function or dereference `NULL`. The header also declares `ZSTD_preserveUnsortedMark()` even though its implementation is outside this file group; callers depend on that function to preserve binary-tree unsorted markers during index reduction. Constants such as `ZSTD_LAZY_DDSS_BUCKET_LOG` must remain synchronized with memory sizing and dedicated dictionary loading assumptions.

## Test Signals

Build tests should cover all combinations of `ZSTD_EXCLUDE_GREEDY_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_LAZY_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_LAZY2_BLOCK_COMPRESSOR`, and `ZSTD_EXCLUDE_BTLAZY2_BLOCK_COMPRESSOR`. Runtime tests should verify that strategy selection returns non-`NULL` functions only for enabled families and that dictionary-loading paths can call the helper declarations successfully.
