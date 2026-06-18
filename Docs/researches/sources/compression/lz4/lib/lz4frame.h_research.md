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
