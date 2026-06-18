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
