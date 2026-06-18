<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c

## Purpose
`zstd_fast.c` implements the single-hash-table fast block matchfinder. It prioritizes throughput using pipelined hash lookups, simple skip acceleration, and greedy repcode handling.

## Important APIs, Types, and Functions
Exported functions are `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. Internal helpers include CDict/CCtx hash table fillers, `ZSTD_match4Found_cmov()`, `ZSTD_match4Found_branch()`, and generic no-dict/dictMatchState/extDict compressors specialized by minimum match length and branch/cmov mode through `ZSTD_GEN_FAST_FN`.

## Control Flow
Hash-table fill inserts every third position and optionally fills empty intermediate positions; CDict mode stores packed short-cache tags, while CCtx mode stores plain indices. The no-dict compressor pipelines hash, table lookup, match load, and compare across adjacent candidate positions, periodically increasing step size for incompressible regions. It first checks repcode candidates, then hash candidates, counts backward and forward match length, stores sequences, inserts near match boundaries, and consumes immediate repeat matches. DictMatchState mode probes local and attached-dictionary tables, using dictionary tags to avoid many remote loads. ExtDict mode resolves candidates against `dictBase` or `base`, falls back to no-dict when the dictionary is invalidated, and uses two-segment counting for cross-boundary matches.

## State and Persistence
The function mutates `ms->hashTable`, appends to `SeqStore_t`, and updates `rep[0]`/`rep[1]` for subsequent blocks. It reads `ZSTD_MatchState_t.window`, `cParams`, `dictMatchState`, and prefetch settings. It has no persistent global state.

## Dependencies and Integration Points
It depends on internal hash functions, `ZSTD_storeSeq()`, `ZSTD_count()`, `ZSTD_count_2segments()`, repcode macros, window low-index helpers, short-cache tag helpers, and CPU/prefetch macros. It is selected for the `ZSTD_fast` strategy by the compressor dispatcher and supports prefix, external dictionary, and attached CDict modes.

## Risks
The implementation is built around deliberate speculative reads guarded by index checks or dummy addresses, so boundary conditions are high risk. Cmov vs branch selection changes generated code and performance. Repcode invalidation/restoration is subtle when old offsets are outside the current prefix. DictMatchState tries to mimic extDict parse behavior by preferring dictionary matches only when local matches are invalid; changing this can alter compressed output and ratio.

## Test Signals
Tests should cover minMatch 4 through 7, small blocks near `HASH_READ_SIZE`, incompressible skip acceleration, repcode-only matches, prefix and non-contiguous extDict windows, attached CDicts with short-cache tags and prefetching, invalidated dictionaries, branch/cmov behavior on different window logs, ASAN/fuzzer boundary checks, and round-trip determinism for repeated context reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c -->
