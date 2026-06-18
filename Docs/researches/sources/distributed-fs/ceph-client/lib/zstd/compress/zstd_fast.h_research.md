<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h

## Purpose
`zstd_fast.h` declares the fast matchfinder API used by compression strategy dispatch and dictionary table loading.

## Important APIs, Types, and Functions
It declares `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`.

## Control Flow
Callers fill the hash table for a CCtx or CDict with `ZSTD_fillHashTable()`, then dispatch one of the block compressors depending on dictionary mode. All compressors receive `ZSTD_MatchState_t`, `SeqStore_t`, repeat-code history, source pointer, and source size.

## State and Persistence
The header owns no state. The declared implementation updates the match state's hash table, sequence store contents, and caller-held repeat offsets.

## Dependencies and Integration Points
It includes common memory types and `zstd_compress_internal.h`. It is consumed by the main block-compressor selector and other compression internals that need to prefill or run the fast parser.

## Risks
The API assumes `ms->hashTable`, window fields, and compression parameters are initialized for fast parsing. Calling the wrong variant for the active dictionary mode can produce invalid offsets.

## Test Signals
Compile tests should verify inclusion in kernel-style builds. Runtime coverage should exercise the no-dict, dictMatchState, and extDict functions via the `ZSTD_fast` strategy and verify round-trip correctness with reused contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h -->
