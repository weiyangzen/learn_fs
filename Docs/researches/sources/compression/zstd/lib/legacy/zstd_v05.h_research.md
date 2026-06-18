# sources/compression/zstd/lib/legacy/zstd_v05.h

## Purpose
This header declares the public compatibility surface for decoding Zstandard v0.5 frames. It gives callers one-shot, context-based, dictionary-based, direct streaming, raw block, frame-size probing, and buffered streaming APIs without exposing the internals of `ZSTDv05_DCtx` or `ZBUFFv05_DCtx`.

## Important APIs, Types, And Functions
The primary one-shot API is `ZSTDv05_decompress(dst, dstCapacity, src, compressedSize)`. `ZSTDv05_findFrameSizeInfoLegacy(src, srcSize, cSize, dBound)` scans a v0.5 frame and reports the compressed frame length plus a decompressed upper bound. `ZSTDv05_isError()` and `ZSTDv05_getErrorName()` expose shared error handling.

Explicit memory management uses the opaque `ZSTDv05_DCtx` type with `ZSTDv05_createDCtx()`, `ZSTDv05_freeDCtx()`, and `ZSTDv05_decompressDCtx()`. Dictionary support is declared through `ZSTDv05_decompress_usingDict()`. Advanced direct streaming declares `ZSTDv05_strategy`, `ZSTDv05_parameters`, `ZSTDv05_getFrameParams()`, `ZSTDv05_decompressBegin_usingDict()`, `ZSTDv05_copyDCtx()`, `ZSTDv05_nextSrcSizeToDecompress()`, and `ZSTDv05_decompressContinue()`. The only practically useful frame parameter for decompression is `windowLog`, though the legacy parameter struct also contains compression-related fields for API shape compatibility.

The buffered API uses opaque `ZBUFFv05_DCtx` with `ZBUFFv05_createDCtx()`, `ZBUFFv05_freeDCtx()`, `ZBUFFv05_decompressInit()`, `ZBUFFv05_decompressInitDictionary()`, `ZBUFFv05_decompressContinue()`, `ZBUFFv05_isError()`, `ZBUFFv05_getErrorName()`, `ZBUFFv05_recommendedDInSize()`, and `ZBUFFv05_recommendedDOutSize()`. The header also defines `ZSTDv05_MAGICNUMBER` as `0xFD2FB525`.

## Control Flow
The simplest caller allocates a destination buffer large enough for the decompressed data and calls `ZSTDv05_decompress()` with the exact compressed frame size. Reusable callers allocate `ZSTDv05_DCtx`, pass it to `ZSTDv05_decompressDCtx()` or `ZSTDv05_decompress_usingDict()`, and free it when done.

Direct streaming callers first inspect a frame with `ZSTDv05_getFrameParams()` if they need the window size, then initialize a context with `ZSTDv05_decompressBegin_usingDict()` or the no-dictionary begin function declared in the implementation's static section, then loop over `ZSTDv05_nextSrcSizeToDecompress()` and `ZSTDv05_decompressContinue()`. The contract is strict: every `ZSTDv05_decompressContinue()` call must receive exactly the requested number of source bytes, and frame completion is signaled when the next source size becomes zero.

Buffered streaming callers create a `ZBUFFv05_DCtx`, initialize it, and repeatedly call `ZBUFFv05_decompressContinue()`. That function consumes and produces variable amounts by updating `*srcSizePtr` and `*dstCapacityPtr`, returning a next-input-size hint or zero at frame completion.

## State, Persistence, And Dependencies
The header depends on `<stddef.h>` for `size_t` and `../common/mem.h` for `U64` and `U32`. It deliberately hides the layouts of both decompression contexts, forcing allocation through the declared constructors. Contexts are reusable across frames after initialization, and dictionary-prepared contexts can be copied for repeated decodes with the same dictionary.

Direct streaming persists history in the `ZSTDv05_DCtx`; callers must respect the documented requirement that previous output remains available contiguously or through an accepted ring-buffer layout up to the frame window. The buffered API owns that history internally and exposes only variable-size input/output progress through pointer parameters.

## Integration Points
This header is included by `zstd_v05.c` and by any legacy-dispatch code that needs to probe or decode v0.5 frames. It is source-tree-aligned with other legacy zstd headers, and its magic number is the selector that lets a higher-level compatibility layer route v0.5 data to this decoder. Error helpers integrate with zstd's shared error-code convention.

## Risks
The API is legacy and partially experimental. The comments warn that advanced/static-linking prototypes may change and should not be used as a stable DLL surface. The one-shot API requires the exact compressed size and a sufficiently large destination buffer, but the header cannot express the decompressed size. Direct streaming is easy to misuse because source chunk sizes must exactly match `ZSTDv05_nextSrcSizeToDecompress()`, and output history must remain accessible across block calls. `ZSTDv05_findFrameSizeInfoLegacy()` assumes non-null output pointers. The buffered API overwrites the caller's destination span on each call and requires the caller to preserve produced bytes if needed.

## Test Signals
Header-level tests should compile C and C++ consumers against the declarations, verify opaque context allocation/free cycles, assert that `ZSTDv05_MAGICNUMBER` routes frames correctly, and exercise one-shot, dictionary, direct streaming, and buffered streaming call contracts. Negative tests should cover non-exact compressed sizes, too-small destination capacity, null or zero-size dictionaries, partial frame headers in `ZSTDv05_getFrameParams()` and `ZBUFFv05_decompressContinue()`, and error-name plumbing through `ZSTDv05_isError()`/`ZBUFFv05_isError()`.
