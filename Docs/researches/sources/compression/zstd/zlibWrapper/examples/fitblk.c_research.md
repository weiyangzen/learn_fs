# sources/compression/zstd/zlibWrapper/examples/fitblk.c

## Purpose
`fitblk.c` is a zlib-wrapper-adapted version of Mark Adler's example for fitting a compressed stream into a requested block size. It estimates how much stdin can be compressed into a target output size through one initial compression and up to two recompression passes, while routing zlib APIs through `zstd_zlibwrapper.h`.

## Important APIs, Types, and Functions
The key routines are `quit()`, `partcompress()`, `recompress()`, and `main()`. Constants `RAWLEN`, `EXCESS`, and `MARGIN` control the intermediate raw buffer size, extra first-pass output allowance, and final safety margin. It uses `z_stream`, `z_streamp`, `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, `inflateEnd()`, plus wrapper-specific `ZWRAP_isUsingZSTDcompression()` and `zstdVersion()`.

## Control Flow, State, and Persistence
`main()` parses a single numeric target size, prints zlib and optional zstd versions, allocates `blk`, initializes a deflater, and calls `partcompress()` until either stdin ends or `size + EXCESS` output capacity fills. If all input fits with at least `EXCESS` spare bytes, it reports unused capacity and exits. Otherwise it initializes an inflater and temporary buffer, resets deflate state, recompresses the first-pass stream into `tmp`, resets both streams, then recompresses `size - MARGIN` bytes from `tmp` into `blk` with exactly `size` output capacity. The adapted file disables writes of compressed data to stdout and instead prints progress/statistics, making it a behavioral test rather than a binary filter.

## Dependencies and Integration Points
It depends on `zstd_zlibwrapper.h`, stdio/stdlib/assert, stdin input, and zlib-compatible stream semantics. The Makefile builds it as `fitblk` and `fitblk_zstd`, and test targets feed `../doc/zstd_compression_format.md` with target sizes of 10240 and 40960 bytes.

## Risks and Test Signals
Risks include relying on zlib stream behavior in a wrapper whose flush/block semantics differ, using asserts for internal invariants, memory pressure for `size + EXCESS` allocations, and disabled stdout output changing its usefulness as a real filter. Signals include successful runs in both wrapper modes, `ret == Z_STREAM_END` after final recompression, no `Z_MEM_ERROR`/`Z_ERRNO`, sane reported unused byte counts, and valgrind-clean cleanup of deflate/inflate states.
