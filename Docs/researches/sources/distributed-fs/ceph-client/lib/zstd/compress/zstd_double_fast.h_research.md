<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h

## Purpose
`zstd_double_fast.h` declares the double-fast matchfinder API and compile-time exclusion shims.

## Important APIs, Types, and Functions
It declares `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()` when `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is not defined. It also defines `ZSTD_COMPRESSBLOCK_DOUBLEFAST*` macros to either the real functions or `NULL`.

## Control Flow
The compressor dispatcher includes this header and uses the macros to install function pointers for no-dict, attached-dictionary, and extDict double-fast compression. Table loading calls `ZSTD_fillDoubleHashTable()` with dictionary table load and table fill purpose modes.

## State and Persistence
The header owns no state. The functions it declares mutate `ZSTD_MatchState_t` tables, `SeqStore_t` output, and repeat offsets through caller-provided pointers.

## Dependencies and Integration Points
It includes common memory types and `zstd_compress_internal.h`. It is the interface between strategy dispatch and `zstd_double_fast.c`, and its `NULL` macros support builds that remove the double-fast compressor.

## Risks
Callers must handle `NULL` macro values when the implementation is excluded. Passing a match state without both long and small tables sized for double-fast would corrupt memory in the implementation.

## Test Signals
Compile tests should cover both normal and `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` builds. Runtime tests should verify dispatch to no-dict, dictMatchState, and extDict functions for the `dfast` strategy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h -->
