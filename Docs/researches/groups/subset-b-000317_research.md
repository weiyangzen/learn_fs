# subset-b-000317 research

This grouped report covers zstd decompression internals and the deprecated ZBUFF streaming compatibility layer. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress.c -->
# sources/compression/zstd/lib/decompress/zstd_decompress.c

## Purpose
`zstd_decompress.c` is the main frame-level decompression implementation for libzstd. It owns decompression context lifecycle, frame and skippable-frame parsing, dictionary attachment, single-shot decompression, bufferless decompression, buffered streaming decompression, parameter handling, and checksum/window enforcement.

## Important APIs, Types, And Functions
Context APIs include `ZSTD_createDCtx`, `ZSTD_createDCtx_advanced`, `ZSTD_initStaticDCtx`, `ZSTD_freeDCtx`, `ZSTD_sizeof_DCtx`, `ZSTD_DCtx_reset`, `ZSTD_DCtx_setParameter`, and `ZSTD_DCtx_getParameter`. Frame-inspection APIs include `ZSTD_isFrame`, `ZSTD_isSkippableFrame`, `ZSTD_frameHeaderSize`, `ZSTD_getFrameHeader_advanced`, `ZSTD_getFrameContentSize`, `ZSTD_findFrameCompressedSize`, `ZSTD_decompressBound`, and `ZSTD_decompressionMargin`. Decode APIs include `ZSTD_decompress`, `ZSTD_decompressDCtx`, `ZSTD_decompress_usingDict`, `ZSTD_decompress_usingDDict`, `ZSTD_decompressContinue`, and `ZSTD_decompressStream`. Dictionary APIs include `ZSTD_decompressBegin_usingDict`, `ZSTD_decompressBegin_usingDDict`, `ZSTD_loadDEntropy`, `ZSTD_DCtx_loadDictionary`, `ZSTD_DCtx_refDDict`, `ZSTD_DCtx_refPrefix`, `ZSTD_getDictID_fromDict`, and `ZSTD_getDictID_fromFrame`. Internal `ZSTD_DDictHashSet_*` helpers support contexts that reference multiple prepared dictionaries by dictID.

## Control Flow
Single-shot decompression enters `ZSTD_decompressMultiFrame()`, skips skippable frames, optionally dispatches to legacy support, initializes the context with a raw dictionary or DDict, and calls `ZSTD_decompressFrame()` for each zstd frame. `ZSTD_decompressFrame()` decodes the frame header, optionally clamps max block size, loops over block headers, and dispatches compressed blocks to `ZSTD_decompressBlock_internal()`, raw blocks to `ZSTD_copyRawBlock()`, and RLE blocks to `ZSTD_setRleBlock()`. At frame end it validates declared content size and the optional XXH64 checksum. The bufferless path `ZSTD_decompressContinue()` is an exact-byte state machine over frame-header-size, full frame header, block header, block body, checksum, and skippable-frame states. The buffered `ZSTD_decompressStream()` adds a higher-level stream state machine for header loading, input buffering, direct decode, output flushing, stable-output-buffer enforcement, and no-forward-progress detection.

## State And Persistence
All persistent decode state lives in `ZSTD_DCtx`: frame parameters, decode stage, expected input size, entropy tables, repcodes, prefix/virtual/dictionary history pointers, checksum state, input/output ring buffers, literal scratch buffers, loaded dictionaries, multiple-DDict hash set, stream stage, oversized-buffer duration, and no-forward-progress counters. The module does not write filesystem state. Context parameters and loaded dictionaries survive across sessions until reset or replaced; `ZSTD_use_once` prefixes are consumed by the next decompression while `ZSTD_use_indefinitely` dictionaries persist. Streaming output history is preserved by `previousDstEnd`, `prefixStart`, `virtualStart`, and `dictEnd`, and `ZSTD_checkContinuity()` converts non-contiguous output into external dictionary history.

## Dependencies And Integration Points
This file depends on common zstd helpers for memory, allocation, errors, bit constants, FSE/HUF declarations, xxhash, DDict accessors, and `zstd_decompress_block.h`. It is the public decompression surface exposed through `zstd.h` and feeds compressed block bodies to `zstd_decompress_block.c`. It also integrates optional legacy frame support, optional trace hooks, dynamic BMI2 detection, custom allocators, and static-workspace mode.

## Risks
High-risk areas are exact size accounting for headers, skippable payloads, block bodies, checksums, and multi-frame trailing bytes; output/input overlap during in-place decompression; maintaining valid history windows across non-contiguous output buffers; dictionary ID selection when multiple DDicts are referenced; static context buffer sizing; window-size rejection before allocation; stable-output-buffer semantics; and the hostage-byte/no-forward-progress logic that prevents streaming callers from stalling silently. The DDict hash set uses open addressing and assumes non-NULL entries are only probed after allocation; changes must preserve replacement and resize behavior.

## Test Signals
Useful tests include round trips through `ZSTD_decompress()` and `ZSTD_decompressStream()`, fragmented headers and block inputs for `ZSTD_decompressContinue()`, skippable-frame-only and mixed-frame streams, wrong dictionary ID failures, raw/RLE/compressed block combinations, frame content size mismatches, checksum mismatch and checksum-ignore modes, max-window/max-block rejection, stable output buffer misuse, in-place decompression margin cases, static DCtx allocation limits, and multiple-DDict selection by dictID.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_block.c -->
# sources/compression/zstd/lib/decompress/zstd_decompress_block.c

## Purpose
`zstd_decompress_block.c` implements decoding for compressed zstd blocks. It parses compressed block headers and literal sections, builds or reuses FSE sequence tables, decodes literal-length/match-length/offset sequences from the bitstream, executes matches against current prefix or external dictionary history, and updates block-to-block entropy and repcode state.

## Important APIs, Types, And Functions
Public/internal entry points are `ZSTD_getcBlockSize()`, `ZSTD_decodeSeqHeaders()`, `ZSTD_buildFSETable()`, `ZSTD_decompressBlock_internal()`, `ZSTD_checkContinuity()`, `ZSTD_decompressBlock_deprecated()`, and `ZSTD_decompressBlock()`. Important internal helpers include `ZSTD_decodeLiteralsBlock()`, `ZSTD_allocateLiteralsBuffer()`, `ZSTD_buildSeqTable()`, `ZSTD_decodeSequence()`, `ZSTD_execSequence()`, `ZSTD_execSequenceEnd()`, split-literal-buffer variants, long-offset/prefetch sequence decoders, and `ZSTD_getOffsetInfo()`. Local state types include `seq_t`, `ZSTD_fseState`, `seqState_t`, and `ZSTD_OffsetInfo`.

## Control Flow
`ZSTD_decompressBlock_internal()` first rejects compressed block sizes above the active max block size, decodes the literals section, then decodes sequence headers and FSE tables. Literal decoding handles `set_basic`, `set_rle`, `set_compressed`, and `set_repeat`, placing literals either in the destination tail, in `litExtraBuffer`, or split across both to avoid overwriting history during streaming. Sequence-header decoding reads the sequence count, parses table encoding modes for LL/OF/ML, and builds or points to default/repeated/RLE FSE tables. The block entry point then determines whether 32-bit long-offset handling or prefetch decoding is needed and dispatches to the regular, split-literal, or long/prefetch sequence loop. Sequence loops decode symbols, copy literals, copy matches from prefix or extDict, flush remaining literals, verify bitstream completion, and save repcodes back to the context.

## State And Persistence
The block decoder mutates the caller's `ZSTD_DCtx`: literal buffer pointers and location, `litEntropy`, `fseEntropy`, HUF/FSE table pointers, entropy tables, `entropy.rep`, `ddictIsCold`, and history pointers through `ZSTD_checkContinuity()`. It persists no external state. Default FSE tables are static constants. Repeated literal and sequence tables depend on prior blocks or dictionaries; therefore caller ordering and context reuse are semantically significant.

## Dependencies And Integration Points
This module depends on common memory, compiler, FSE, HUF, bit, and zstd internal helpers plus `zstd_decompress_internal.h`. It is called by frame-level code for `bt_compressed` blocks and by the deprecated block API. It shares literal-buffer allocation policy with streaming frame decompression and consumes dictionary-loaded entropy tables from `ZSTD_loadDEntropy()` in `zstd_decompress.c`.

## Risks
The main risks are pointer arithmetic near buffer ends, 32-bit address-space overflow, wildcopy overread/overwrite assumptions, split literal-buffer transitions, validating offsets against prefix plus external dictionary history, repeated-table use before initialization, last-sequence FSE state handling, and differences between 32-bit long-offset decoding and 64-bit decoding. Performance-sensitive alignment and prefetch code should be changed carefully because it can alter decoder speed without changing behavior.

## Test Signals
Important signals are successful decode of blocks using all literal encodings and sequence table encodings, repeat-table behavior across block boundaries and dictionaries, corrupt headers producing zstd errors rather than overreads, offsets that cross from extDict into prefix, near-end literals and matches, small-offset overlap copies, long-distance matches on 32-bit-sensitive configurations, cold-DDict prefetch path coverage, and block API continuity across consecutive `ZSTD_decompressBlock()` calls.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_block.h -->
# sources/compression/zstd/lib/decompress/zstd_decompress_block.h

## Purpose
`zstd_decompress_block.h` is the internal interface for compressed-block decompression. It exposes the block decoder and FSE table builder to frame-level decompression and dictionary-loading code while keeping implementation details in `zstd_decompress_block.c`.

## Important APIs, Types, And Functions
The header defines `streaming_operation` with `not_streaming` and `is_streaming`, declares `ZSTD_decompressBlock_internal()`, declares `ZSTD_buildFSETable()`, and declares `ZSTD_decompressBlock_deprecated()` as the internal wrapper behind the deprecated public block API. It also documents that `ZSTD_decompressBlock()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()` are published elsewhere.

## Control Flow
There is no runtime control flow in the header. It determines how callers distinguish streaming from non-streaming literal-buffer allocation and gives frame decompression a single entry point for `bt_compressed` blocks.

## State And Persistence
The declared functions operate on `ZSTD_DCtx`; state is held by the context and by caller-owned buffers. The header itself contains no persistent state.

## Dependencies And Integration Points
It includes zstd dependency definitions, public `zstd.h`, common internal block types, and `zstd_decompress_internal.h` for `ZSTD_seqSymbol`. It is included by `zstd_decompress.c` and `zstd_decompress_block.c`, and `ZSTD_buildFSETable()` is also used when dictionaries load their precomputed entropy tables.

## Risks
Changing the `streaming_operation` contract can break literal placement and streaming history safety. Changing prototypes affects internal ABI expectations across decompression and dictionary modules. Workspace sizing for `ZSTD_buildFSETable()` must remain consistent with `ZSTD_BUILD_FSE_TABLE_WKSP_SIZE`.

## Test Signals
Compile coverage is the main direct signal. Behavioral signals come from frame decompression, dictionary-loading tests, block API tests, and streaming tests that exercise both `is_streaming` and `not_streaming` paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_internal.h -->
# sources/compression/zstd/lib/decompress/zstd_decompress_internal.h

## Purpose
`zstd_decompress_internal.h` defines shared decompression tables, internal decode types, context state, and helper prototypes used across zstd decompression modules. It is the structural contract between frame decoding, block decoding, dictionary handling, and streaming.

## Important APIs, Types, And Functions
Static base/additional-bit tables `LL_base`, `OF_base`, `OF_bits`, and `ML_base` define sequence symbol interpretation. Key types are `ZSTD_seqSymbol_header`, `ZSTD_seqSymbol`, `ZSTD_entropyDTables_t`, `ZSTD_dStage`, `ZSTD_dStreamStage`, `ZSTD_dictUses_e`, `ZSTD_DDictHashSet`, `ZSTD_litLocation_e`, and the full `struct ZSTD_DCtx_s`. It also defines table/workspace sizing macros, literal extra buffer sizing, `ZSTD_DCtx_get_bmi2()`, and prototypes for `ZSTD_loadDEntropy()` and `ZSTD_checkContinuity()`.

## Control Flow
This header has no executable flow beyond the inline BMI2 accessor. Its enums encode the control-flow states used by `ZSTD_decompressContinue()` and `ZSTD_decompressStream()`: frame header sizing, frame header decode, block header decode, block decompression, last block, checksum, skippable header, skippable payload, stream initialization, header loading, reading, loading, and flushing.

## State And Persistence
`ZSTD_DCtx_s` is the persistent decompression state container. It stores entropy tables and pointers, history boundaries, expected input size, frame parameters, block type, checksum state, dictionary pointers and use policy, multiple-DDict set, streaming buffers and positions, legacy stream state, output-buffer stability data, literal buffers, oversized-buffer tracking, optional fuzzing dictionary bounds, and optional trace context. State persists across streaming calls and selected resets according to `ZSTD_DCtx_reset()` semantics.

## Dependencies And Integration Points
The header depends on common memory and zstd internal constants plus HUF/XXH types pulled through those includes. It is consumed by both decompression C files and by DDict support code. Its layout affects static context sizing, workspace sharing between FSE and HUF table construction, and the public opaque `ZSTD_DCtx`/`ZSTD_DStream` objects declared in `zstd.h`.

## Risks
Layout and sizing changes can break static allocation, table workspace assumptions, or dictionary table reuse. The literal extra buffer size balances memory against safety for split literals. History pointer fields must stay coherent with `ZSTD_checkContinuity()` and external dictionary matching. New fields need reset, copy, size-accounting, and static-workspace consideration.

## Test Signals
Compilation across decompression modules, static DCtx/DStream tests, dictionary round trips, streaming fragmented-input tests, checksum tests, repeated entropy-table tests, and fuzzing builds with sequence assertions all exercise this contract.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_decompress_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff.h -->
# sources/compression/zstd/lib/deprecated/zbuff.h

## Purpose
`zbuff.h` declares the deprecated buffered streaming API that predates the current `ZSTD_CStream` and `ZSTD_DStream` APIs. It preserves source compatibility while directing users to modern `zstd.h` functions through deprecation attributes and comments.

## Important APIs, Types, And Functions
`ZBUFF_CCtx` aliases `ZSTD_CStream` and `ZBUFF_DCtx` aliases `ZSTD_DStream`. Compression APIs include `ZBUFF_createCCtx`, `ZBUFF_freeCCtx`, `ZBUFF_compressInit`, `ZBUFF_compressInitDictionary`, `ZBUFF_compressContinue`, `ZBUFF_compressFlush`, and `ZBUFF_compressEnd`. Decompression APIs include `ZBUFF_createDCtx`, `ZBUFF_freeDCtx`, `ZBUFF_decompressInit`, `ZBUFF_decompressInitDictionary`, and `ZBUFF_decompressContinue`. Tool APIs include `ZBUFF_isError`, `ZBUFF_getErrorName`, and recommended buffer size helpers. Static-linking-only declarations expose advanced custom-memory creation and `ZBUFF_compressInit_advanced()`.

## Control Flow
The header describes the intended streaming flow: create a context, initialize for compression or decompression, repeatedly continue with arbitrary caller buffer sizes, flush or end compression when needed, and free the context. For decompression, return values distinguish complete frame, pending internal output, desired next input size, and errors.

## State And Persistence
The API state is the underlying `ZSTD_CStream` or `ZSTD_DStream`; the header introduces no independent state. Contexts can be reused after reinitialization. User-provided dictionaries must remain valid according to the underlying modern API behavior selected by wrapper implementations.

## Dependencies And Integration Points
It includes `stddef.h` and `../zstd.h`, and all implementation files in `lib/deprecated` include it. The deprecation macro maps to C++14 attributes, GCC/Clang attributes, MSVC declspec, or plain `ZSTDLIB_API` when warnings are disabled or unsupported.

## Risks
The file is compatibility-sensitive: changing typedefs, signatures, return semantics, or deprecation macros can break old applications. The static-linking-only section must not imply stable dynamic ABI. Comments document older `0 == unknown` pledged-size behavior that wrappers preserve.

## Test Signals
Strong signals are successful compilation of legacy callers, warning behavior with and without `ZBUFF_DISABLE_DEPRECATE_WARNINGS`, streaming round trips through ZBUFF wrappers, dictionary compression/decompression, custom allocator creation, and recommended-size helpers matching current ZSTD stream helpers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_common.c -->
# sources/compression/zstd/lib/deprecated/zbuff_common.c

## Purpose
`zbuff_common.c` implements the deprecated ZBUFF error helper functions by forwarding to libzstd's shared error subsystem.

## Important APIs, Types, And Functions
It defines `ZBUFF_isError(size_t errorCode)` and `ZBUFF_getErrorName(size_t errorCode)`. Both are thin wrappers over `ERR_isError()` and `ERR_getErrorName()`.

## Control Flow
Each function performs a single direct call into `error_private.h` helpers and returns the result. There is no branching beyond the underlying error helper behavior.

## State And Persistence
No state is stored or persisted. Results depend only on the numeric zstd error code passed by the caller.

## Dependencies And Integration Points
The file includes `../common/error_private.h` and `zbuff.h`. It provides compatibility symbols for legacy users who still call ZBUFF error helpers after using deprecated compression or decompression wrappers.

## Risks
The main compatibility risk is preserving the exact wrapper names and return types. Any divergence from `ZSTD_isError`/`ZSTD_getErrorName` behavior would surprise legacy callers.

## Test Signals
Tests should verify that known success values are not errors, known zstd error codes are errors, and returned names match the modern ZSTD error-name helper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_compress.c -->
# sources/compression/zstd/lib/deprecated/zbuff_compress.c

## Purpose
`zbuff_compress.c` implements deprecated ZBUFF compression APIs as compatibility wrappers around the modern `ZSTD_CStream`/`ZSTD_CCtx` streaming compression API.

## Important APIs, Types, And Functions
Context wrappers are `ZBUFF_createCCtx()`, `ZBUFF_createCCtx_advanced()`, and `ZBUFF_freeCCtx()`. Initialization wrappers are `ZBUFF_compressInit()`, `ZBUFF_compressInitDictionary()`, and `ZBUFF_compressInit_advanced()`. Streaming wrappers are `ZBUFF_compressContinue()`, `ZBUFF_compressFlush()`, and `ZBUFF_compressEnd()`. Buffer-size helpers are `ZBUFF_recommendedCInSize()` and `ZBUFF_recommendedCOutSize()`.

## Control Flow
Creation and free forward directly to `ZSTD_createCStream*` and `ZSTD_freeCStream()`. Basic init forwards to `ZSTD_initCStream()`. Dictionary init resets the session, sets compression level, loads the dictionary, and returns zero on success. Advanced init preserves historical `pledgedSrcSize == 0` as unknown, resets the session, sets pledged size, validates and applies compression parameters, applies frame parameters, loads the dictionary, and returns zero. Continue/flush/end wrappers construct `ZSTD_outBuffer` and `ZSTD_inBuffer` shims, call the corresponding ZSTD stream function, then write consumed/produced byte counts back through legacy pointer arguments.

## State And Persistence
All state lives in the underlying `ZSTD_CStream`. Initialization changes session parameters, pledged size, frame flags, and loaded dictionary state. Continue/flush/end mutate stream progress and buffered output through the ZSTD API. The wrapper file stores no global or static mutable state.

## Dependencies And Integration Points
It defines `ZBUFF_STATIC_LINKING_ONLY`, includes `zbuff.h`, and uses `error_private.h` for `FORWARD_IF_ERROR`. It bridges old applications to current compression APIs and must remain consistent with the typedef that makes `ZBUFF_CCtx` a `ZSTD_CStream`.

## Risks
Pointer out-parameters must always be updated to the actual consumed/produced counts, including partial-progress cases. Advanced init must keep old pledged-size semantics and correctly map deprecated `ZSTD_parameters` fields to modern individual parameters. Because wrappers forward errors directly, callers must continue using `ZBUFF_isError()`/`ZSTD_isError()` on returned `size_t` values.

## Test Signals
Round-trip tests through `ZBUFF_compressContinue()` plus modern decompression are the key signal. Additional coverage should include tiny output buffers, repeated flush calls, end-stream completion, dictionary init, advanced init with `pledgedSrcSize == 0`, invalid compression parameters, custom allocators, and recommended sizes matching `ZSTD_CStreamInSize()`/`ZSTD_CStreamOutSize()`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_decompress.c -->
# sources/compression/zstd/lib/deprecated/zbuff_decompress.c

## Purpose
`zbuff_decompress.c` implements deprecated ZBUFF decompression APIs as compatibility wrappers around the modern `ZSTD_DStream` streaming decompression API.

## Important APIs, Types, And Functions
Context wrappers are `ZBUFF_createDCtx()`, `ZBUFF_createDCtx_advanced()`, and `ZBUFF_freeDCtx()`. Initialization wrappers are `ZBUFF_decompressInit()` and `ZBUFF_decompressInitDictionary()`. The streaming wrapper is `ZBUFF_decompressContinue()`. Buffer-size helpers are `ZBUFF_recommendedDInSize()` and `ZBUFF_recommendedDOutSize()`.

## Control Flow
Creation/free forward directly to `ZSTD_createDStream*` and `ZSTD_freeDStream()`. Initialization forwards to `ZSTD_initDStream()` or `ZSTD_initDStream_usingDict()`. `ZBUFF_decompressContinue()` adapts legacy pointer/count arguments to `ZSTD_outBuffer` and `ZSTD_inBuffer`, calls `ZSTD_decompressStream()`, then writes output position and input position back to `*dstCapacityPtr` and `*srcSizePtr`.

## State And Persistence
The underlying `ZSTD_DStream` owns all stream state: frame parsing stage, loaded dictionary, input buffering, output buffering, history window, checksum state, and progress. The wrapper layer stores no independent state. Dictionaries loaded by initialization persist according to the modern DStream semantics.

## Dependencies And Integration Points
The file includes `../zstd.h` with deprecation warnings disabled for `ZSTD_initDStream_usingDict`, defines `ZBUFF_STATIC_LINKING_ONLY`, and includes `zbuff.h`. It is the decompression half of the legacy buffered API and interoperates with modern zstd frames.

## Risks
The wrapper must preserve legacy consumed/produced byte reporting even when the modern stream returns a hint or asks for output flushing. Tiny buffers, pending buffered output, and partial input consumption are the main behavioral compatibility risks. Dictionary lifetime and error propagation are delegated to the modern API but remain visible through legacy names.

## Test Signals
Useful tests include streaming decompression with one-byte input/output chunks, dictionary-compressed frames, multiple frames, skippable frames, checksum failures, return-value hints across partial calls, and recommended sizes matching `ZSTD_DStreamInSize()`/`ZSTD_DStreamOutSize()`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/deprecated/zbuff_decompress.c -->
