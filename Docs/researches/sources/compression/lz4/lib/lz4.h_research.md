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
