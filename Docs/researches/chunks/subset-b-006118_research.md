# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress.c lines 5966-7634

## Scope

This chunk covers the single-threaded streaming compression path, the one-shot `ZSTD_compress2()` wrapper, external/public sequence compression entry points, stream finalization helpers, compression-level parameter lookup, and external sequence-producer registration.

The range begins with the tail of `ZSTD_initCStream()` and then implements the `ZSTD_compressStream2()` state machine from line 6291. It continues through sequence conversion/compression helpers for both "source plus sequences" and "literals plus sequences" modes, ends stream flushing at lines 7429-7458, and finishes with `ZSTD_getCParams()`, `ZSTD_getParams()`, and registration of `ZSTD_sequenceProducer_F` callbacks.

## Purpose

The code provides the core compression API behavior used after a `ZSTD_CCtx` has been configured. It turns requested compression parameters, dictionaries, stable-buffer options, and end directives into frame output while preserving streaming progress across calls.

It also exposes lower-level sequence ingestion paths. These paths let callers supply already-discovered `ZSTD_Sequence` arrays, either alongside the original source buffer (`ZSTD_compressSequences()`) or alongside just the literals buffer (`ZSTD_compressSequencesAndLiterals()`). That is relevant to this tree because `sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c` registers external sequence producers and calls `ZSTD_compressSequencesAndLiterals()` from the zstd module wrapper.

The final section maps public compression levels and source/dictionary size hints to concrete `ZSTD_compressionParameters`, including dedicated dictionary-search adjustments and the registration point for out-of-tree or module-level sequence producers.

## Important APIs, Types, and Functions

- `ZSTD_nextInputSizeHint()` returns the minimum input amount needed to complete the current block. Buffered mode uses `inBuffTarget - inBuffPos`; stable-input mode uses `blockSizeMax - stableIn_notConsumed`.
- `ZSTD_compressStream_generic()` is the internal streaming state machine for `ZSTD_compressStream2()` and legacy `ZSTD_compressStream()`. It handles `zcss_load`, optional `zcss_flush`, direct-output shortcuts, buffered input/output movement, and frame completion reset.
- `ZSTD_compressStream()` is the legacy continue-only wrapper around `ZSTD_compressStream2(..., ZSTD_e_continue)` and returns the next input-size hint rather than pending output bytes.
- `ZSTD_setBufferExpectations()` and `ZSTD_checkBufferStability()` enforce `ZSTD_c_stableInBuffer` and `ZSTD_c_stableOutBuffer` contracts through `expectedInBuffer`, `stableIn_notConsumed`, and `expectedOutBufferSize`.
- `ZSTD_CCtx_init_compressStream2()` performs transparent initialization for `ZSTD_compressStream2()`: initializes a one-use local dictionary, resolves effective compression parameters, starts the frame with `ZSTD_compressBegin_internal()`, and initializes stream buffer cursors.
- `ZSTD_compressStream2()` is the public streaming API taking `ZSTD_EndDirective` (`ZSTD_e_continue`, `ZSTD_e_flush`, `ZSTD_e_end`). It validates buffer positions, transparently initializes the context if still in `zcss_init`, performs stable-buffer checks, calls the generic compressor, and returns bytes still buffered for flushing.
- `ZSTD_compressStream2_simpleArgs()` adapts pointer/position arguments into `ZSTD_inBuffer` and `ZSTD_outBuffer`.
- `ZSTD_compress2()` implements the one-shot CCtx API by resetting the session, temporarily enabling stable input/output buffers, running `ZSTD_compressStream2_simpleArgs(..., ZSTD_e_end)`, restoring requested buffer modes, and returning the final output position.
- `ZSTD_validateSequence()` checks supplied sequence offsets and match lengths against current decode position, window size, dictionary size, `minMatch`, and whether an external sequence producer is active.
- `ZSTD_finalizeOffBase()` converts raw offsets into internal offBase values, using the current repcode triplet and the zero-literals special case.
- `ZSTD_transferSequences_wBlockDelim()` copies public sequences into `seqStore` until an explicit block delimiter `(matchLength == 0 && offset == 0)`, optionally validates them, stores block-ending literals, and updates next-block repcodes.
- `ZSTD_transferSequences_noDelim()` copies sequences when delimiters are absent, splitting or backing off from a sequence when the target block boundary would create an invalid match fragment.
- `ZSTD_selectSequenceCopier()`, `blockSize_explicitDelimiter()`, and `determine_blockSize()` select block-delimited versus target-block-size sequence parsing and validate explicit block sizes.
- `ZSTD_compressSequences_internal()` builds compressed, raw, or RLE blocks from a source buffer plus external sequences, including block headers and block-state entropy transitions.
- `ZSTD_compressSequences()` is the public frame wrapper for source-backed sequence compression. It initializes the CCtx, writes the frame header, optionally updates the XXH64 checksum, compresses blocks, and appends the checksum.
- `convertSequences_noRepcodes()` has AVX2 and scalar implementations that convert `ZSTD_Sequence` entries into `SeqDef` entries when repcode resolution is disabled, while detecting long literal or match lengths.
- `ZSTD_convertBlockSequences()` converts one explicit-delimiter block for the literals-only API. It uses the fast no-repcode conversion path or resolves repcodes sequence-by-sequence.
- `ZSTD_get1BlockSummary()` summarizes one explicit-delimiter block by returning sequence count, block size, and literal size. It also has AVX2 and scalar implementations.
- `ZSTD_compressSequencesAndLiterals_internal()` compresses blocks from public sequences plus a separate literals buffer, without access to the reconstructed source.
- `ZSTD_compressSequencesAndLiterals()` is the public frame wrapper for the literals-only sequence API. It requires explicit block delimiters, rejects validation and frame checksums, writes the frame header, and calls the literals-only block compressor.
- `inBuffer_forEndFlush()`, `ZSTD_flushStream()`, and `ZSTD_endStream()` finalize a stream using either null input or the remembered stable input buffer.
- `ZSTD_maxCLevel()`, `ZSTD_minCLevel()`, and `ZSTD_defaultCLevel()` expose compression-level bounds from `clevels.h`.
- `ZSTD_dedicatedDictSearch_getCParams()`, `ZSTD_dedicatedDictSearch_isSupported()`, and `ZSTD_dedicatedDictSearch_revertCParams()` adjust compression parameters for dedicated dictionary search in lazy strategies.
- `ZSTD_getCParams_internal()`, `ZSTD_getCParams()`, `ZSTD_getParams_internal()`, and `ZSTD_getParams()` map compression level, source size, dictionary size, and dictionary attach mode to concrete compression and frame parameters.
- `ZSTD_registerSequenceProducer()` and `ZSTD_CCtxParams_registerSequenceProducer()` install or clear external sequence producer state/function pointers on a context or parameter object.

Relevant internal state lives in `ZSTD_CCtx_s` and `ZSTD_CCtx_params_s` from `zstd_compress_internal.h`: `requestedParams`, `appliedParams`, `blockSizeMax`, `pledgedSrcSizePlusOne`, streaming buffers/cursors, `streamStage`, `frameEnded`, stable-buffer expectations, `seqStore`, `blockState`, `tmpWorkspace`, dictionary references, `blockDelimiters`, `validateSequences`, and `searchForExternalRepcodes`.

## Control Flow

`ZSTD_compressStream2()` begins by checking that input/output positions are within buffer sizes and the end directive is valid. If the context is still in `zcss_init`, it may delay full initialization for stable input when the caller provides less than one block and requests `ZSTD_e_continue`. In that delayed path it records the stable buffer, pretends the input was consumed, accumulates `stableIn_notConsumed`, and returns the minimum frame-header size as a progress hint.

Otherwise, initialization is delegated to `ZSTD_CCtx_init_compressStream2()`. This function snapshots requested params and a one-use prefix dictionary, initializes local dictionaries, clears `prefixDict`, lets a true CDict compression level override requested level, resolves effective cParams and advanced switches, and calls `ZSTD_compressBegin_internal()`. It then sets `inToCompress`, `inBuffPos`, `inBuffTarget`, `outBuffContentSize`, `outBuffFlushedSize`, `streamStage = zcss_load`, and `frameEnded = 0`.

After initialization, `ZSTD_compressStream2()` validates stable input/output contracts and calls `ZSTD_compressStream_generic()`. The generic function adjusts stable-input bookkeeping first, then loops over `streamStage`. In `zcss_load`, an end directive with enough destination capacity and no buffered input takes the direct `ZSTD_compressEnd_public()` shortcut into the caller's output buffer. Otherwise buffered input is filled up to `inBuffTarget`, or stable input is used directly up to `blockSizeMax`.

When enough input or a flush/end directive is present, the current block is compressed with `ZSTD_compressContinue_public()` or `ZSTD_compressEnd_public()`. If caller output has enough space, compression goes directly to `output->dst`; otherwise it goes to `outBuff` and falls through to `zcss_flush`. The flush stage copies `outBuffContentSize - outBuffFlushedSize` bytes to the caller output and either stops on a full destination or returns to `zcss_load` after the internal output is fully drained. Frame completion resets the session-only state.

`ZSTD_flushStream()` and `ZSTD_endStream()` are thin wrappers over `ZSTD_compressStream2()`. They synthesize an input buffer with no new data to ingest. In stable-input mode that buffer is the saved expected input buffer, which lets pending unconsumed stable bytes remain addressable. `ZSTD_endStream()` returns the pending flush amount and, in single-thread mode, adds an estimate for a final empty block header and checksum when the frame has not yet ended.

The sequence-backed path starts at `ZSTD_compressSequences()`. It initializes a complete frame, writes a frame header, updates frame checksum state if enabled, then calls `ZSTD_compressSequences_internal()`. The internal function repeatedly determines the next block size, resets `seqStore`, copies public sequences into internal sequence storage using either the explicit-delimiter or no-delimiter copier, then entropy-compresses the sequence store. It emits raw blocks for very small or incompressible blocks, RLE blocks for repeat-byte blocks after the first block, or compressed blocks with a 24-bit block header and confirmed entropy/repcodes.

The literals-only path starts at `ZSTD_compressSequencesAndLiterals()`. It initializes the context as a one-shot end frame, rejects no-delimiter mode, rejects sequence validation, and rejects checksums because it does not have the full source bytes. Its internal loop uses `ZSTD_get1BlockSummary()` to find each explicit-delimiter block, converts public sequences with `ZSTD_convertBlockSequences()`, consumes the matching slice of the literals buffer, and calls `ZSTD_entropyCompressSeqStore_internal()`. Unlike the source-backed path, it cannot emit raw fallback blocks because the original source is unavailable, so an incompressible result returns `cannotProduce_uncompressedBlock`.

Compression-level lookup is table driven. `ZSTD_getCParams_internal()` computes a row-size bucket from source size, dictionary size, and attach mode, clamps or defaults the requested level, reads `ZSTD_defaultCParameters[tableID][row]`, applies negative-level acceleration through `targetLength`, and calls `ZSTD_adjustCParams_internal()`. `ZSTD_getParams_internal()` wraps those cParams into `ZSTD_parameters` with content-size flag enabled.

## State and Persistence Behavior

`ZSTD_CCtx` is stateful across streaming calls. The stream stage, input buffer positions, output flush positions, `frameEnded`, stable-buffer expectations, block state, entropy tables, repcodes, checksum state, dictionary references, and workspace-backed sequence storage are all mutated as compression progresses.

Session completion calls `ZSTD_CCtx_reset(cctx, ZSTD_reset_session_only)` in several paths. That reset is intentionally session-scoped: sticky requested parameters, dictionaries configured for future sessions, and context allocation are not freed as part of normal stream completion.

Stable input mode intentionally lies to the caller about progress for sub-block `ZSTD_e_continue` calls before initialization. It advances `input->pos` to `input->size` but stores `stableIn_notConsumed` so later initialization can compress those bytes from the same stable source address. Subsequent calls must use the same `input->src` and expected position, or `stabilityCondition_notRespected` is returned.

Buffered streaming owns `inBuff` and `outBuff` inside the CCtx. Input may persist in `inBuff` between calls until a block is complete or a flush/end directive arrives. Output may persist in `outBuff` when the caller destination is too small; `ZSTD_compressStream2()` reports the remaining flush amount as `outBuffContentSize - outBuffFlushedSize`.

Sequence compression mutates `seqStore`, `blockState.prevCBlock`, `blockState.nextCBlock`, repeat-mode metadata, repcodes, and `isFirstBlock`. `ZSTD_blockState_confirmRepcodesAndEntropyTables()` commits the next block's entropy and repcode state after a compressed block is accepted.

`ZSTD_registerSequenceProducer()` stores `extSeqProdFunc` and `extSeqProdState` in `requestedParams`. Passing a null function clears both fields. The state pointer is not owned or freed here; the caller must keep it valid for compression sessions that use it.

Compression parameter lookup functions are pure with respect to context state, except dedicated dictionary helpers operate on passed `ZSTD_compressionParameters` values. They derive parameters from static tables in `clevels.h` and from supplied size hints.

## Dependencies and Integration Points

- Public zstd APIs and types from the surrounding library: `ZSTD_CCtx`, `ZSTD_CStream`, `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_EndDirective`, `ZSTD_Sequence`, `ZSTD_parameters`, `ZSTD_compressionParameters`, and `ZSTD_sequenceProducer_F`.
- Internal compression helpers from this file and sibling zstd compression modules: `ZSTD_compressBegin_internal()`, `ZSTD_compressContinue_public()`, `ZSTD_compressEnd_public()`, `ZSTD_writeFrameHeader()`, `ZSTD_noCompressBlock()`, `ZSTD_rleCompressBlock()`, `ZSTD_entropyCompressSeqStore()`, `ZSTD_entropyCompressSeqStore_internal()`, and `ZSTD_adjustCParams_internal()`.
- Internal state/types from `zstd_compress_internal.h`: `ZSTD_CCtx_s`, `ZSTD_CCtx_params_s`, `SeqStore_t`, `SeqDef`, `Repcodes_t`, `ZSTD_SequencePosition`, `BlockSummary`, `ZSTD_bufferMode_e`, `ZSTD_SequenceFormat_e`, and `ZSTD_ParamSwitch_e`.
- Memory and bit helpers: `ZSTD_memcpy()`, `ZSTD_memset()`, `ZSTD_limitCopy()`, `MEM_writeLE24()`, `MEM_writeLE32()`, `OFFSET_TO_OFFBASE()`, `REPCODE*_TO_OFFBASE`, and `ZSTD_updateRep()`.
- Error/logging/assertion macros: `RETURN_ERROR()`, `RETURN_ERROR_IF()`, `FORWARD_IF_ERROR()`, `ERROR()`, `DEBUGLOG()`, `assert()`, `UNLIKELY()`, and `ZSTD_STATIC_ASSERT()`.
- Checksum integration through `xxh64_update()` and `xxh64_digest()` for `ZSTD_compressSequences()` when frame checksums are enabled.
- Architecture-specific acceleration through AVX2 intrinsics when `__AVX2__` or `ZSTD_ARCH_X86_AVX2` is defined. The scalar paths are always available.
- `clevels.h` supplies `ZSTD_defaultCParameters` and compression-level constants used by `ZSTD_getCParams_internal()`.
- In this source tree, `sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c` calls `ZSTD_CCtxParams_registerSequenceProducer()`, `ZSTD_registerSequenceProducer()`, and `ZSTD_compressSequencesAndLiterals()`, so this chunk is part of the module-level bridge for external sequence producers.

## Risks and Edge Cases

- The direct end shortcut in `ZSTD_compressStream_generic()` depends on `ZSTD_compressBound()` or stable output mode to avoid partial direct writes. Any change to the condition can break callers that expect buffered flushing when destination capacity is small.
- Stable input mode has strict pointer and position requirements. A caller that reallocates or mutates the input buffer after earlier calls can trigger `stabilityCondition_notRespected` or, worse, compress changed bytes if checks are weakened.
- `stableIn_notConsumed` is subtracted from `input->pos` before compression. Incorrect bookkeeping around this field can underflow positions or duplicate/drop bytes.
- Stable output mode validates only remaining output capacity (`output->size - output->pos`), not the destination pointer. This matches the local contract but requires callers to keep the underlying buffer stable enough for direct compression.
- The streaming compressor treats each block compression as non-interruptible. If a lower-level compression call returns an error after stable input has advanced, the caller observes positions adjusted to mirror buffered mode.
- `ZSTD_compress2()` temporarily overwrites requested buffer modes and restores them only after `ZSTD_compressStream2_simpleArgs()` returns. The code restores before forwarding errors, which is important for reusing the CCtx after failure.
- External sequences must exactly describe the source data. Delimiter mode requires a delimiter for every block and rejects blocks larger than `blockSizeMax` or longer than remaining source. No-delimiter mode must avoid invalid match splits and can reduce the consumed byte count below the target block size.
- `ZSTD_validateSequence()` relies on the cumulative decoded position, window log, dictionary size, and `minMatch`. Incorrect `dictSize` discovery for CDict versus prefix dict would reject valid offsets or allow invalid ones.
- When `searchForExternalRepcodes` is disabled, repcodes are updated in a fast approximation from the last raw offsets. That path must stay consistent with decoder expectations even though sequence parsing skipped per-sequence repcode resolution.
- `convertSequences_noRepcodes()` encodes long length position as a single `size_t` marker. It asserts only one long length is found; malformed sequences with multiple long fields depend on assertions in debug builds and later encoding behavior in release builds.
- AVX2 conversion and summary paths depend on exact struct sizes and field offsets. The static asserts protect layout drift, but build flags must agree with available CPU support and compiler intrinsic support.
- `ZSTD_compressSequencesAndLiterals()` cannot emit raw fallback blocks. Inputs that entropy-compress to size zero, or to larger than max block size, become `cannotProduce_uncompressedBlock` even though the equivalent source-backed path could emit raw bytes.
- The literals-only API checks `litCapacity < litSize` but the error text mentions an 8-byte margin. The actual guard in this chunk does not enforce that margin, so callers must follow the broader API contract if later entropy code may overread padded literals.
- `ZSTD_compressSequencesAndLiterals()` rejects checksums because full source bytes are absent. Enabling checksums there without reconstructing the original source would produce invalid frames.
- Empty-frame handling differs slightly between sequence paths: source-backed code checks `dstCapacity < 4` while writing a 3-byte block header through `MEM_writeLE32()`, and literals-only code checks `<3` and writes `MEM_writeLE24()`. This is intentional-looking but worth preserving carefully.
- `ZSTD_endStream()` has a multi-thread branch even though `ZSTD_CCtx_init_compressStream2()` asserts `nbWorkers == 0` in this path. Future merge/reconciliation should check earlier/later MT sections before generalizing behavior.
- Compression-level row selection treats public `srcSizeHint == 0` as unknown in wrappers, but internal `ZSTD_getCParams_internal()` treats zero as a real zero-size hint. Callers must choose the right entry point.
- `ZSTD_getCParamRowSize()` adds 500 bytes for unknown source size with a dictionary. This heuristic affects table bucket selection and can change compression ratio/performance if altered.

## Test Signals

- Streaming regression tests should cover `ZSTD_compressStream2()` with all three directives: continue with sub-block input, flush with no new input, and end with both enough and insufficient output capacity.
- Stable input tests should verify the delayed-initialization path: repeated sub-block `ZSTD_e_continue` calls must report progress, then `ZSTD_e_flush` or `ZSTD_e_end` must compress the accumulated bytes exactly once.
- Stable-buffer negative tests should change `input->src`, externally alter `input->pos`, or change remaining output capacity and expect `stabilityCondition_notRespected`.
- Buffered output tests should force `zcss_flush` by using a destination smaller than `ZSTD_compressBound(blockSize)`, then repeatedly call flush/end until `outBuffContentSize - outBuffFlushedSize` reaches zero.
- `ZSTD_compress2()` should be tested with small destination capacity to confirm it returns `dstSize_tooSmall` and restores the original requested buffer modes afterward.
- External sequence tests should include explicit block delimiters, missing delimiters, too-large explicit blocks, source-length mismatches, small blocks that force raw output, RLE-eligible blocks after the first block, and checksum-enabled `ZSTD_compressSequences()`.
- No-delimiter sequence tests should exercise block boundaries inside literals, inside matches, and near `minMatch` to catch split/backoff mistakes.
- Validation tests should cover offsets beyond window/dictionary bounds and match lengths below the lower bound for normal and external-producer modes.
- Repcode tests should compare frames produced with `searchForExternalRepcodes` enabled and disabled, especially zero-literal sequences and the `rep[0] - 1` special case.
- Literals-only sequence tests should verify the required explicit delimiter mode, rejection of validation/checksum settings, exact literal consumption, exact decompressed-size accounting, and expected failure for incompressible blocks where raw fallback would be needed.
- AVX2 and scalar builds should produce byte-identical compressed output for the same external sequence inputs. Struct-layout static assertions are compile-time signals; runtime cross-build corpus checks catch logic drift.
- Compression-level tests should check level `0`, negative levels below the minimum clamp, levels above `ZSTD_MAX_CLEVEL`, unknown source size, zero source size through internal callers, dictionary attach versus create modes, and dedicated dictionary-search eligibility.
- Integration tests in `zstd_compress_module.c` should verify that registered sequence producers are called, that clearing a producer nulls both function and state, and that `ZSTD_compressSequencesAndLiterals()` frames decompress to the producer-described source.

## Chunk Boundary Notes

The first three lines are the tail of `ZSTD_initCStream()` from the preceding chunk. The declarations of `ZSTD_CCtx`, stream-stage enums, sequence structs, error macros, and most helper routines are outside this range and should be described in the final merged file report with their defining chunks.

This chunk is the main single-threaded API/control-flow section for `zstd_compress.c`. Later chunks continue after sequence-producer registration, so the final report should connect this section's parameter lookup and registration APIs to the rest of CDict creation, simple API wrappers, and module exports.
