# sources/compression/zstd/lib/compress/zstd_compress_internal.h

## Purpose
Defines the private compression-side ABI shared by `lib/compress` modules in zstd. It centralizes context state, match state, entropy table state, sequence storage, repeat-code conventions, workspace sizing constants, hash helpers, window/index maintenance, and private entry points used by streaming, dictionary, block, long-distance, and sequence-producer paths.

## Important APIs, Types, And Functions
Core state types include `ZSTD_CCtx_s`, `ZSTD_CCtx_params_s`, `ZSTD_MatchState_t`, `ZSTD_window_t`, `ZSTD_blockState_t`, `ZSTD_compressedBlockState_t`, `SeqStore_t`, `SeqDef`, `rawSeq`, `RawSeqStore_t`, `optState_t`, `ldmState_t`, `ldmParams_t`, and entropy table metadata/containers (`ZSTD_hufCTables_t`, `ZSTD_fseCTables_t`, `ZSTD_entropyCTables_t`, `ZSTD_entropyCTablesMetadata_t`). `ZSTD_BlockCompressor_f` defines the common block compressor signature, and `ZSTD_selectBlockCompressor()` is the dispatcher hook used by the main compressor to pick fast, double-fast, lazy, btlazy, optimal, or row-based implementations.

Sequence helpers encode zstd's sequence representation: `ZSTD_getSequenceLength()` expands `SeqDef` plus the single long-length side channel in `SeqStore_t`; `ZSTD_storeSeqOnly()` and `ZSTD_storeSeq()` append a match sequence and copy literals; `ZSTD_LLcode()` and `ZSTD_MLcode()` map raw lengths to entropy symbol codes. Repeat-code utilities define the offBase sum type: `REPCODE*_TO_OFFBASE`, `OFFSET_TO_OFFBASE()`, `OFFBASE_IS_OFFSET()`, `OFFBASE_TO_OFFSET()`, `OFFBASE_TO_REPCODE()`, `ZSTD_updateRep()`, and `ZSTD_newRep()`.

Window and index helpers are a large part of the file: `ZSTD_window_init()`, `ZSTD_window_update()`, `ZSTD_window_clear()`, `ZSTD_window_hasExtDict()`, `ZSTD_matchState_dictMode()`, `ZSTD_window_needOverflowCorrection()`, `ZSTD_window_correctOverflow()`, `ZSTD_window_enforceMaxDist()`, `ZSTD_checkDictValidity()`, `ZSTD_getLowestMatchIndex()`, `ZSTD_getLowestPrefixIndex()`, and `ZSTD_index_overlap_check()`. Hash helpers include fixed-size hashes for 3-8 byte match lengths, salted row-matchfinder hashes, rolling hashes for long-distance matching, and short-cache tag helpers `ZSTD_writeTaggedIndex()` and `ZSTD_comparePackedTags()`.

Private/public-internal declarations include entropy loading/reset (`ZSTD_loadCEntropy()`, `ZSTD_reset_compressedBlockState()`), sequence conversion/summary APIs, parameter derivation (`ZSTD_getCParamsFromCCtxParams()`, `ZSTD_getCParamsFromCDict()`), streaming/init entry points, deprecated internal wrappers, external sequence registration (`ZSTD_referenceExternalSequences()`), and tracing.

## Control Flow
This header does not own a full compression pipeline by itself, but its inline helpers run throughout every block compression call. A context is initialized with parameters, workspace, block state, sequence store, match state, optional dictionary/prefix, optional LDM state, and streaming buffers. The caller selects a block compressor via `ZSTD_selectBlockCompressor()`, the compressor fills `SeqStore_t` by calling `ZSTD_storeSeq()`, the entropy pipeline consumes the stored sequences and literals, and the repeat offsets and entropy tables are carried forward through `prevCBlock`/`nextCBlock`.

Window flow is index-based rather than pointer-persistent. `ZSTD_window_update()` appends a contiguous source segment or converts the previous prefix into an external dictionary when the source is non-contiguous. Before block compression, `ZSTD_window_enforceMaxDist()` or `ZSTD_checkDictValidity()` invalidates history outside the allowed window and drops attached dictionaries when they can no longer be referenced. When 32-bit indices approach `ZSTD_CURRENT_MAX`, `ZSTD_window_correctOverflow()` shifts `base`, `dictBase`, `lowLimit`, and `dictLimit` by a correction that preserves the low cycle bits used by hash/chain tables.

Sequence flow uses compact `SeqDef` fields and a single long-length escape in `SeqStore_t`. Literal bytes are copied into the literal buffer, while match lengths are stored as `mlBase = matchLength - MINMATCH`. Repeat-code updates follow zstd's special rules for zero-literal repeat matches via `ll0`.

## State And Persistence
All state is in-memory and context-scoped. `ZSTD_CCtx_s` persists requested/applied parameters, workspace ownership, source/destination byte counts, checksum state, block entropy state, repeat offsets, sequence buffers, match tables, LDM data, optional local dictionary buffers, streaming input/output buffers, and external sequence buffers across calls as required by simple or streaming APIs. `ZSTD_MatchState_t` persists hash/chain tables, row-matchfinder caches, dictionary match-state references, `nextToUpdate`, lazy-skipping settings, and dictionary validity boundaries. `ZSTD_window_t` persists the base referential and low/dictionary limits that make stored U32 indices meaningful.

The file also defines persistence rules for reusable entropy: `prevCBlock` and `nextCBlock` carry Huffman/FSE tables and repeat offsets across blocks; literal/FSE repeat modes determine whether new tables, default tables, or previous tables are used.

## Dependencies And Integration Points
The header depends on common zstd internals (`zstd_internal.h`, `bits.h`, `mem.h` through transitive includes), the compression workspace allocator (`zstd_cwksp.h`), optional multithreaded compression (`zstdmt_compress.h`), and block splitting workspace sizing (`zstd_preSplit.h`). It is included by the concrete compressors, literal/sequence/superblock encoders, dictionary builder paths, and some benchmark/decode-corpus utilities that need sequence conversion.

Integration is broad: fast and double-fast compressors use hash, count, repeat, sequence, and window helpers; entropy encoders use `SeqStore_t` and entropy table types; superblock code uses entropy metadata and `ZSTD_getSequenceLength()`; main compression code owns the declared private entry points.

## Risks And Edge Cases
The main risks are invariant drift and undefined behavior around pointer/index arithmetic. Many helpers intentionally allow pointer overflow attributes and depend on U32 index correction, power-of-two distances, and contiguous/non-contiguous source detection. Sequence storage assumes the caller allocated enough literal and sequence capacity and that at most one long literal or match length needs the side channel. Repeat-code handling is subtle when a zero-literal match changes the repcode interpretation.

Dictionary validity is another high-risk area: `loadedDictEnd`, `dictLimit`, `lowLimit`, and `dictMatchState` must be invalidated together or stale dictionary references can survive beyond the window. Short-cache tagged indices pack tag bits into hash table entries and require index high bits to be clear. Inline assembly in `ZSTD_selectAddr()` is x86-64-specific and relies on fallback behavior elsewhere.

## Test Signals
Useful tests include compression/decompression round trips across simple, streaming, dictionary, prefix, ext-dict, attached CDict, and external-sequence modes; fuzzing with `ZSTD_WINDOW_OVERFLOW_CORRECT_FREQUENTLY`; ASAN/UBSAN/MSAN runs for sequence/literal buffers and workspace reuse; tests that force non-contiguous input segments and dictionary invalidation; tests with very long literal or match lengths; and corpus comparisons that verify compressed output remains decodable and ratio-sensitive after changes to match or repeat-code logic.
