# sources/compression/zlib/gzguts.h

## Purpose
`gzguts.h` is the private shared header for zlib `gz*` file operations. It centralizes platform feature macros, gzip file modes, the internal `gz_state` layout, and shared helper prototypes.

## Important APIs, Types, and Functions
It defines `ZLIB_INTERNAL`, `GZBUFSIZE`, `GZ_NONE`, `GZ_READ`, `GZ_WRITE`, `GZ_APPEND`, read submodes `LOOK`, `COPY`, `GZIP`, and `gz_state`/`gz_statep`. `gz_state` embeds the public `gzFile_s` prefix plus file descriptor, path, buffers, direct/transparent mode, read state, write state, seek skip count, error message, and in-place `z_stream`. It declares `gz_error()`, `gz_intmax()`, and platform helpers.

## Control Flow, State, and Persistence
The header owns no runtime flow, but its fields define all persistent state for `gzopen()`, `gzread()`, `gzwrite()`, seeking, error reporting, and closing. The `x` prefix must remain compatible with public `gzgetc()` macro expectations.

## Dependencies and Integration Points
It includes `zlib.h`, libc headers, platform I/O headers, large-file compatibility declarations, and Windows/OS-specific error adaptations. It links the otherwise separate `gzlib.c`, `gzread.c`, `gzwrite.c`, and `gzclose.c` internals.

## Risks and Test Signals
Risks include platform macro drift, large-file offset mismatches, public/private struct prefix breakage, and buffer-size assumptions that require doubling to fit in `unsigned`. Test signals include cross-platform compilation, `gzbuffer()` bounds checks, large-file seek/tell behavior, and macro-compatible `gzgetc()` operation.
