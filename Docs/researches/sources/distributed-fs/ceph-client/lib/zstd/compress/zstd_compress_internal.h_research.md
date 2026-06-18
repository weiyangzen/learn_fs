<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h

## Purpose
`zstd_compress_internal.h` is the private compression spine for this Zstd copy. It defines compressor context state, match/window state, sequence storage, entropy table metadata, hash helpers, repeat-offset helpers, block/raw encoders, and private function declarations used by the compressor implementation and nearby dictionary/benchmark code.

## Important APIs, Types, and Functions
Key types include `ZSTD_CCtx_s`, `ZSTD_CCtx_params_s`, `ZSTD_MatchState_t`, `ZSTD_window_t`, `SeqStore_t`, `SeqDef`, `rawSeq`, `RawSeqStore_t`, `ZSTD_compressedBlockState_t`, `ZSTD_entropyCTables_t`, `ZSTD_entropyCTablesMetadata_t`, `ldmState_t`, `ldmParams_t`, `optState_t`, and `ZSTD_blockSplitCtx`. Important helpers are `ZSTD_getSequenceLength()`, `ZSTD_LLcode()`, `ZSTD_MLcode()`, `ZSTD_noCompressBlock()`, `ZSTD_rleCompressBlock()`, `ZSTD_minGain()`, `ZSTD_literalsCompressionIsDisabled()`, `ZSTD_storeSeqOnly()`, `ZSTD_storeSeq()`, `ZSTD_updateRep()`, `ZSTD_newRep()`, `ZSTD_count()`, `ZSTD_count_2segments()`, `ZSTD_hashPtr()`, `ZSTD_hashPtrSalted()`, rolling-hash helpers, `ZSTD_window_*()` maintenance helpers, `ZSTD_matchState_dictMode()`, and short-cache helpers `ZSTD_writeTaggedIndex()`/`ZSTD_comparePackedTags()`.

## Control Flow
Compressor front ends select block compressors through `ZSTD_selectBlockCompressor()` and use the context fields declared here to hold requested/applied params, window state, block entropy states, sequence stores, temporary workspace, dictionaries, streaming buffers, and external sequence producer buffers. Matchfinders append matches with `ZSTD_storeSeq()`, which copies literals into `SeqStore_t`, records long literal or match lengths through `longLengthType`, and emits `offBase` values in the repeat-code/full-offset sum type. Entropy and block writers later consume the same sequence/literal/code arrays.

## State and Persistence
`ZSTD_CCtx_s` persists across calls and contains reusable workspace allocations, previous/next block entropy, repeat offsets, streaming positions, dictionary references, pledged/consumed/produced byte counts, checksum state, and table-backed match state. `ZSTD_window_t` persists pointer bases and 32-bit indices; overflow correction adjusts `base`, `dictBase`, `lowLimit`, and `dictLimit` while preserving hash/chain cycle bits. `ZSTD_MatchState_t` persists hash tables, chain tables, dictionary match state links, LDM input, row-cache fields, and parser behavior flags.

## Dependencies and Integration Points
This header depends on common Zstd internals, bits, workspace allocation, and block pre-splitting. It is included by fast/double-fast matchfinders, literal/sequence/superblock encoders, lazy/optimal paths outside this work item, and dictionary builder code. The declarations for `ZSTD_buildBlockEntropyStats()`, `ZSTD_loadCEntropy()`, streaming init, advanced compression, external sequences, and deprecated internal wrappers connect private compressor modules to the public API layer and optional multithreaded compression.

## Risks
The highest-risk areas are pointer/index arithmetic around `base`, `dictBase`, `lowLimit`, and `dictLimit`; repeat-code translation for zero-literal sequences; one-long-length representation in `SeqStore_t`; intentional unsigned underflow checks; and wildcopy literal copying near block ends. Overflow correction requires table users to apply the returned correction consistently. External sequences are explicitly unverified and can cause out-of-bounds access if invalid.

## Test Signals
Useful tests cover no-dict, prefix-dict, ext-dict, attached CDict, dictionary invalidation after window distance, index overflow correction, first-block determinism, raw/RLE block fallback, long literal and match lengths above 64 KiB, zero-literal repcode updates, external sequence validation/fallback behavior, 32-bit builds, fuzzing with frequent overflow correction, and ASAN/MSAN/UBSAN runs around wildcopy and two-segment matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h -->
