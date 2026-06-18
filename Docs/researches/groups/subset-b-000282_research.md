# subset-b-000282 Research

Grouped research for six LZ4 library files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4.h -->
# sources/compression/lz4/lib/lz4.h

## Purpose
`lz4.h` is the public C API for the raw LZ4 block codec. It declares versioning, symbol export macros, block compression/decompression entry points, streaming compression/decompression contexts, static-linking-only helpers, internal context layouts for static allocation, and deprecated compatibility APIs. It explicitly handles LZ4 blocks, not self-describing LZ4 frames; frame production and parsing are delegated to `lz4frame.h`.

## Important APIs, Types, And Macros
The stable one-shot API is `LZ4_compress_default()`, `LZ4_decompress_safe()`, `LZ4_compressBound()`, `LZ4_compress_fast()`, `LZ4_compress_fast_extState()`, `LZ4_compress_destSize()`, and `LZ4_decompress_safe_partial()`. The caller owns all buffers and must supply sizes because raw blocks do not embed compressed or decompressed lengths.

Version and build contracts are exposed through `LZ4_VERSION_MAJOR`, `LZ4_VERSION_MINOR`, `LZ4_VERSION_RELEASE`, `LZ4_VERSION_NUMBER`, `LZ4_VERSION_STRING`, `LZ4_versionNumber()`, and `LZ4_versionString()`. `LZ4LIB_API` handles DLL import/export and compiler visibility. `LZ4_FREESTANDING` disables heap use and requires caller-provided memory macros.

Streaming compression revolves around opaque `LZ4_stream_t`, with `LZ4_createStream()`, `LZ4_freeStream()`, `LZ4_initStream()`, `LZ4_resetStream_fast()`, `LZ4_loadDict()`, `LZ4_loadDictSlow()`, `LZ4_attach_dictionary()`, `LZ4_compress_fast_continue()`, and `LZ4_saveDict()`. Streaming decompression uses `LZ4_streamDecode_t`, `LZ4_createStreamDecode()`, `LZ4_freeStreamDecode()`, `LZ4_setStreamDecode()`, `LZ4_decoderRingBufferSize()`, `LZ4_decompress_safe_continue()`, `LZ4_decompress_safe_usingDict()`, and `LZ4_decompress_safe_partial_usingDict()`.

Static-linking-only declarations are enabled by `LZ4_STATIC_LINKING_ONLY`. They include fast-reset and destination-size variants, in-place buffer margin macros, and compile-time tunables such as `LZ4_DISTANCE_MAX`. The header also exposes private layouts `LZ4_stream_t_internal`, `union LZ4_stream_u`, and `LZ4_streamDecode_t_internal` only so callers can allocate contexts statically; comments warn that members are not ABI-safe.

## Control Flow And State
One-shot compression consumes a single input span and returns either bytes written or zero on fitting failure. Safe decompression consumes exactly one raw block and returns bytes decoded or a negative error. The partial decompressor stops after a target output count, but the header warns that passing a source size larger than the exact block size can silently corrupt output when `targetOutputSize` exceeds the real decompressed size.

Streaming compression preserves up to the prior 64 KiB as history. Callers initialize or create a stream, optionally load/attach a dictionary, then call `LZ4_compress_fast_continue()` per block. The state assumes prior source data remains available unless the caller uses `LZ4_saveDict()` to copy history into a safe buffer. After compression errors, stream state is undefined and must be reset or freed.

Streaming decompression tracks the last decoded bytes through `LZ4_streamDecode_t`. The destination history must remain available, or the caller must reestablish it with `LZ4_setStreamDecode()`. Ring-buffer support is documented through size rules in `LZ4_decoderRingBufferSize()` and `LZ4_DECODER_RING_BUFFER_SIZE()`.

## Dependencies And Integration Points
The header depends only on `<stddef.h>` for the stable API and conditionally `<stdint.h>` for exposed private allocation layouts. Implementations live in `lz4.c`, with high-compression in `lz4hc.*` and frame integration in `lz4frame.*`. `lz4frame.c` includes this header with `LZ4_STATIC_LINKING_ONLY` to use fast-reset, dictionary, and context-size behavior.

## Risks And Edge Cases
Raw blocks are not self-describing, so callers must transport sizes out of band. Misstated `compressedSize`, `dstCapacity`, or streaming dictionary availability causes errors or undefined stream state. Deprecated `LZ4_decompress_fast*()` functions are explicitly unsafe for untrusted input because they do not know the input size and may read out of bounds on malformed data. Static-linking-only declarations and private structs are not stable ABI. Freestanding mode excludes LZ4F APIs and heap-using functions.

## Test Signals
Useful test coverage includes one-shot round trips across edge sizes including zero, `LZ4_MAX_INPUT_SIZE` boundary checks, too-small destination failures, malformed block rejection by `LZ4_decompress_safe()`, partial decode behavior with exact and oversized source buffers, streaming compression/decompression with linked blocks, dictionary attach/load/save paths, ring-buffer scenarios, static allocation via `LZ4_initStream()`, freestanding compile checks, and deprecation/visibility compile checks.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4file.c -->
# sources/compression/lz4/lib/lz4file.c

## Purpose
`lz4file.c` implements a small static file-oriented wrapper around the LZ4 frame API. It exposes handle-based read and write helpers that operate on caller-owned `FILE*` streams, allocate frame contexts and work buffers internally, and translate I/O failures into `LZ4F_errorCode_t` values.

## Important APIs, Types, And Functions
The read side defines `struct LZ4_readFile_s` with an `LZ4F_dctx*`, `FILE*`, source buffer, current source cursor, current source size, and maximum source buffer size. Public functions are `LZ4F_readOpen()`, `LZ4F_read()`, and `LZ4F_readClose()`. Helpers include `freeReadFileResources()`, `freeAndNullReadFile()`, and `readAndParseHeader()`.

The write side defines `struct LZ4_writeFile_s` with an `LZ4F_cctx*`, `FILE*`, destination buffer, maximum input chunk size, destination buffer capacity, and sticky error code. Public functions are `LZ4F_writeOpen()`, `LZ4F_write()`, and `LZ4F_writeClose()`. Helpers include `freeWriteFileResources()`, `freeAndNullWriteFile()`, and `writeHeader()`.

`returnErrorCode()` and `RETURN_ERROR()` locally construct frame-style negative error codes from static-only `LZ4F_errorCodes`.

## Control Flow
`LZ4F_readOpen()` validates parameters, allocates the read handle, creates a decompression context with `LZ4F_VERSION`, reads up to `LZ4F_HEADER_SIZE_MAX` bytes, parses frame info with `LZ4F_getFrameInfo()`, sizes `srcBuf` using `LZ4F_getBlockSize()`, and preserves any bytes read past the frame header for later decompression.

`LZ4F_read()` loops until the caller's output buffer is filled or input ends. It uses any buffered compressed bytes first, refills `srcBuf` with `fread()` when empty, calls `LZ4F_decompress()`, advances the compressed-buffer cursor by the consumed count, and advances the output pointer by produced bytes. It returns either decoded byte count or an LZ4F error code encoded as `size_t`.

`LZ4F_writeOpen()` validates the output handle and `FILE*`, derives the block size from preferences or default settings, allocates the write handle and destination buffer sized by `LZ4F_compressBound(blockSize, prefsPtr)`, creates the compression context, writes the frame header with `LZ4F_compressBegin()`, and returns the handle.

`LZ4F_write()` splits the caller input into chunks no larger than the frame block size, compresses each chunk with `LZ4F_compressUpdate()`, writes compressed bytes with `fwrite()`, and returns the original input size on success. `LZ4F_writeClose()` finalizes the frame with `LZ4F_compressEnd()` unless a prior write error is sticky, writes the end bytes, releases the handle, and returns the final status.

## State And Persistence
State is per-handle and heap allocated. Read handles persist decompression context state, buffered compressed input, and file position through the underlying `FILE*`. Write handles persist compression context state, output scratch buffer, and a sticky `errCode` that suppresses frame finalization after earlier write/compression failure. The module never closes the underlying `FILE*`; ownership remains with the caller.

## Dependencies And Integration Points
The implementation includes `<stdlib.h>`, `<string.h>`, `<assert.h>`, `lz4.h`, and `lz4file.h`. It depends heavily on static-only frame helpers from `lz4frame_static.h`, including `LZ4F_errorCodes` and `LZ4F_getBlockSize()`. It integrates with any C caller that already has binary-mode `FILE*` handles and wants simple frame read/write routines without driving the lower-level streaming frame API directly.

## Risks And Edge Cases
`readAndParseHeader()` reads a fixed `LZ4F_HEADER_SIZE_MAX` chunk up front and requires at least `LZ4F_HEADER_SIZE_MIN + LZ4F_ENDMARK_SIZE` bytes, which rejects very short/truncated inputs early but also couples the wrapper to seekless forward consumption. `LZ4F_read()` breaks on EOF even if the frame has not returned a completed status, so truncated streams can look like a short read instead of a frame error unless later logic checks for frame completion externally.

There is a notable cleanup-risk path in `LZ4F_writeOpen()`: after allocating `writeFile`, if `LZ4F_createCompressionContext()` fails, it calls `freeAndNullWriteFile(lz4fWrite)` instead of `freeAndNullWriteFile(&writeFile)`. Since the caller output pointer has not been assigned yet, this can free an unrelated value supplied by the caller and leak the local allocation. The analogous read path uses the local pointer correctly.

`LZ4F_write()` treats `fwrite()` returning fewer bytes than requested as `io_write`, sets sticky error state, and returns an error code. It does not retry partial writes. All read/write functions return frame-style error codes in unsigned return types, so callers must consistently use `LZ4F_isError()`.

## Test Signals
Focused tests should cover opening null pointers, valid round-trip file compression/decompression, short headers, invalid frame headers, truncated frame bodies, frame checksum failure propagation, small caller read buffers, large writes split across multiple frame blocks, write finalization after a prior write error, partial `fwrite()` failure via a mock or fopencookie-style stream, and the `LZ4F_writeOpen()` compression-context allocation failure cleanup path.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4file.h -->
# sources/compression/lz4/lib/lz4file.h

## Purpose
`lz4file.h` declares the static file wrapper API implemented by `lz4file.c`. It gives callers a compact `FILE*`-based interface for LZ4 frame decompression and compression while hiding the underlying frame contexts and temporary buffers.

## Important APIs And Types
The header includes `<stdio.h>` for `FILE*` and `lz4frame_static.h` for frame types, static export macros, and static-only helpers. It forward declares opaque handle types `LZ4_readFile_t` and `LZ4_writeFile_t`.

The read API is `LZ4F_readOpen(LZ4_readFile_t** lz4fRead, FILE* fp)`, `LZ4F_read(LZ4_readFile_t* lz4fRead, void* buf, size_t size)`, and `LZ4F_readClose(LZ4_readFile_t* lz4fRead)`. The write API is `LZ4F_writeOpen(LZ4_writeFile_t** lz4fWrite, FILE* fp, const LZ4F_preferences_t* prefsPtr)`, `LZ4F_write(LZ4_writeFile_t* lz4fWrite, const void* buf, size_t size)`, and `LZ4F_writeClose(LZ4_writeFile_t* lz4fWrite)`.

All declarations use `LZ4FLIB_STATIC_API`, signaling that this API is intended for static-linking or explicitly published static symbols rather than the default shared-library surface.

## Control Flow And Contract
Callers open a binary `FILE*` themselves, then call `LZ4F_readOpen()` or `LZ4F_writeOpen()` to allocate a wrapper handle. Reads and writes are performed through the wrapper, and the wrapper handle must be closed with the matching close function. The comments specify that output handle arguments are out parameters whose initial values are ignored and valid only on success.

The header documents that `LZ4F_read()` returns bytes read into the caller buffer and `LZ4F_write()` returns bytes written from the caller buffer. Error returns are frame error codes and should be checked with `LZ4F_isError()`.

## State And Persistence
The header deliberately hides state layout. Runtime state lives in the opaque handle implementation: frame context, buffers, sticky write error state, and the caller's `FILE*`. The underlying `FILE*` is not documented as being closed by the wrapper, and implementation confirms that only wrapper resources are freed.

## Dependencies And Integration Points
This is a convenience layer on top of `lz4frame.h`/`lz4frame_static.h`, not a replacement for the full streaming frame API. It integrates with standard C file I/O and inherits frame preferences from `LZ4F_preferences_t` on write. Because it includes `lz4frame_static.h`, it also defines `LZ4F_STATIC_LINKING_ONLY` before including `lz4frame.h`.

## Risks And Edge Cases
The API name prefix overlaps the core frame API (`LZ4F_*`) while being static-only and file-specific, so link visibility and documentation need care. The comments contain a duplicated "LZ4 File Decompression" heading above the write API, which can confuse generated docs but not compilation. Since binary-mode `FILE*` is required, Windows callers must avoid text mode. Error values share the unsigned `size_t`/`LZ4F_errorCode_t` convention, so callers that compare directly to negative values will mishandle failures.

## Test Signals
Header-level checks should compile both C and C++ consumers, verify static-only symbol visibility under default and `LZ4F_PUBLISH_STATIC_FUNCTIONS` builds, confirm binary `FILE*` read/write examples round-trip with `LZ4F_isError()` checks, and ensure consumers can pass custom `LZ4F_preferences_t` through `LZ4F_writeOpen()`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame.c -->
# sources/compression/lz4/lib/lz4frame.c

## Purpose
`lz4frame.c` implements the LZ4 frame format API declared in `lz4frame.h`. It creates and decodes self-contained LZ4 frames with magic numbers, frame descriptors, block headers, optional block checksums, optional content checksums, optional content size and dictionary ID fields, skippable-frame handling, streaming compression, streaming decompression, dictionary compression, and custom memory allocation hooks.

## Important Types And Internal State
Compression state is held in `LZ4F_cctx_t`. Important fields include custom memory functions, frame preferences, version, `cStage`, optional `LZ4F_CDict`, block/buffer sizing, `tmpBuff` and `tmpIn` streaming buffers, `tmpInSize`, total input size for content-size validation, content checksum state, selected LZ4/LZ4HC context pointer and allocation type, and current block compression mode.

Dictionary compression state is `struct LZ4F_CDict_s`, which owns a copied last-64-KiB dictionary buffer plus preloaded fast and HC LZ4 contexts. It is read-only after creation and intended to be shareable across compression jobs.

Decompression state is `struct LZ4F_dctx_s`. It stores custom memory functions, decoded `LZ4F_frameInfo_t`, version, `dStage`, remaining content size, max block/buffer sizes, temporary input and output buffers, dictionary pointer and size, output flush cursors, content and block checksum states, a sticky checksum-skip flag, and a header scratch buffer.

The decompressor stage enum `dStage_t` drives incremental parsing: frame header acquisition, initialization, block header acquisition, direct copy of uncompressed blocks, compressed block acquisition, temporary output flushing, suffix checksum verification, skippable-frame size reading, and skippable payload skipping.

## Important APIs And Functions
Error handling uses `LZ4F_isError()`, `LZ4F_getErrorName()`, `LZ4F_getErrorCode()`, `LZ4F_returnErrorCode()`, `RETURN_ERROR()`, `RETURN_ERROR_IF()`, and `FORWARD_IF_ERROR()`. Sizes and little-endian fields are handled by `LZ4F_readLE32()`, `LZ4F_writeLE32()`, `LZ4F_readLE64()`, `LZ4F_writeLE64()`, `LZ4F_getBlockSize()`, and `LZ4F_headerChecksum()`.

One-shot compression is `LZ4F_compressFrame()` and `LZ4F_compressFrame_usingCDict()`, with capacity estimation from `LZ4F_compressFrameBound()` and `LZ4F_compressBound()`. Streaming compression is created/freed with `LZ4F_createCompressionContext*()` and `LZ4F_freeCompressionContext()`, started with `LZ4F_compressBegin()`, `LZ4F_compressBegin_usingDict()`, or `LZ4F_compressBegin_usingCDict()`, fed through `LZ4F_compressUpdate()` or static-only `LZ4F_uncompressedUpdate()`, flushed with `LZ4F_flush()`, and finalized with `LZ4F_compressEnd()`.

Dictionary APIs are `LZ4F_createCDict_advanced()`, `LZ4F_createCDict()`, and `LZ4F_freeCDict()`. Context inspection APIs are `LZ4F_cctx_size()` and `LZ4F_dctx_size()`.

Decompression is created/freed with `LZ4F_createDecompressionContext*()` and `LZ4F_freeDecompressionContext()`, reset with `LZ4F_resetDecompressionContext()`, introspected with `LZ4F_headerSize()` and `LZ4F_getFrameInfo()`, executed with `LZ4F_decompress()`, and dictionary-seeded with `LZ4F_decompress_usingDict()`.

## Compression Control Flow
`LZ4F_compressFrame_usingCDict()` normalizes preferences, auto-corrects content size, picks an optimal block size, forces independent blocks for single-block content, sets `autoFlush`, checks destination capacity, writes the frame header, compresses all input, and writes the frame suffix.

`LZ4F_compressBegin_internal()` allocates or reinitializes the correct fast or HC LZ4 context, sizes internal buffers based on block size, `autoFlush`, and linked-block mode, initializes dictionaries and checksum state, writes the magic number and descriptor bytes, writes optional content size and dictionary ID fields, appends the header checksum byte, and sets `cStage` to 1.

`LZ4F_compressUpdateImpl()` requires `cStage == 1`, verifies destination capacity using buffered input, flushes when switching between compressed and uncompressed block modes, fills any partial block in `tmpIn`, emits full blocks through `LZ4F_makeBlock()`, optionally auto-flushes a final partial block, saves linked-block history when needed, buffers remaining input when not auto-flushing, updates the content checksum, and increments `totalInSize`.

`LZ4F_makeBlock()` attempts compression with a selected fast/HC/continue/no-compress function. If compression fails or is not smaller than the input, it emits an uncompressed block marked with `LZ4F_BLOCKUNCOMPRESSED_FLAG`; otherwise it emits compressed bytes. Optional block checksums cover the emitted block payload.

`LZ4F_flush()` emits a pending partial block. `LZ4F_compressEnd()` flushes, writes a zero block endmark, writes optional content checksum, resets `cStage` to reusable state, and validates declared content size against `totalInSize`.

## Decompression Control Flow
`LZ4F_decompress()` is an incremental state machine. It updates caller-provided consumed and produced byte counts, returns a next-source-size hint, and can pause when it lacks input or output space. It starts by decoding or accumulating the frame header through `LZ4F_decodeHeader()`. Header decoding handles skippable-frame magic, validates frame magic, version and reserved bits, computes variable header size, verifies the header checksum, extracts block mode/checksum/content-size/dict-ID metadata, and sets `dstage_init`.

At `dstage_init`, decompression allocates temporary input and output buffers large enough for the maximum block size and linked-block history. Block headers are then read either directly or via `tmpIn`. A zero block header moves to suffix processing. Uncompressed blocks enter `dstage_copyDirect`, copy directly from source to caller destination, update optional block/content checksums, track declared content-size remaining, and update linked-block history.

Compressed blocks are acquired directly or copied into `tmpIn`. Optional block checksum is verified before decode. If the caller destination has enough room and dictionary layout permits, the block is decoded directly to `dstBuffer`; otherwise it is decoded to `tmpOutBuffer` and flushed through `dstage_flushOut` across one or more calls. Linked-block history is preserved through `LZ4F_updateDict()`, with extra copying into `tmpOutBuffer` when the caller has not pledged `stableDst`.

Suffix processing validates declared frame size, reads optional content checksum, compares it to accumulated XXH32 unless checksums were skipped, resets the context, and returns zero for a completed frame. Skippable frames read a 32-bit size and advance over the payload without producing output, then reset for the next frame.

## State And Persistence Behavior
Compression contexts are reusable after a successful `LZ4F_compressEnd()`. After compression update errors, comments state the context is undefined and must be reinitialized or freed. Compression preserves linked-block history either in stable caller source memory or by copying up to 64 KiB into the internal buffer. `contentSize` validation persists across the frame through `totalInSize`.

Decompression contexts persist stage, buffered input, temporary output, dictionary history, checksum state, and frame metadata across calls. `skipChecksums` is sticky for the rest of a frame once set. `stableDst` is a caller pledge that lets the decompressor avoid preserving history internally; violating it can break linked-block decompression. `LZ4F_freeDecompressionContext()` returns the current stage value, allowing callers to notice a context freed mid-frame.

## Dependencies And Integration Points
The implementation includes `lz4frame.h` with `LZ4F_STATIC_LINKING_ONLY`, `lz4.h` with `LZ4_STATIC_LINKING_ONLY`, `lz4hc.h` with `LZ4_HC_STATIC_LINKING_ONLY`, and `xxhash.h` with `XXH_STATIC_LINKING_ONLY`. It integrates with fast and high-compression block codecs, HC dictionary APIs, XXH32 checksums, standard allocation by default, optional custom allocators, and the `lz4` CLI frame format.

## Risks And Edge Cases
Destination-capacity calculations are strict; callers must use the right bound for the right operation. Contexts are not thread-safe for concurrent mutation, while `LZ4F_CDict` is intended to be shared read-only. Static-only APIs such as custom allocators and uncompressed update can change ABI. The code has fuzzing build gates that disable some validation under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`, which must not leak into production builds.

Dictionary behavior has sharp contracts: raw dictionary buffers must outlive the compression/decompression frame, `LZ4F_compressBegin_usingDict()` notes that it only uses the dictionary once rather than once per independent block, and `stableSrc`/`stableDst` pledges must be true. Error returns are encoded in `size_t`, so callers must use `LZ4F_isError()`.

`LZ4F_getFrameInfo()` can consume the frame header and start decoding; callers must resume decompression after the consumed header bytes. Passing the same bytes again is documented as risking failure or silent corruption. Skippable frames produce no output and return hints until fully skipped.

## Test Signals
High-value tests include frame round trips for every block size and block mode, content-size present and absent, content checksum and block checksum enabled/disabled, header checksum failures, reserved flag failures, invalid block size IDs, destination-too-small paths, `autoFlush` and buffered flush behavior, content-size mismatch at compression and decompression end, linked-block streaming with and without `stableSrc`/`stableDst`, dictionary compression/decompression with raw dictionaries and `LZ4F_CDict`, uncompressed-update independent-block mode, skippable frames, concatenated frames, tiny incremental input/output buffers, custom allocator success/failure paths, and context-size reporting.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame.h -->
# sources/compression/lz4/lib/lz4frame.h

## Purpose
`lz4frame.h` is the public API contract for producing and consuming interoperable LZ4 frames. Unlike `lz4.h`, it describes a self-contained framing layer with metadata, block headers, optional content and block checksums, optional content size and dictionary ID, streaming compression/decompression, dictionary compression, and static-linking-only extension points.

## Important APIs, Types, And Constants
Error handling is based on `typedef size_t LZ4F_errorCode_t`, `LZ4F_isError()`, and `LZ4F_getErrorName()`. Public enums define frame parameters: `LZ4F_blockSizeID_t`, `LZ4F_blockMode_t`, `LZ4F_contentChecksum_t`, `LZ4F_blockChecksum_t`, and `LZ4F_frameType_t`.

`LZ4F_frameInfo_t` carries block size, block mode, checksum flags, read-only frame type, optional content size, optional dictionary ID, and block checksum flag. `LZ4F_preferences_t` wraps frame info plus compression level, `autoFlush`, `favorDecSpeed`, and reserved fields. Both have initializer macros.

One-shot compression is `LZ4F_compressFrame()` plus `LZ4F_compressFrameBound()`. Advanced streaming compression uses opaque `LZ4F_cctx`, `LZ4F_createCompressionContext()`, `LZ4F_freeCompressionContext()`, `LZ4F_compressBegin()`, `LZ4F_compressBound()`, `LZ4F_compressUpdate()`, `LZ4F_flush()`, and `LZ4F_compressEnd()`.

Streaming decompression uses opaque `LZ4F_dctx`, `LZ4F_createDecompressionContext()`, `LZ4F_freeDecompressionContext()`, `LZ4F_headerSize()`, `LZ4F_getFrameInfo()`, `LZ4F_decompress()`, and `LZ4F_resetDecompressionContext()`. `LZ4F_decompressOptions_t` provides `stableDst` and sticky `skipChecksums` behavior.

Dictionary APIs are `LZ4F_compressBegin_usingDict()`, `LZ4F_decompress_usingDict()`, opaque `LZ4F_CDict`, `LZ4F_createCDict()`, `LZ4F_freeCDict()`, `LZ4F_compressFrame_usingCDict()`, and `LZ4F_compressBegin_usingCDict()`.

Static-linking-only declarations enabled by `LZ4F_STATIC_LINKING_ONLY` expose `LZ4F_errorCodes`, `LZ4F_getErrorCode()`, `LZ4F_getBlockSize()`, `LZ4F_uncompressedUpdate()`, custom allocator types and advanced context/CDict creation functions, `LZ4F_defaultCMem`, and context-size inspection functions.

## Control Flow Contract
One-shot compression consumes all input and requires `dstCapacity >= LZ4F_compressFrameBound()`. Streaming compression requires creating a context, writing a header with `LZ4F_compressBegin()`, calling `LZ4F_compressUpdate()` repeatedly, optionally flushing, and closing the frame with `LZ4F_compressEnd()`. After `compressEnd`, the context can start another compression task.

Streaming decompression is pull-oriented and incremental. Callers repeatedly supply source and destination buffers to `LZ4F_decompress()` until it returns zero or an error. The API updates both size pointers to report consumed and produced bytes, and the return value is a hint for the next preferred source size. The header explicitly documents that unconsumed input may be the start of another frame.

`LZ4F_getFrameInfo()` can be called before decompression to consume just the frame header and populate frame info, or later to retrieve already-decoded metadata. If it consumes the header, callers must advance the source pointer before calling `LZ4F_decompress()`.

## State And Persistence Behavior
Opaque compression and decompression contexts persist across calls and are not value types. Preferences and options contain reserved fields that must be zero for forward compatibility. `stableSrc` and `stableDst` are lifetime pledges: when set, the implementation may skip internal copies by assuming source or destination history remains available. `skipChecksums` disables checksum calculation and verification for the rest of a frame after being set once.

`LZ4F_CDict` persists a digested compression dictionary and can be shared by multiple threads because its use is read-only. Raw dictionary buffers passed to streaming dictionary APIs must remain accessible for the relevant compression or decompression session.

## Dependencies And Integration Points
The header depends on `<stddef.h>` and optionally C++ linkage guards. It does not require `lz4.h` except for callers that want shared version constants. Implementations integrate with `lz4.c`, `lz4hc.c`, and `xxhash.c`. `lz4file.h` includes `lz4frame_static.h`, which enables this header's static-only declarations for the file wrapper.

## Risks And Edge Cases
Error codes share the `size_t` return channel with successful byte counts; callers must test with `LZ4F_isError()`. Bounds are operation-specific: `LZ4F_compressFrameBound()` is for one-shot frame compression, while `LZ4F_compressBound()` is for individual streaming updates/flush/end. Misusing `LZ4F_getFrameInfo()` by replaying consumed header bytes can cause failure or silent corruption. `stableDst`, `stableSrc`, and dictionary lifetime violations are correctness hazards.

The static-linking-only section is explicitly unstable and normally not exported from shared libraries. `LZ4F_uncompressedUpdate()` only supports independent blocks. The dictionary note states that `LZ4F_compressBegin_usingDict()` uses the dictionary only for the first block, while `LZ4F_compressFrame_usingCDict()` can reuse it for each independent block in larger inputs.

## Test Signals
API conformance tests should compile C and C++ consumers, validate frame round trips through one-shot and streaming APIs, exercise all frame preference flags and block sizes, confirm error detection for invalid headers and checksums, verify size-bound functions against worst-case writes, check `LZ4F_getFrameInfo()` consumed-byte behavior, test dictionary APIs and `dictID` propagation, test `stableDst`/`stableSrc` paths, and verify static-only declarations only appear when `LZ4F_STATIC_LINKING_ONLY` is defined.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame_static.h -->
# sources/compression/lz4/lib/lz4frame_static.h

## Purpose
`lz4frame_static.h` is a compatibility shim for older users of the LZ4 frame static API. The declarations that used to live here have been merged into `lz4frame.h`; this header now enables `LZ4F_STATIC_LINKING_ONLY` and includes `lz4frame.h`.

## Important APIs And Types
The file itself declares no functions or types. Its effective API is the side effect of defining `LZ4F_STATIC_LINKING_ONLY`, which exposes static-linking-only declarations from `lz4frame.h`: frame error enumeration, `LZ4F_getErrorCode()`, `LZ4F_getBlockSize()`, `LZ4F_uncompressedUpdate()`, custom allocator hooks, advanced context and CDict creation functions, and context-size inspection.

## Control Flow And State
There is no runtime control flow or state. Preprocessor flow is straightforward: an include guard prevents repeated inclusion, `LZ4F_STATIC_LINKING_ONLY` is defined, and `lz4frame.h` is included. Any resulting symbols and declarations are controlled by `lz4frame.h` and build macros such as `LZ4F_PUBLISH_STATIC_FUNCTIONS`.

## Dependencies And Integration Points
This header depends directly on `lz4frame.h`. It is used by `lz4file.h` so the file wrapper can use `LZ4FLIB_STATIC_API`, `LZ4F_errorCodes`, and `LZ4F_getBlockSize()`. It also supports downstream code that still includes `lz4frame_static.h` instead of defining `LZ4F_STATIC_LINKING_ONLY` before including `lz4frame.h`.

## Risks And Edge Cases
Including this header broadens the visible API to unstable static-only declarations. Because it defines `LZ4F_STATIC_LINKING_ONLY` before inclusion, translation units that include it may see declarations that are not exported by a shared LZ4 library unless the library was built with `LZ4F_PUBLISH_STATIC_FUNCTIONS`. This can create link errors when code compiles against static-only prototypes but links dynamically.

## Test Signals
Test signals are compile/link oriented: include the header in C and C++ translation units, verify static-only declarations are visible, verify repeated inclusion is harmless, verify dynamic-link builds fail or omit static-only symbols unless explicitly published, and verify legacy consumers can replace direct `lz4frame_static.h` use with `#define LZ4F_STATIC_LINKING_ONLY` plus `#include "lz4frame.h"`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4frame_static.h -->
