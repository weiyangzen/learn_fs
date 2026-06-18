# sources/compression/zstd/lib/compress/zstd_compress.c lines 1-6006

## Scope And Purpose

This chunk covers the front 6,006 lines of zstd's main compression implementation. It owns most single-threaded `ZSTD_CCtx` and `ZSTD_CDict` lifecycle logic, compression parameter plumbing, workspace sizing and reset, dictionary loading, block sequence generation, entropy selection, frame/block emission, one-shot compression APIs, digested-dictionary APIs, and the first streaming-context setup helpers.

The code is the integration hub between public APIs from `zstd.h`, internal workspace management, strategy-specific match finders, long-distance matching, external sequence producers, literal/FSE entropy encoders, and frame-format writers. Later lines in the same file continue the streaming state machine and sequence-conversion APIs; this chunk ends just after `ZSTD_resetCStream()`.

## Important APIs, Types, And Data

`ZSTD_CCtx` is the mutable compression context. This chunk creates, initializes, resets, sizes, and frees it through `ZSTD_createCCtx()`, `ZSTD_createCCtx_advanced()`, `ZSTD_initStaticCCtx()`, `ZSTD_freeCCtx()`, `ZSTD_sizeof_CCtx()`, `ZSTD_CCtx_reset()`, and the `ZSTD_CStream` aliases. The context persists requested parameters, applied parameters, workspace allocations, sequence stores, entropy state, match state, dictionary references, streaming stage, pledged source size, produced/consumed counters, checksum state, and optional tracing state.

`ZSTD_CCtx_params` carries requested compression, frame, LDM, buffering, block-splitting, row-matchfinder, external-sequence, and dictionary-attachment preferences. The public setters/getters are `ZSTD_CCtxParams_init*()`, `ZSTD_CCtxParams_setParameter()`, `ZSTD_CCtxParams_getParameter()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_getParameter()`, and bulk setters for `ZSTD_parameters`, `ZSTD_compressionParameters`, and `ZSTD_frameParameters`.

`ZSTD_CDict_s` is defined here as a digested dictionary: original dictionary content or owned copy, entropy workspace, `ZSTD_cwksp`, prepared `ZSTD_MatchState_t`, compressed block state, custom allocator, dict ID, selected compression level, and row-matchfinder mode. Public dictionary entry points include `ZSTD_createCDict*()`, `ZSTD_initStaticCDict()`, `ZSTD_freeCDict()`, `ZSTD_sizeof_CDict()`, `ZSTD_getCParamsFromCDict()`, and `ZSTD_getDictID_fromCDict()`.

Key internal state structures used through this chunk are `ZSTD_MatchState_t`, `ZSTD_compressedBlockState_t`, `ZSTD_blockState_t`, `SeqStore_t`, `RawSeqStore_t`, `SeqCollector`, `Repcodes_t`, `ZSTD_entropyCTables_t`, and `ZSTD_entropyCTablesMetadata_t`. They hold matchfinder tables, rolling window coordinates, repeat offsets, pending literals and sequences, and reusable Huffman/FSE tables.

Important configuration helpers include `ZSTD_cParam_getBounds()`, `ZSTD_checkCParams()`, `ZSTD_adjustCParams_internal()`, `ZSTD_getCParamsFromCCtxParams()`, `ZSTD_makeCCtxParamsFromCParams()`, `ZSTD_resolveRowMatchFinderMode()`, `ZSTD_resolveBlockSplitterMode()`, `ZSTD_resolveEnableLdm()`, `ZSTD_resolveMaxBlockSize()`, and `ZSTD_resolveExternalRepcodeSearch()`.

Main compression APIs in this range are `ZSTD_compressBegin*()`, `ZSTD_compressContinue()`, `ZSTD_compressBlock()`, `ZSTD_compressEnd()`, `ZSTD_compress_advanced()`, `ZSTD_compress_usingDict()`, `ZSTD_compressCCtx()`, `ZSTD_compress()`, `ZSTD_compress_usingCDict*()`, `ZSTD_writeSkippableFrame()`, and `ZSTD_writeLastEmptyBlock()`. Sequence-collection APIs include `ZSTD_sequenceBound()`, `ZSTD_generateSequences()`, and `ZSTD_mergeBlockDelimiters()`.

## Control Flow

Context creation flows through allocation, zeroing, CPU BMI2 detection, and `ZSTD_CCtx_reset(..., ZSTD_reset_parameters)`. Static contexts reserve fixed object space inside caller-provided memory and cannot resize or own copied dictionaries. Freeing clears local/prefix/CDict references, frees multithread state when enabled, and releases the workspace unless the context itself lives inside it.

Parameter flow is staged. Setters first enforce bounds and stage rules, then update `requestedParams`. Some parameters are update-authorized mid-stream by setting `cParamsChanged`, but most require `zcss_init`. Initialization finalizes auto modes: row matchfinder, LDM, post-block splitter, max block size, and external repcode search. Compression parameters are adjusted to source size, dictionary size, attach-vs-copy mode, excluded compressor macros, short-cache limits, and row-hash bit limits.

Workspace reset is centered on `ZSTD_resetCCtx_internal()`. It copies finalized params into `appliedParams`, adjusts LDM, computes window/block sizes, estimates memory, resizes dynamic workspaces when too small or wasteful, resets or preserves match indexes according to overflow/dictionary conditions, reserves match tables, sequence buffers, LDM tables, external-sequence buffers, literal buffers, and optional streaming input/output buffers, then resets frame counters and block state.

Dictionary setup has three main paths. A local raw/full dictionary can be stored by reference or copy, then digested on first use. A `ZSTD_CDict` can be attached in-place for small/unknown inputs or forced attach, letting the working match state point at the CDict match state. Otherwise the CDict tables are copied into the working context, with short-cache tags stripped when needed. `ZSTD_compress_insertDictionary()` dispatches between raw-content loading and full zstd dictionary parsing.

Block compression starts by updating the window and optional LDM window in `ZSTD_compressContinue_internal()`. Frame mode writes a frame header on the first call, chunks input into block-sized slices in `ZSTD_compress_frameChunk()`, corrects index overflow, enforces max distance, then chooses target compressed-block-size, post-sequence block splitting, or normal block compression.

Sequence generation in `ZSTD_buildSeqStore()` selects one of four producers: external raw sequences already referenced on the context, LDM-generated sequences, an external sequence producer callback, or the built-in strategy compressor selected by `ZSTD_selectBlockCompressor()`. The selected path fills `SeqStore_t`, updates repeat offsets, appends last literals, and validates match lengths in debug builds.

Entropy compression converts sequence fields to literal-length, offset, and match-length codes with `ZSTD_seqToCodes()`, compresses literals through `ZSTD_compressLiterals()`, selects FSE encoding types for each sequence alphabet, builds C tables, writes sequence headers, and encodes sequences. Blocks that do not beat min-gain thresholds, run out of bounded space, or hit old-decoder edge cases fall back to raw or RLE blocks.

Frame completion flows through `ZSTD_writeEpilogue()`: it writes an empty last block if needed, appends the optional XXH64-derived 32-bit checksum, returns the stage to created, and validates pledged source size in `ZSTD_compressEnd_public()`.

## State And Persistence Behavior

`requestedParams` persist across compressions until reset with `ZSTD_reset_parameters` or `ZSTD_reset_session_and_parameters`. `appliedParams` are the finalized per-frame/session copy and may differ because auto modes, LDM, cParam adjustment, or dictionary attachment/copy decisions have been resolved.

The workspace (`ZSTD_cwksp`) persists between sessions for reuse. Dynamic contexts resize it; static contexts fail if the reserved memory is insufficient. Table cleanliness is tracked so match tables can be left dirty when they will be overwritten by a copied CDict, then marked clean after copy/reduction. MemorySanitizer hooks deliberately poison/unpoison reused table memory in the reduce path.

Match state persists indexes across context reuse unless overflow, large dictionary load, first initialization, or workspace resize forces an index reset. `ZSTD_overflowCorrectIfNeeded()` reduces table indexes and clears dictionary attachment when 32-bit positions approach overflow. `ZSTD_window_update()`, `ZSTD_window_enforceMaxDist()`, and loaded-dictionary markers maintain the active history window.

Entropy state persists from block to block through `prevCBlock` and `nextCBlock`. Successful compressed blocks swap them with `ZSTD_blockState_confirmRepcodesAndEntropyTables()`. Raw and RLE blocks reset simulated decompression repcode history for partitioned block-split output and may leave FSE repeat modes in `FSE_repeat_check`.

Dictionary state can be owned or borrowed. `ZSTD_CCtx_loadDictionary()` copies into `localDict.dictBuffer`, while by-reference and prefix APIs require caller lifetime stability. `ZSTD_CDict` may own a copied dictionary in its workspace or refer to caller memory, depending on load method. `ZSTD_clearAllDicts()` frees local owned buffers and local CDicts, clears prefix state, and drops the attached CDict pointer.

Frame progress counters (`consumedSrcSize`, `producedCSize`, `pledgedSrcSizePlusOne`) are updated per continue call and validated against pledged sizes. `xxhState` persists across frame chunks only when checksum output is enabled. Optional `traceCtx` persists across a frame and is closed in `ZSTD_CCtx_trace()`.

## Dependencies And Integration Points

This file depends directly on common allocation, memory, error, FSE, HUF, bit, and CPU helpers, plus compression internals from `zstd_compress_internal.h`, literal/sequence encoders, strategy compressors (`zstd_fast`, `zstd_double_fast`, `zstd_lazy`, `zstd_opt`), long-distance matching, superblock compression, and pre-splitting.

Strategy dispatch integrates with per-strategy compressors through `ZSTD_selectBlockCompressor()`. It selects normal, ext-dict, dict-match-state, dedicated-dictionary-search, or row-matchfinder function tables based on `ZSTD_strategy`, dictionary mode, and resolved row mode.

Dictionary integration spans zstd dictionary format parsing (`ZSTD_MAGIC_DICTIONARY`, entropy tables, repcodes, dict ID), raw-content dictionaries, CDict attach/copy heuristics, dedicated dictionary search, short-cache tagged indices, and LDM dictionary loading. Frame header generation integrates dictionary ID and frame parameter flags into the wire format.

Sequence integration includes internal `SeqStore_t` encoding, public `ZSTD_Sequence` collection, block delimiter insertion/merging, external sequence producer callback support, and conversion from repcode-relative offsets to raw offsets for exported sequences or partition repair.

Multithread integration in this chunk is mostly parameter bounds, size/progression delegation, static-context rejection for workers, and thread-pool references. Actual MT compression is outside this line range under `ZSTD_MULTITHREAD`.

Public API integration is broad: one-shot APIs allocate or reuse contexts, advanced APIs share the same begin/continue/end core, CDict APIs reuse the same reset and dictionary-insertion machinery, and CStream creation/free/size/reset are aliases or wrappers around CCtx behavior at the end of the chunk.

## Risks And Edge Cases

Stage rules are critical. Many setters, dictionary loads, prefix references, and resets are only legal in init stage; missing a stage guard can corrupt active stream state or change parameters after workspace/table sizes have already been selected.

Workspace sizing must match actual reservations. Underestimation can cause allocation failure or memory overwrite; overestimation can waste memory and trigger unnecessary dynamic reallocations. Static contexts are especially sensitive because they cannot resize and cannot copy dictionaries internally.

Auto-parameter resolution has subtle compatibility effects. Row matchfinder, LDM, post-block splitting, max block size, external repcode search, source-size hints, and CDict attach mode all affect table sizes and selected compressors. Mismatches between estimation, reset, and compressor selection can yield invalid table pointers or poor compression.

Dictionary handling is high risk. Full dictionaries must reject corrupt entropy tables, zero/too-large repcodes, and impossible offset alphabets. Very large dictionaries are truncated to avoid 32-bit index overflow and short-cache tag overlap. Attached dictionaries require adjacency assumptions; max-distance enforcement intentionally avoids attached dicts when `forceWindow` is set.

Repeat-offset history is fragile around raw/RLE blocks and block splitting. The split-block path simulates compression and decompression repcode histories separately and rewrites invalid repcodes to raw offsets when needed. Incorrect handling can produce streams that compress successfully but fail to decompress.

External sequence producers can return invalid counts, missing block delimiters, impossible length sums, or unsupported combinations with LDM. The fallback flag changes whether errors propagate or silently fall back to the built-in matchfinder.

Compatibility workarounds should be preserved: avoiding first-block RLE for old CLI decoders, avoiding tiny compressed sequence payloads that old decoders misread, and keeping compressed block sizes below legacy decoder limits.

Overflow correction and table reduction are correctness-sensitive. Index correction must update hash, chain, and hash3 tables while preserving special binary-tree unsorted marks. It must also invalidate dictionary state and adjust `nextToUpdate` consistently.

The chunk boundary matters for research merging: streaming initialization continues after line 6006, so this document should not be treated as a complete account of `ZSTD_compressStream2()` or sequence-conversion APIs later in the file.

## Test Signals

Core signals are zstd round-trip tests across levels, strategies, source sizes, and buffer alignments, including empty input, one-byte input, tiny blocks below `MIN_CBLOCK_SIZE`, exact block-size inputs, multi-block inputs, incompressible data, RLE data, and highly compressible repeated data.

Parameter tests should cover every `ZSTD_cParameter` setter/getter, boundary clamping, unsupported MT parameters in non-MT builds, stage-wrong errors during active compression, reset directives, `srcSizeHint`, `maxBlockSize`, row-matchfinder auto/enable/disable, LDM auto/enable, block splitter, target compressed block size, and magicless frame format.

Dictionary tests should include raw and full dictionaries, by-copy and by-reference lifetimes, prefixes, CDict attach vs copy vs force-load/force-attach/force-copy, static CDict/CCtx memory sizing, corrupt dictionary entropy, zero or oversized repcodes, large dictionary truncation, short-cache strategies, dedicated dictionary search, and `noDictIDFlag` frame behavior.

Block and entropy tests should compare compressed output validity and decompressed bytes for normal, raw, RLE, split-block, superblock/target-size, repeated entropy-table, and no-literal-compression cases. Regression tests should include old-decoder compatibility edge cases around first-block RLE and very small sequence bitstreams.

Sequence API tests should verify `ZSTD_generateSequences()` bounds, block delimiters, long literal/match lengths, repcode export, delimiter merging, external sequence producer success and failure, fallback enabled/disabled, and invalid external length sums.

State reuse tests should repeatedly compress many small inputs with one context, force index-overflow correction with large cumulative input, copy contexts with `ZSTD_copyCCtx()`, reset sessions with and without parameter resets, and validate `ZSTD_getFrameProgression()` counters.

Memory and sanitizer signals should include ASAN/MSAN/UBSAN builds, static allocation size estimates versus actual initialization, custom allocator failure injection, `ZSTD_COMPRESS_HEAPMODE` stack/heap variants, and builds with selected strategy compressors excluded by preprocessor macros.

Frame-format tests should inspect frame headers for content size, checksum, dict ID, single-segment/window descriptor, magicless format, skippable frames, last empty blocks, and pledged-size mismatch errors at both continue-time and end-time.
