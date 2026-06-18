<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h -->
# sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h

## Purpose
`zstd_zlibwrapper.h` exposes the public control surface for the Zstandard zlib wrapper while including zlib in prefixed mode so wrapper symbols can coexist with native zlib symbols.

## Important APIs, Types, and Functions
The header defines `ZLIB_CONST`, `Z_PREFIX`, and `ZLIB_INTERNAL`, includes `<zlib.h>`, ensures `z_const` and `_Z_OF` compatibility, and declares `zstdVersion()`. Compression controls are `ZWRAP_useZSTDcompression()`, `ZWRAP_isUsingZSTDcompression()`, `ZWRAP_setPledgedSrcSize()`, and `ZWRAP_deflateReset_keepDict()`. Decompression controls include `ZWRAP_decompress_type` with `ZWRAP_FORCE_ZLIB` and `ZWRAP_AUTO`, plus `ZWRAP_setDecompressionType()`, `ZWRAP_getDecompressionType()`, `ZWRAP_isUsingZSTDdecompression()`, and `ZWRAP_inflateReset_keepDict()`.

## Control Flow
The header has no runtime flow, but its macros determine symbol prefixing and internal zlib visibility. Consumers include this header and then call standard zlib-like APIs plus wrapper controls.

## State and Persistence
The header documents that compression and decompression mode controls mutate global runtime state and are not thread-safe. Per-stream effects such as pledged source size and keep-dictionary reset are applied to zlib streams created under wrapper mode.

## Dependencies and Integration Points
It is the public integration point for users of the wrapper, benchmark code, and the copied `gz*` implementation. It depends on zlib types such as `z_streamp` and must be C++ compatible through `extern "C"`.

## Risks
Because `Z_PREFIX` is set before including zlib, callers must understand that symbol names may be prefixed and linked with the wrapper build. `ZLIB_INTERNAL` disables some gz64 functions as a compatibility workaround. Thread-unsafety of global controls is explicitly documented and should be respected by callers.

## Test Signals
Test signals are mostly compile/link coverage: C and C++ inclusion, prefixed zlib symbol resolution, and availability of wrapper control APIs. Runtime tests should verify the documented global switches and stream-specific helper functions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h -->
