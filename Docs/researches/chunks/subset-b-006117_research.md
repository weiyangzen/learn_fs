# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress.c lines 1-5965

## Scope And Purpose

This chunk covers the first 5,965 lines of Ceph's vendored kernel-oriented zstd compression core. It implements most single-threaded compression context lifecycle, compression-parameter plumbing, workspace sizing and reset, dictionary ingestion and digested dictionaries, match-state reset and overflow correction, block sequence generation, entropy-table construction, block/frame emission, one-shot compression APIs, CDict APIs, and the beginning of CStream initialization.

The file is the central integration point for the compressor side of the vendored zstd library under `sources/distributed-fs/ceph-client/lib/zstd`. It connects public `ZSTD_*` APIs to workspace allocation, strategy-specific match finders, long-distance matching, optional external sequence producers, Huffman/FSE entropy writers, frame-format writers, and dictionary handling. This chunk ends inside the streaming initialization section after `ZSTD_initCStream()` has only opened; the later streaming state machine belongs to the next chunk.

## Important APIs, Types, And Data

`struct ZSTD_CDict_s` is defined in this chunk. It stores the dictionary content pointer and size, content type, entropy workspace, `ZSTD_cwksp`, prepared `ZSTD_MatchState_t`, compressed block state, custom allocator, dict ID, original compression level, and resolved row-matchfinder mode. CDicts may own copied dictionary bytes in their workspace or reference caller-owned bytes, depending on the load method.

`ZSTD_CCtx` is created, initialized, reset, sized, copied, and freed here through `ZSTD_createCCtx()`, `ZSTD_createCCtx_advanced()`, `ZSTD_initStaticCCtx()`, `ZSTD_freeCCtx()`, `ZSTD_sizeof_CCtx()`, `ZSTD_CCtx_reset()`, and `ZSTD_copyCCtx()`. The CCtx persists requested and applied params, workspace memory, match/block state, sequence stores, streaming stage, dictionary references, frame counters, checksum state, input/output buffers, and optional external-sequence state.

`ZSTD_CCtx_params` is the main parameter carrier. Public and internal helpers include `ZSTD_CCtxParams_init()`, `ZSTD_CCtxParams_init_advanced()`, `ZSTD_CCtxParams_reset()`, `ZSTD_CCtxParams_setParameter()`, `ZSTD_CCtxParams_getParameter()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_getParameter()`, `ZSTD_CCtx_setCParams()`, `ZSTD_CCtx_setFParams()`, `ZSTD_CCtx_setParams()`, and `ZSTD_CCtx_setParametersUsingCCtxParams()`.

Parameter-resolution helpers include `ZSTD_cParam_getBounds()`, `ZSTD_checkCParams()`, `ZSTD_adjustCParams_internal()`, `ZSTD_getCParamsFromCCtxParams()`, `ZSTD_makeCCtxParamsFromCParams()`, `ZSTD_resolveRowMatchFinderMode()`, `ZSTD_resolveBlockSplitterMode()`, `ZSTD_resolveEnableLdm()`, `ZSTD_resolveMaxBlockSize()`, and `ZSTD_resolveExternalRepcodeSearch()`. In this Ceph/kernel variant, multithreading bounds are zero and nonzero `nbWorkers`, `jobSize`, `overlapLog`, and `rsyncable` settings return unsupported-parameter errors.

The block pipeline uses `ZSTD_MatchState_t`, `ZSTD_compressedBlockState_t`, `ZSTD_blockState_t`, `SeqStore_t`, `RawSeqStore_t`, `SeqCollector`, `Repcodes_t`, `ZSTD_entropyCTables_t`, and `ZSTD_entropyCTablesMetadata_t`. These hold match tables, rolling windows, repeat offsets, literals, parsed sequences, exported sequence buffers, Huffman/FSE tables, and block-splitting metadata.

Main compression entry points in this range include `ZSTD_compressBegin*()`, `ZSTD_compressContinue()`, `ZSTD_compressBlock()`, `ZSTD_compressEnd()`, `ZSTD_compress_advanced()`, `ZSTD_compress_usingDict()`, `ZSTD_compressCCtx()`, `ZSTD_compress()`, `ZSTD_compress_usingCDict*()`, `ZSTD_writeSkippableFrame()`, and `ZSTD_writeLastEmptyBlock()`. Sequence-facing APIs include `ZSTD_sequenceBound()`, `ZSTD_generateSequences()`, `ZSTD_mergeBlockDelimiters()`, `ZSTD_referenceExternalSequences()`, and internal conversion/validation helpers.

CDict and CStream APIs in this chunk include `ZSTD_estimateCDictSize*()`, `ZSTD_createCDict*()`, `ZSTD_initStaticCDict()`, `ZSTD_freeCDict()`, `ZSTD_sizeof_CDict()`, `ZSTD_getCParamsFromCDict()`, `ZSTD_getDictID_fromCDict()`, `ZSTD_createCStream*()`, `ZSTD_initStaticCStream()`, `ZSTD_freeCStream()`, `ZSTD_CStreamInSize()`, `ZSTD_CStreamOutSize()`, `ZSTD_resetCStream()`, and early `ZSTD_initCStream*()` wrappers.

## Control Flow

Context creation allocates or reserves a `ZSTD_CCtx`, zeroes it, records the custom allocator, detects BMI2 support, and resets default parameters. Static CCtx creation uses caller-provided 8-byte-aligned memory, reserves fixed block-state and temporary workspace objects up front, and cannot later resize or allocate copied dictionaries.

Parameter flow is staged. Setters enforce bounds and stage restrictions, then update `requestedParams`. Only a small subset of compression parameters can be changed after streaming has started, and those changes mark `cParamsChanged`; dictionary, frame, LDM, buffer, and most experimental settings require init stage. Finalization resolves auto modes for row matchfinder, block splitter, LDM, max block size, external repcode search, and adjusted cParams.

`ZSTD_resetCCtx_internal()` is the core session reset. It copies finalized params into `appliedParams`, adjusts LDM params, computes window and block sizes, estimates workspace needs, resizes dynamic workspaces when too small or wasteful, reserves match tables, sequence storage, literal buffers, LDM tables, external-sequence buffers, and optional streaming buffers, then resets frame counters, checksum state, dictionary IDs, block state, and match state.

Match-state reset chooses hash, chain, hash3, row tag, and optimal-parser tables based on strategy, row-matchfinder mode, dictionary-search mode, and reset target. It can either clean tables or leave them dirty when the next step will overwrite them, such as copying CDict tables. Row-based match finding uses an additional tag table and a hash salt; CDict resets keep unsalted deterministic tables.

Dictionary setup has local and CDict paths. `ZSTD_CCtx_loadDictionary_advanced()` stores a local dictionary by reference or by owned copy for later digestion. `ZSTD_initLocalDict()` turns a loaded local dictionary into a CDict on first use. `ZSTD_CCtx_refCDict()` attaches an existing CDict reference. Prefix APIs clear other dictionaries and use caller-owned prefix data as raw content.

CDict application chooses between attaching and copying. `ZSTD_shouldAttachDict()` favors in-place attachment for dedicated dictionary search, small or unknown sources, forced attach, and non-force-window cases. Attachment points the working match state at the CDict match state and copies entropy/repcodes. Copying resets the working context with CDict table parameters, copies hash/chain/tag tables, strips short-cache tags for tagged CDict indices, zeroes hash3, and copies dictionary window offsets.

Block compression starts in `ZSTD_compressContinue_internal()`. Frame mode writes a frame header at the first chunk, updates the match/LDM windows, then calls `ZSTD_compress_frameChunk()` to split input into blocks. Each block corrects index overflow, checks dictionary validity, enforces max distance, and then chooses target compressed-block-size mode, post-sequence block splitting, or normal block compression.

`ZSTD_buildSeqStore()` fills `SeqStore_t`. It can consume externally referenced raw sequences, generate LDM sequences, call an external sequence producer callback, or dispatch to built-in strategy compressors via `ZSTD_selectBlockCompressor()`. The selected path updates repcodes, emits last literals, handles fallback from external producers when enabled, and validates sequence lengths in debug builds.

Entropy compression converts sequence fields into LL/OF/ML code streams with `ZSTD_seqToCodes()`, compresses literals through `ZSTD_compressLiterals()`, selects FSE encoding modes, builds FSE C tables, writes sequence headers, and encodes the bitstream. Blocks that are too small, uncompressible, too large for the output budget, or in old-decoder compatibility edge cases fall back to raw or RLE block output.

Block splitting builds entropy stats for candidate sub-blocks, estimates compressed sizes, recursively records beneficial sequence split points, and then emits partitions. Because raw/RLE partitions affect decoder-side repeat-offset history differently from compressor-side history, the split path maintains separate compression and decompression repcode simulations and rewrites invalid repcodes to raw offsets when needed.

Frame completion uses `ZSTD_writeEpilogue()`. It writes an empty last block for empty or not-yet-ended frames, appends an optional XXH64-derived checksum, validates pledged source size, traces the context hook, and returns the stage to created. One-shot APIs wrap begin/end around this same path; `ZSTD_compress()` allocates a temporary CCtx.

## State And Persistence Behavior

`requestedParams` persist across sessions until parameters are reset. `appliedParams` are the finalized per-session copy and can differ because source size, dictionary size, row matchfinder, LDM, block splitter, max block size, and attach/copy heuristics are resolved at begin/reset time.

The `ZSTD_cwksp` workspace persists for reuse. Dynamic contexts can free and recreate it; static contexts fail if the caller-provided workspace is too small. Table dirty/clean state is explicit so the code can avoid redundant clearing when tables are about to be copied or reduced.

Match indexes persist across reuse unless the context is uninitialized, a workspace resize occurs, the dictionary is too large, or positions approach 32-bit overflow. `ZSTD_overflowCorrectIfNeeded()` reduces table entries, adjusts `nextToUpdate`, clears loaded-dictionary markers, and drops attached dictionary match state.

Rolling windows track contiguous input history and dictionary content. `ZSTD_window_update()`, `ZSTD_window_enforceMaxDist()`, `ZSTD_checkDictValidity()`, `loadedDictEnd`, `dictLimit`, and `lowLimit` collectively decide what history is addressable. `forceNonContiguous` is set for deterministic referenced prefixes.

Entropy and repcode state persist between compressed blocks through `prevCBlock` and `nextCBlock`. Successful compressed blocks swap these states. Raw/RLE or uncompressed paths deliberately avoid some entropy updates and may move FSE repeat modes from valid to check to keep future block encodings decodable.

Dictionary lifetime depends on API choice. By-copy local dictionaries and CDicts are owned by the context/workspace. By-reference dictionaries, prefixes, and by-reference CDicts require caller lifetime stability. `ZSTD_clearAllDicts()` frees owned local dictionary bytes and local CDicts, clears prefix state, and drops any referenced CDict.

Frame counters (`consumedSrcSize`, `producedCSize`, `pledgedSrcSizePlusOne`) persist through a frame and are surfaced by `ZSTD_getFrameProgression()`. `xxhState` persists only when checksum output is enabled. `streamStage` and `stage` enforce public API sequencing.

## Dependencies And Integration Points

This chunk includes common allocation, dependency, memory, error, FSE, HUF, and bit helpers, plus zstd compression internals, sequence/literal encoders, strategy compressors (`zstd_fast`, `zstd_double_fast`, `zstd_lazy`, `zstd_opt`), LDM, superblock compression, and pre-splitting.

Strategy integration is table-driven in `ZSTD_selectBlockCompressor()`. The selected function depends on `ZSTD_strategy`, dictionary mode, dedicated dictionary search, and row-matchfinder use. This binds the central pipeline to normal, ext-dict, dict-match-state, dedicated-dictionary-search, and row-based compressor variants.

Dictionary integration spans raw-content dictionaries, full zstd dictionary format parsing, entropy table loading, repcode validation, dict ID propagation, CDict attach/copy heuristics, dedicated dictionary search, short-cache tagged indices, and LDM dictionary loading.

Frame-format integration is handled by `ZSTD_writeFrameHeader()`, `writeBlockHeader()`, `ZSTD_writeLastEmptyBlock()`, `ZSTD_writeSkippableFrame()`, and `ZSTD_writeEpilogue()`. These encode magicless-vs-standard format, dictionary ID, checksum flag, content-size flag, single-segment/window descriptor, block type, and frame checksum.

Sequence integration covers internal `SeqStore_t`, public `ZSTD_Sequence` collection, block delimiter insertion and merging, external sequence producer callbacks, LDM raw sequence stores, and offset/repcodes conversion for exported or partitioned sequences.

Ceph-specific integration is through the vendored kernel zstd subtree. Compared with the generic userspace zstd copy, this chunk has an SPDX GPL/BSD header, no active `ZSTD_MULTITHREAD` code paths, and a Linux-kernel row-matchfinder auto threshold that disables row matching at common 128 KiB windows without SIMD.

## Risks And Edge Cases

Stage rules are correctness-critical. Parameter changes, dictionary loads, prefix references, resets, and CDict attachment are only safe in the expected init/session stages. Bypassing those checks can make allocated tables inconsistent with active compression state.

Workspace estimation must match actual reservations for dynamic and static contexts. Underestimation can produce allocation failures or invalid table pointers; overestimation wastes memory and can cause needless workspace churn. Static contexts are especially constrained because they cannot resize.

Auto-parameter resolution is subtle. Row matchfinder, LDM, block splitter, max block size, source-size hints, and CDict attach/copy decisions affect table sizes, chosen compressors, and frame behavior. Estimation, reset, and dispatch must agree on the resolved values.

Dictionary handling is high-risk. Full dictionaries must reject corrupt entropy tables, impossible offset alphabets, zero repcodes, and repcodes larger than dictionary content. Large dictionaries are truncated to avoid index overflow and short-cache tag overlap. Attached dictionaries rely on adjacency and are incompatible with some force-window behavior.

Repeat-offset history is fragile around raw, RLE, and split blocks. The split-block path's dual repcode simulation prevents streams that encode successfully but fail when the decoder's repcode history diverges.

External sequence producers can return oversized counts, no delimiter, impossible length sums, invalid parses, or errors. The `enableMatchFinderFallback` flag decides whether the compressor propagates those errors or falls back to the internal parser.

Compatibility workarounds are intentional: avoid first-block RLE for old zstd CLI decoders, avoid tiny compressed sequence payloads that old decoders mishandle, and ensure compressed block size behavior stays inside legacy decoder and `ZSTD_compressBound()` expectations.

Overflow correction and table reduction must preserve special index values, binary-tree unsorted marks, row/hash tables, and `nextToUpdate`. When correction happens, dictionary attachment is invalidated because historical positions have changed.

The chunk boundary is a risk for readers. `ZSTD_initCStream()` begins at line 5963 but its body and the main streaming compressor are not in this chunk, so this document should not be treated as complete streaming coverage.

## Test Signals

Round-trip tests should cover all compression levels and strategies supported in this build, empty input, one-byte input, small inputs below compression thresholds, exact block-sized input, multi-block input, RLE data, highly compressible data, and incompressible data.

Parameter tests should exercise every `ZSTD_cParameter` bound, default/clamp behavior, getter/setter round trips, unsupported nonzero multithreading parameters, row-matchfinder auto behavior at kernel thresholds, LDM enable/auto, block splitting, max block size, target compressed block size, reset directives, and stage-wrong errors.

Dictionary tests should cover raw and full dictionaries, by-copy and by-reference lifetimes, prefixes, local dictionary initialization, CDict attach/copy/force preferences, static CDict and static CCtx sizing, corrupt dictionary entropy, zero or oversized repcodes, large dictionary truncation, dict ID suppression, short-cache strategies, and dedicated dictionary search fallback.

Block and entropy tests should validate normal compressed blocks, raw fallback, RLE fallback, target-size superblocks, post-sequence block splitting, repeated entropy tables, no-literal-compression mode, min-gain decisions, old-decoder compatibility cases, and exact output-capacity failures.

Sequence tests should cover `ZSTD_generateSequences()`, `ZSTD_sequenceBound()`, block delimiters, delimiter merging, long literal/match lengths, repcode export, external sequence producer success/failure, fallback enabled/disabled, and invalid sequence length sums.

State-reuse tests should repeatedly compress many small inputs with one context, copy contexts in init stage, reset sessions with and without parameter reset, force index-overflow correction through large cumulative input, validate `ZSTD_getFrameProgression()`, and verify that `ZSTD_resetCStream()` preserves the expected requested parameters while resetting session state.

Memory and sanitizer signals should include ASAN/MSAN/UBSAN builds, custom allocator failure injection, static workspace estimates versus actual initialization, by-reference lifetime stress, excluded-strategy preprocessor builds, and kernel-build configurations without zstd multithreading.
