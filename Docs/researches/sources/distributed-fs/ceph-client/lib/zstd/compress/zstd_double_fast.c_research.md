<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c

## Purpose
`zstd_double_fast.c` implements the double-fast block matchfinder. It keeps both a long-match hash table and a small-match hash table, favoring speed while finding better matches than the single fast parser.

## Important APIs, Types, and Functions
When not excluded by `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR`, exported functions are `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. Internal variants include CDict/CCtx table fillers and generic no-dict, dictMatchState, and extDict compressors specialized by minimum match length through `ZSTD_GEN_DFAST_FN`.

## Control Flow
Fill functions populate `ms->hashTable` as the long table and `ms->chainTable` as the small table, using tagged short-cache entries for CDicts and normal indices for CCtx tables. The no-dict compressor probes repcode at `ip+1`, then long matches, then small matches, and for a small hit checks whether a long match at `ip+1` is better. After storing a sequence it performs complementary insertions near the match end and greedily consumes immediate repcode matches. DictMatchState mode probes prefix tables and attached dictionary tables with tag checks. ExtDict mode maps indices to either `base` or `dictBase` and counts matches across the dictionary/prefix boundary with `ZSTD_count_2segments()`.

## State and Persistence
The function updates match tables in `ZSTD_MatchState_t`, appends sequences and literals to `SeqStore_t`, and updates the caller's `rep[0..1]` history for the next block. Dictionary variants read but do not mutate attached dictionary match tables. It has no file-static mutable state.

## Dependencies and Integration Points
It depends on `zstd_compress_internal.h` for hashing, sequence storage, repeat-code handling, window boundaries, short-cache helpers, and match counting. It is selected by the block-compressor dispatcher for the `ZSTD_dfast` strategy unless excluded at compile time. The header maps the function pointers to `NULL` when excluded, allowing dispatch tables to omit the strategy implementation.

## Risks
The code relies on intentional pointer arithmetic near `iend - HASH_READ_SIZE`, unsigned index comparisons, dummy reads for branchless safety, and correct base selection for extDict. Short/long table synchronization and complementary insertions are performance-critical and correctness-sensitive. Repcode disabling/restoration must preserve history when offsets fall outside the current prefix.

## Test Signals
Tests should cover no-dict, extDict, and dictMatchState compression at minMatch 4 through 7; CDict table prefill and short-cache tags; excluded-build compilation; repeated immediate repcodes; long-vs-small match preference; window boundary invalidation; 32-bit and 64-bit builds; ASAN/fuzzer runs for end-of-block probes; and round trips for data crossing dictionary/prefix boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c -->
