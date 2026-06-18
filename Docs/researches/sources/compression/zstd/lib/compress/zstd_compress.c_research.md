# Research: sources/compression/zstd/lib/compress/zstd_compress.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000312`: lines 1-6006, `Docs/researches/chunks/subset-b-000312_research.md`
- `subset-b-000313`: lines 6007-8370, `Docs/researches/chunks/subset-b-000313_research.md`

## Chunk Research

### subset-b-000312: lines 1-6006

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

### subset-b-000313: lines 6007-8370

# sources/compression/zstd/lib/compress/zstd_compress.c lines 6007-8370

## Scope

This chunk covers the streaming compression front end, one-shot compression through `compressStream2()`, the experimental sequence ingestion APIs, the architecture-specific conversion helpers for public `ZSTD_Sequence` arrays, stream flush/end wrappers, predefined compression-level parameter selection, and external sequence producer registration.

It starts at `ZSTD_initCStream_internal()` after the CStream creation helpers, and ends at `ZSTD_CCtxParams_registerSequenceProducer()`. The chunk is a bridge between public or semi-public APIs in `zstd.h` and lower-level frame/block compression helpers defined earlier in `zstd_compress.c`.

## Purpose

The main purpose of this range is to turn user-facing compression calls into initialized `ZSTD_CCtx` state and then drive block-by-block frame production. It supports three related entry styles:

- Legacy streaming setup with `ZSTD_initCStream*()` followed by `ZSTD_compressStream()`, `ZSTD_flushStream()`, or `ZSTD_endStream()`.
- Modern advanced streaming and one-shot compression through `ZSTD_compressStream2()`, `ZSTD_compressStream2_simpleArgs()`, and `ZSTD_compress2()`.
- Experimental sequence compression through `ZSTD_compressSequences()` and `ZSTD_compressSequencesAndLiterals()`, where callers provide a parse instead of letting zstd's match finder generate one.

The chunk also exposes compression-level metadata (`ZSTD_maxCLevel()`, `ZSTD_minCLevel()`, `ZSTD_defaultCLevel()`, `ZSTD_getCParams()`, `ZSTD_getParams()`) and stores callbacks for the block-level external sequence producer API.

## Important APIs, Types, And Functions

Streaming initialization functions:

- `ZSTD_initCStream_internal()` resets the session, sets pledged source size, copies validated `ZSTD_CCtx_params`, and installs either a raw dictionary or a `ZSTD_CDict`.
- `ZSTD_initCStream_usingCDict_advanced()`, `ZSTD_initCStream_usingCDict()`, `ZSTD_initCStream_advanced()`, `ZSTD_initCStream_usingDict()`, `ZSTD_initCStream_srcSize()`, and `ZSTD_initCStream()` are legacy wrappers that reset session state, set compression level or frame parameters, and attach dictionary state as needed.
- The legacy APIs preserve compatibility quirks where zero pledged size can mean `ZSTD_CONTENTSIZE_UNKNOWN` in selected paths.

Streaming compression functions:

- `ZSTD_compressStream2()` is the central public advanced streaming API in this chunk. It validates buffer positions and end directives, lazily initializes the context, dispatches to multi-threaded or single-threaded streaming, tracks stable buffer guarantees, and returns a lower bound on remaining buffered output.
- `ZSTD_compressStream_generic()` is the single-threaded streaming state machine. It handles `zcss_load` and `zcss_flush`, fills or references input according to buffer mode, calls `ZSTD_compressContinue_public()` or `ZSTD_compressEnd_public()`, and drains internal output buffers.
- `ZSTD_compressStream()` is the legacy continue-only wrapper around `ZSTD_compressStream2()`.
- `ZSTD_compress2()` implements one-shot advanced compression by resetting the session, temporarily enabling stable input/output buffer modes, invoking `ZSTD_compressStream2_simpleArgs(..., ZSTD_e_end)`, and converting incomplete output into `dstSize_tooSmall`.
- `ZSTD_flushStream()` and `ZSTD_endStream()` convert stream finalization into `ZSTD_compressStream2()` calls with synthetic or stable input buffers.

Buffer-stability helpers:

- `ZSTD_setBufferExpectations()` records `expectedInBuffer` and `expectedOutBufferSize` after each call when stable buffer modes are active.
- `ZSTD_checkBufferStability()` rejects later calls that change the stable input pointer/position or grow the stable output remainder.
- `inBuffer_forEndFlush()` returns the stored stable input buffer for flush/end operations, or a null input buffer for ordinary buffered mode.

Context initialization:

- `ZSTD_CCtx_init_compressStream2()` is the transparent lazy initializer used by streaming, `compress2()`, and sequence APIs. It initializes local dictionaries, consumes one-shot prefix dictionaries, derives final `ZSTD_CCtx_params`, resolves automatic switches, configures multi-threading when allowed, or calls `ZSTD_compressBegin_internal()` for single-threaded buffered compression.
- In multi-threaded builds it rejects external sequence producers with `nbWorkers >= 1`, skips MT for tiny pledged inputs, creates `ZSTDMT_CCtx` on demand, and calls `ZSTDMT_initCStream_internal()`.

Sequence compression helpers:

- `ZSTD_validateSequence()` validates external sequences against offset bounds, minimum match length, window log, dictionary size, and external-producer rules.
- `ZSTD_finalizeOffBase()` converts raw public offsets into internal offBase values, using current repcodes when the raw offset matches repcode history.
- `ZSTD_transferSequences_wBlockDelim()` copies an explicitly delimited block of public sequences into `seqStore`, validates if enabled, updates repcodes, stores the final literals from the delimiter sequence, and advances `ZSTD_SequencePosition`.
- `ZSTD_transferSequences_noDelim()` copies sequences without explicit delimiters into target block-sized chunks. It may split a long match only when required and when both sides can satisfy `minMatch`; otherwise it backs up and stores remaining bytes as last literals.
- `ZSTD_selectSequenceCopier()`, `blockSize_explicitDelimiter()`, and `determine_blockSize()` choose and size the next sequence block based on `ZSTD_c_blockDelimiters`.
- `ZSTD_compressSequences_internal()` compresses a source buffer using caller-provided sequences. It writes raw blocks for tiny or incompressible data, may emit RLE blocks after checking actual source bytes, and writes compressed-block headers after entropy compression succeeds.
- `ZSTD_compressSequences()` initializes a frame, writes the frame header, optionally updates the checksum state from the full source, delegates to `ZSTD_compressSequences_internal()`, and appends the frame checksum when requested.

Sequence-and-literals variant:

- `convertSequences_noRepcodes()` converts `ZSTD_Sequence` to internal `SeqDef` without repcode resolution and returns encoded long-length metadata. This chunk contains AVX2, RISC-V RVV, ARM SVE2, ARM NEON, and scalar implementations guarded by architecture macros.
- `ZSTD_convertBlockSequences()` converts one explicitly delimited block of sequences into `seqStore`, either through the fast no-repcode converter or a scalar path that resolves repcodes as it stores sequences.
- `ZSTD_get1BlockSummary()` scans an explicitly delimited sequence array to find one block, count consumed sequences, and sum literal and total block sizes. It has AVX2, RISC-V RVV, and scalar implementations; the scalar path uses packed `litLength`/`matchLength` reads and endian-aware terminator detection.
- `ZSTD_compressSequencesAndLiterals_internal()` compresses blocks from public sequences plus a separate contiguous literal buffer. Because the original source bytes are unavailable, it cannot emit uncompressed blocks and returns `cannotProduce_uncompressedBlock` if entropy compression cannot produce a compressed block.
- `ZSTD_compressSequencesAndLiterals()` wraps the variant with frame-header emission and rejects unsupported modes: no block delimiters, sequence validation, and frame checksum.

Compression-level helpers:

- `ZSTD_maxCLevel()`, `ZSTD_minCLevel()`, and `ZSTD_defaultCLevel()` expose bounds from `clevels.h`.
- `ZSTD_dedicatedDictSearch_getCParams()`, `ZSTD_dedicatedDictSearch_isSupported()`, and `ZSTD_dedicatedDictSearch_revertCParams()` adjust or inspect lazy-strategy dictionary-search parameters.
- `ZSTD_getCParamRowSize()`, `ZSTD_getCParams_internal()`, `ZSTD_getCParams()`, `ZSTD_getParams_internal()`, and `ZSTD_getParams()` select rows from `ZSTD_defaultCParameters` based on level, source size, dictionary size, and dictionary attach mode, then refine through `ZSTD_adjustCParams_internal()`.

External producer registration:

- `ZSTD_registerSequenceProducer()` stores a user-provided block-level sequence producer function and state on `ZSTD_CCtx.requestedParams`.
- `ZSTD_CCtxParams_registerSequenceProducer()` performs the same operation for reusable parameter objects and clears both fields when the function pointer is `NULL`.

Important supporting types include `ZSTD_CCtx`, `ZSTD_CStream`, `ZSTD_CCtx_params`, `ZSTD_CDict`, `ZSTD_outBuffer`, `ZSTD_inBuffer`, `ZSTD_EndDirective`, `ZSTD_Sequence`, `ZSTD_SequencePosition`, `SeqDef`, `SeqStore_t`, `BlockSummary`, `Repcodes_t`, `ZSTD_SequenceFormat_e`, and `ZSTD_sequenceProducer_F`.

## Control Flow

`ZSTD_compressStream2()` has a transparent initialization stage. When `streamStage == zcss_init`, it may defer initialization for stable input mode if a non-flushing continue call has less than one block available. In that case it pretends to consume input, records the stable input buffer, accumulates `stableIn_notConsumed`, and returns a minimum frame-header-size hint. Otherwise it calls `ZSTD_CCtx_init_compressStream2()`, then records buffer expectations.

Initialization resolves parameters in several steps. It initializes local dictionary material, clears one-shot prefix dictionary state, lets a non-local `CDict` compression level override requested level, sets pledged size automatically for `ZSTD_e_end`, computes final compression parameters based on source size and dictionary size, resolves automatic feature switches, and chooses either multi-threaded or single-threaded execution. The single-threaded path calls `ZSTD_compressBegin_internal()`, initializes input/output buffer cursors, moves to `zcss_load`, and clears `frameEnded`.

The single-threaded streaming state machine alternates between:

- `zcss_load`: load enough input into `inBuff` in buffered mode, or reference caller input directly in stable mode. For `ZSTD_e_continue`, it stops early if a full block is not available. For `ZSTD_e_flush`, it stops if there is no new data. For `ZSTD_e_end`, it may shortcut directly to `ZSTD_compressEnd_public()` if output space is sufficient or stable output mode is allowed.
- Compression within `zcss_load`: choose direct output if remaining output is large enough for `ZSTD_compressBound(iSize)` or stable output is enabled; otherwise compress into `outBuff`. The call is `ZSTD_compressContinue_public()` unless this is the last block, in which case it is `ZSTD_compressEnd_public()`.
- `zcss_flush`: copy pending bytes from `outBuff` to the caller output. If the frame ended, reset the session; otherwise return to `zcss_load`.

The multi-threaded branch delegates to `ZSTDMT_compressStream_generic()`, updates `consumedSrcSize` and `producedCSize`, refreshes changed compression parameters through `ZSTDMT_updateCParams_whileCompressing()`, and resets the session once end compression completes.

`ZSTD_compressSequences()` follows frame-oriented control flow: initialize the context as an end operation, write the frame header, update checksum state if enabled, repeatedly determine a block size, copy caller sequences into `seqStore`, entropy-compress the block, and emit compressed, RLE, or raw block output. `ZSTD_compressSequencesAndLiterals()` follows the same frame start but requires explicit block delimiters and compresses using a pre-extracted literals buffer, so its block loop cannot fall back to raw/RLE source emission.

## State And Persistence Behavior

Most state in this chunk lives on `ZSTD_CCtx` and persists across streaming calls until a session reset. Important fields include `requestedParams`, `appliedParams`, `streamStage`, `inBuffPos`, `inBuffTarget`, `inToCompress`, `outBuffContentSize`, `outBuffFlushedSize`, `stableIn_notConsumed`, `expectedInBuffer`, `expectedOutBufferSize`, `frameEnded`, `pledgedSrcSizePlusOne`, `dictID`, `dictContentSize`, `consumedSrcSize`, and `producedCSize`.

Dictionary state is sticky depending on how it is installed. `ZSTD_initCStream_internal()` copies requested params and loads or references a dictionary. `ZSTD_CCtx_init_compressStream2()` treats `prefixDict` as single-use by copying it locally and zeroing `cctx->prefixDict`. A referenced `CDict` remains attached until reset or replacement, and may override the requested compression level during initialization.

Stable input mode avoids an input window copy by trusting the caller's memory to remain valid and unchanged. The compressor may report input as consumed before it is actually compressed, storing the unconsumed amount in `stableIn_notConsumed`. Stable output mode avoids the internal output buffer and permits immediate `dstSize_tooSmall` failures when output capacity is insufficient.

Sequence compression mutates `seqStore`, block repcodes, entropy table state, checksum state, and frame progress just like normal compression. `ZSTD_blockState_confirmRepcodesAndEntropyTables()` commits next block state after compressed blocks. The sequence-and-literals variant consumes the supplied literals pointer and sequence pointer block by block, and verifies at the end that both literal size and represented decompressed size were consumed exactly.

External sequence producer registration stores only a function pointer and opaque state pointer. The user owns the lifetime of that state. Registration persists until compression parameters are reset or the caller registers a `NULL` function.

No file-system persistence or commits occur in this code. All persistence is in process memory associated with compression contexts, parameter objects, and optionally MT contexts.

## Dependencies And Integration Points

This chunk depends heavily on earlier helpers in the same file:

- Context setup and reset: `ZSTD_CCtx_reset()`, `ZSTD_CCtx_setPledgedSrcSize()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_loadDictionary()`, `ZSTD_CCtx_refCDict()`, `ZSTD_initLocalDict()`, and `ZSTD_compressBegin_internal()`.
- Block and frame output: `ZSTD_writeFrameHeader()`, `ZSTD_compressContinue_public()`, `ZSTD_compressEnd_public()`, `ZSTD_noCompressBlock()`, `ZSTD_rleCompressBlock()`, `ZSTD_writeLastEmptyBlock()`, and `ZSTD_writeEpilogue()`.
- Sequence and entropy internals: `ZSTD_storeSeq()`, `ZSTD_storeSeqOnly()`, `ZSTD_storeLastLiterals()`, `ZSTD_resetSeqStore()`, `ZSTD_entropyCompressSeqStore()`, `ZSTD_entropyCompressSeqStore_internal()`, `ZSTD_maybeRLE()`, `ZSTD_isRLE()`, and `ZSTD_updateRep()`.
- Parameter logic: `ZSTD_getCParamMode()`, `ZSTD_getCParamsFromCCtxParams()`, `ZSTD_adjustCParams_internal()`, `ZSTD_checkCParams()`, and `clevels.h`.

It integrates with `zstd.h` static/experimental APIs for `ZSTD_compressSequences()`, `ZSTD_compressSequencesAndLiterals()`, stable buffer parameters, block delimiters, sequence validation, repcode search, and external sequence producers. It also integrates with `zstdmt_compress.c` when `ZSTD_MULTITHREAD` is enabled through `ZSTDMT_createCCtx_advanced()`, `ZSTDMT_initCStream_internal()`, `ZSTDMT_compressStream_generic()`, `ZSTDMT_nextInputSizeHint()`, and `ZSTDMT_updateCParams_whileCompressing()`.

Architecture-specific conversion code depends on AVX2 intrinsics (`immintrin.h`), RISC-V vector intrinsics (`riscv_vector.h`), ARM SVE2 intrinsics, or ARM NEON intrinsics. Each vector path protects its layout assumptions with `ZSTD_STATIC_ASSERT()` against `ZSTD_Sequence` and `SeqDef` field offsets.

Checksum integration is through `XXH64_update()` and `XXH64_digest()` when frame checksum is enabled. Error propagation uses zstd's common `RETURN_ERROR_IF()`, `RETURN_ERROR()`, `FORWARD_IF_ERROR()`, and `ZSTD_isError()` conventions.

## Risks And Edge Cases

Stable buffer modes are powerful but fragile. If the caller changes the input pointer, externally modifies `pos`, grows the remaining output size, or mutates already-consumed stable input bytes, the code can either return a stability error or, for mutated memory, produce corrupted compressed output. The delayed initialization path for small stable inputs is especially stateful because `input->pos` advances while `stableIn_notConsumed` records that compression has not consumed the bytes internally yet.

Streaming completion resets the session from inside the compression path. Callers relying on sticky parameters must distinguish session reset from parameter reset: session reset preserves parameters, but prefix dictionaries are single-use and have already been cleared during initialization.

`ZSTD_compress2()` temporarily overwrites requested stable buffer modes and restores them after the call. If a new error path is added before restoration, it could accidentally leave requested parameters mutated. In the current code the restoration happens before error forwarding.

Sequence APIs trust caller-provided parses unless `ZSTD_c_validateSequences` is enabled. Invalid offsets, match lengths, block delimiters, or size sums can lead to returned errors when detected, but the public docs explicitly warn that disabled validation can cause undefined behavior or decompression corruption.

Explicit delimiter mode requires delimiter sequences with `offset == 0` and `matchLength == 0`. Missing delimiters, delimiters larger than the remaining source, or blocks larger than `blockSizeMax` return `externalSequences_invalid`. In no-delimiter mode, splitting decisions around matches must maintain minimum match length on both sides; mistakes here would create invalid zstd sequences at block boundaries.

`ZSTD_compressSequencesAndLiterals()` has narrower fallback behavior than `ZSTD_compressSequences()`. Since it lacks the original source, it cannot emit raw uncompressed blocks, cannot produce RLE reliably from source bytes, rejects checksums, rejects validation, and requires exact literal/decompressed-size accounting. Incompressible blocks become hard errors.

The vectorized `convertSequences_noRepcodes()` implementations are performance-sensitive and layout-sensitive. They assume 16-byte `ZSTD_Sequence`, 8-byte `SeqDef`, exact field offsets, and that no repcode resolution is needed. Bugs may appear only on specific CPU feature builds or with long literal/match lengths that trigger overflow metadata.

`ZSTD_get1BlockSummary()` uses vector or packed reads to scan for the first `matchLength == 0` terminator. It also asserts that a terminator has `offset == 0`. Any caller that passes an unterminated block gets `externalSequences_invalid`; a malformed terminator may trip assertions in debug builds.

Multi-threading and external sequence producers are deliberately incompatible in this path. `ZSTD_CCtx_init_compressStream2()` returns `parameter_combination_unsupported` if an external producer is registered and `nbWorkers >= 1`, before MT job-size reduction can mask the configuration.

Compression-level selection depends on source-size interpretation. Public `ZSTD_getCParams()` and `ZSTD_getParams()` translate `srcSizeHint == 0` to unknown, while internal paths can treat zero as exact depending on the caller. Dictionary attach mode also changes the row-size calculation by ignoring dictionary size for attached dictionaries.

## Test Signals

Streaming tests should cover `ZSTD_compressStream2()` with all end directives: many `ZSTD_e_continue` calls, flush without new input, end with and without pending buffered input, empty frames, output buffers that fill mid-flush, and direct-output shortcuts where `dstCapacity >= ZSTD_compressBound(input)`.

Stable buffer tests should enable `ZSTD_c_stableInBuffer` and `ZSTD_c_stableOutBuffer` separately and together. Useful cases include small stable inputs that delay initialization, appended input through increasing `size`, mismatched input pointers, externally modified `pos`, and output remaining-size growth. Expected results are either valid compressed frames or `stabilityCondition_notRespected`.

Multi-threaded builds should test `nbWorkers > 0`, dynamic parameter updates during compression, tiny pledged input that disables MT, end completion resetting the session, and the unsupported combination of external sequence producer plus workers.

Legacy API coverage should exercise every `ZSTD_initCStream*()` wrapper with no dictionary, raw dictionary, `CDict`, advanced frame parameters, pledged size zero compatibility paths, and unknown pledged size. `ZSTD_flushStream()` and `ZSTD_endStream()` should be checked after both buffered and stable-input operation.

Sequence API tests should compare `ZSTD_compressSequences()` output to normal compression for generated valid sequences, both with `ZSTD_sf_noBlockDelimiters` and `ZSTD_sf_explicitBlockDelimiters`. Boundary cases should include empty source, tiny blocks, incompressible data falling back to raw blocks, RLE-eligible non-first blocks, last literals, dictionaries/prefixes, checksum enabled, and sequence validation enabled/disabled.

Invalid sequence tests should include missing explicit delimiters, delimiter with nonzero match length, too-large offsets, match lengths below `minMatch`, sequence lengths that exceed source size, source bytes left over as literals, and insufficient `seqStore.maxNbSeq`.

`ZSTD_compressSequencesAndLiterals()` tests should cover exact literal consumption, too-small literal capacity, wrong decompressed size, no-delimiter rejection, checksum rejection, validation rejection, empty frame emission, and incompressible block failure with `cannotProduce_uncompressedBlock`.

Architecture coverage should compile and run sequence conversion tests on scalar, AVX2, RISC-V RVV, ARM SVE2, and ARM NEON builds where available. Inputs should include odd sequence counts, long match lengths, long literal lengths, zero-length delimiter sequences, and high offsets.

Compression-level tests should verify `ZSTD_maxCLevel()`, `ZSTD_minCLevel()`, `ZSTD_defaultCLevel()`, negative-level acceleration through `targetLength`, source-size table row boundaries around 16 KB, 128 KB, and 256 KB, unknown source sizes, and dictionary attach/create modes.

External producer tests should register a callback on `ZSTD_CCtx` and `ZSTD_CCtx_params`, verify persistence across compressions, verify clearing with `NULL`, verify static-CCtx size estimation paths, and confirm advanced APIs honor the producer while legacy APIs that ignore advanced parameters behave as documented.
