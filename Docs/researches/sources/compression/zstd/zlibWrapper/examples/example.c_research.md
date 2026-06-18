# sources/compression/zstd/zlibWrapper/examples/example.c

## Purpose
`example.c` is a zlib API example adapted to compile against `zstd_zlibwrapper.h`. It validates that the wrapper preserves common zlib behaviors for one-shot compression, gzip file APIs, streaming deflate/inflate, large buffer operation, dynamic compression parameter changes, and preset dictionaries, while skipping unsupported sync/flush recovery tests when zstd compression is enabled.

## Important APIs, Types, and Functions
The main test routines are `test_compress()`, `test_gzio()`, `test_deflate()`, `test_inflate()`, `test_large_deflate()`, `test_large_inflate()`, `test_flush()`, `test_sync()`, `test_dict_deflate()`, `test_dict_inflate()`, and `main()`. It uses zlib-compatible types and APIs from the wrapper: `Byte`, `uLong`, `z_stream`, `compress()`, `uncompress()`, `gzopen()`, `gzputc()`, `gzputs()`, `gzprintf()`, `gzseek()`, `gztell()`, `gzgetc()`, `gzungetc()`, `gzgets()`, `gzread()`, `gzclose()`, `deflateInit()`, `deflate()`, `deflateParams()`, `deflateSetDictionary()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateSetDictionary()`, `inflateSync()`, and `inflateEnd()`. Wrapper-specific integration uses `ZWRAP_isUsingZSTDcompression()` and `zstdVersion()`.

## Control Flow, State, and Persistence
`main()` checks zlib version compatibility, prints zlib and optional zstd versions, allocates cleared compression/decompression buffers, then runs each test. Non-`Z_SOLO` builds first validate `compress()`/`uncompress()` and `gz*` file I/O against `foo.gz` or a CLI-provided path. Small-buffer deflate/inflate force one-byte input/output chunks. Large-buffer tests compress zero-heavy data, feed already-compressed bytes through `deflateParams()`, and verify decompressed byte counts. Dictionary tests store `dictId` from the compressor stream adler and require the inflater to request and accept the same dictionary. `test_flush()` and `test_sync()` are guarded out when `ZWRAP_isUsingZSTDcompression()` reports zstd mode.

## Dependencies and Integration Points
The file depends on `zstd_zlibwrapper.h`, libc allocation/string I/O, and optional `Z_SOLO` custom allocators. It is built by the zlibWrapper Makefile into both `example` and `example_zstd`, providing a compact compatibility test for wrapper builds and gzip wrapper object integration.

## Risks and Test Signals
Risks include assuming zlib-only semantics such as `inflateSync()` recovery, which is why those tests are disabled under zstd compression, and relying on gzip seek/read behavior from wrapper-provided `gz*` functions. Signals include exact string round trips, expected `gzseek()`/`gztell()` positions for the longer wrapper test string, successful large inflate output count, successful dictionary ID handoff, and clean exit from both normal and zstd-linked binaries.
