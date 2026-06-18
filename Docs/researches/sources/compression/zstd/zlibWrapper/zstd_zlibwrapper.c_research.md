<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c -->
# sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c

## Purpose
`zstd_zlibwrapper.c` implements a zlib-compatible API layer that can redirect compression to Zstandard and can auto-detect ZSTD versus zlib streams for decompression. It preserves zlib entry points with a `z_` prefix while delegating unsupported or disabled cases to native zlib.

## Important APIs, Types, and Functions
Compression APIs include `ZWRAP_useZSTDcompression()`, `ZWRAP_isUsingZSTDcompression()`, `z_deflateInit_()`, `z_deflateInit2_()`, `z_deflateSetDictionary()`, `z_deflate()`, `z_deflateEnd()`, `z_deflateBound()`, `z_deflateParams()`, `z_compress()`, `z_compress2()`, and `z_compressBound()`. Decompression APIs include `ZWRAP_setDecompressionType()`, `ZWRAP_getDecompressionType()`, `z_inflateInit_()`, `z_inflateInit2_()`, `z_inflate()`, `z_inflateReset()`, `z_inflateSetDictionary()`, `z_inflateEnd()`, `z_inflateSync()`, and `z_uncompress()`. Internal contexts are `ZWRAP_CCtx` and `ZWRAP_DCtx`.

## Control Flow
Compression is controlled by global `g_ZWRAP_useZSTDcompression`. Disabled mode simply calls zlib. Enabled mode allocates a `ZWRAP_CCtx`, creates a ZSTD stream lazily, initializes parameters from zlib compression level and pledged source size, then maps `deflate()` input/output buffers to `ZSTD_compressStream()`, `ZSTD_flushStream()`, and `ZSTD_endStream()`. Decompression starts in unknown mode unless forced to zlib. `z_inflate()` buffers or inspects the first four bytes; non-ZSTD data initializes native zlib inflate and transfers control, while ZSTD data creates a ZSTD DStream and drives `ZSTD_decompressStream()`.

## State and Persistence
The file maintains process-global switches for compression and decompression mode. Per-stream state is stored in `strm->state` as a wrapper context and decompression stream type is recorded in `strm->reserved`. The compression context tracks `streamEnd`, total input bytes independent of user resets, compression level, pledged size, custom allocator state, ZSTD stream state, and in/out buffers. The decompression context tracks header bytes, error count for dictionary signaling, windowBits/version for zlib fallback, custom memory, and ZSTD stream state.

## Dependencies and Integration Points
It depends on `zlib.h` without `Z_PREFIX` for native fallback and `zstd.h` with `ZSTD_STATIC_LINKING_ONLY` for frame detection, magic numbers, custom memory, and stream parameter APIs. It is the core integration layer used by wrapper consumers and by `gzread.c`/`gzwrite.c`.

## Risks
Global toggles are not thread-safe. Several advanced zlib APIs are unsupported when operating on ZSTD streams and return stream errors with messages. ZSTD decompression returns `Z_NEED_DICT` once on dictionary errors, then errors on repeated failure. The code relies on `z_stream.reserved`, which is not normally application-managed in zlib code. There are debug log format strings that reference a `res` token in arguments where `result` is intended, which would matter if logging macros are enabled. Compression flush modes `Z_FULL_FLUSH`, `Z_BLOCK`, and `Z_TREES` are unsupported in ZSTD mode, affecting consumers that rely on zlib block semantics.

## Test Signals
Essential coverage includes zlib-disabled passthrough, ZSTD-enabled compression, one-shot compress/uncompress, streaming deflate/inflate with small buffers, dictionary set/reset paths, pledged source size, zlib fallback auto-detection, forced-zlib mode, unsupported advanced APIs, custom allocators, and `gz*` integration using ZSTD frames.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c -->
