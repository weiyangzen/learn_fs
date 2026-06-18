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
