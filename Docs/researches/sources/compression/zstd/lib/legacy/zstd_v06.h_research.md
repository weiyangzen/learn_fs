# sources/compression/zstd/lib/legacy/zstd_v06.h

## Purpose
Declares the public C interface for the Zstandard v0.6 legacy decompressor. It is included by the legacy dispatcher when `ZSTD_LEGACY_SUPPORT` covers version 6, and it exposes one-shot, context-based, dictionary, direct streaming, and buffered streaming decompression APIs for frames with magic number `ZSTDv06_MAGICNUMBER`.

The header is format-version-specific: all symbols carry the `v06` suffix to avoid colliding with current zstd APIs and other legacy decoders. It uses an optional Windows export macro but otherwise has no ABI decoration.

## Important APIs, Types, And Constants
`ZSTDv06_decompress()` is the simple one-shot decompression API. It requires the exact compressed frame size and a destination buffer large enough for the original data.

`ZSTDv06_findFrameSizeInfoLegacy()` scans a v0.6 frame to return the compressed frame size consumed and a decompressed-size upper bound. The comments require non-NULL `cSize` and `dBound`.

`ZSTDv06_isError()` and `ZSTDv06_getErrorName()` expose the shared zstd error-code convention for `size_t` results.

`ZSTDv06_DCtx` is an opaque direct decompression context. The header exposes `ZSTDv06_createDCtx()`, `ZSTDv06_freeDCtx()`, `ZSTDv06_decompressDCtx()`, and `ZSTDv06_decompress_usingDict()` for explicit memory management and dictionary-based decode.

`ZSTDv06_frameParams` carries `frameContentSize` and `windowLog` from a frame header. `ZSTDv06_getFrameParams()` parses enough header bytes without consuming a stream. `ZSTDv06_decompressBegin_usingDict()`, `ZSTDv06_copyDCtx()`, `ZSTDv06_nextSrcSizeToDecompress()`, and `ZSTDv06_decompressContinue()` form the direct advanced streaming API.

`ZBUFFv06_DCtx` is an opaque buffered streaming context. `ZBUFFv06_createDCtx()`, `ZBUFFv06_freeDCtx()`, `ZBUFFv06_decompressInit()`, `ZBUFFv06_decompressInitDictionary()`, and `ZBUFFv06_decompressContinue()` expose arbitrary input/output chunk streaming. `ZBUFFv06_recommendedDInSize()` and `ZBUFFv06_recommendedDOutSize()` advertise the 128 KiB block-sized buffers preferred by the implementation.

`ZSTDv06_MAGICNUMBER` is `0xFD2FB526`, used by `zstd_legacy.h` to identify v0.6 frames.

The header declares `ZSTDv06_compressBound(size_t srcSize)`, but the paired `zstd_v06.c` implementation in this repository does not define it. This appears to be leftover API surface from historical zstd headers; callers should not rely on a v0.6 compression implementation from this file.

## Control Flow And API Use
The intended one-shot flow is allocate output, call `ZSTDv06_decompress()` or create a `ZSTDv06_DCtx` and call `ZSTDv06_decompressDCtx()`/`ZSTDv06_decompress_usingDict()`, then test the returned `size_t` with `ZSTDv06_isError()`.

The direct streaming flow is exact-size and stateful. Initialize a `ZSTDv06_DCtx` with `ZSTDv06_decompressBegin_usingDict()` or by copying a prepared context, query `ZSTDv06_nextSrcSizeToDecompress()`, provide exactly that many source bytes to `ZSTDv06_decompressContinue()`, and repeat until the next source size is zero. The header warns that prior decoded data must remain available up to the frame window, preferably contiguously or through a rolling buffer.

The buffered streaming flow hides the exact-size direct API. Call `ZBUFFv06_decompressInit()` or dictionary init, then repeatedly pass input and output buffers to `ZBUFFv06_decompressContinue()`. The function mutates `*srcSizePtr` and `*dstCapacityPtr` to report consumed/produced byte counts and returns a preferred next-input hint, zero on frame completion, or an error code.

Frame parameter discovery can be used before streaming. `ZSTDv06_getFrameParams()` returns zero when `ZSTDv06_frameParams` is filled, a positive byte count when more header data is required, or an error code.

## State And Persistence Behavior
The header defines only opaque context types, so callers cannot persist or inspect internal state directly. All context state is managed by the implementation and must be released with the matching free function.

Direct decompression contexts are reusable after reinitialization. Buffered contexts are also reusable after `ZBUFFv06_decompressInit*()`. Dictionary APIs do not promise to copy dictionary content; the implementation references content dictionaries, so safe callers should keep dictionary memory valid until decompression ends.

The API has no filesystem or durable persistence. The only persistent behavior across calls is context-owned heap memory, buffered input/output, entropy tables, dictionary references, and rolling history needed for LZ matches.

## Dependencies And Integration Points
This header depends only on `<stddef.h>` for `size_t`, making it usable from C and C++ via `extern "C"`.

Its primary integration is `sources/compression/zstd/lib/legacy/zstd_legacy.h`, which conditionally includes it, maps v0.6 magic detection to version number 6, uses its frame-parameter API for decompressed-size compatibility helpers, and routes one-shot and streaming legacy decompression through the declared contexts.

The exported error helpers use the same `size_t` error-code model as the rest of zstd. Callers in the main decompressor should convert or forward these results through normal zstd error handling.

The DLL export macro is limited to `_WIN32` builds that define `ZSTDv06_DLL_EXPORT=1`. Otherwise `ZSTDLIBv06_API` is empty, so symbol visibility is controlled by the containing build.

## Risks And Edge Cases
The header exposes legacy functionality that should remain compatibility-focused. New code should prefer current zstd APIs unless it must handle v0.6 frames.

`ZSTDv06_compressBound()` is declared without an implementation in `zstd_v06.c`, creating a potential link-time trap for callers that assume the header supplies compression support. The rest of the header and implementation are decompression-focused.

Exact compressed sizes matter. One-shot APIs document that `compressedSize` must be exact; direct streaming APIs require each `srcSize` to match `ZSTDv06_nextSrcSizeToDecompress()`. Passing partial or extra data to these lower-level APIs is expected to fail.

`ZSTDv06_findFrameSizeInfoLegacy()` assumes output pointers are not NULL. The header also does not annotate ownership, nullability, or thread-safety. Contexts should be treated as single-operation mutable state and not shared concurrently without external synchronization.

Buffered streaming overwrites the destination buffer content on each call up to the produced byte count; callers must preserve output themselves if needed.

## Test Signals
Header/API conformance tests should compile C and C++ translation units that include `zstd_v06.h`, create/free `ZSTDv06_DCtx` and `ZBUFFv06_DCtx`, call error helpers, and reference `ZSTDv06_MAGICNUMBER`.

Link tests should cover all declared decompression symbols against `zstd_v06.c`. They should deliberately avoid or explicitly flag `ZSTDv06_compressBound()` until an implementation is supplied or the declaration is removed.

Behavioral API tests should enter through `zstd_legacy.h` for v0.6 magic frames, verify `ZSTDv06_getFrameParams()` positive-size retry behavior on short headers, confirm `ZBUFFv06_decompressContinue()` consumption/production pointer updates, and check dictionary and non-dictionary initialization paths.
