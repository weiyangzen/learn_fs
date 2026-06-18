# sources/compression/zlib/gzwrite.c

## Purpose
`gzwrite.c` implements write-side `gzFile` operations: buffered writes, direct transparent writes, formatted output, flushing, compression parameter changes, synthetic seek holes, and write close.

## Important APIs, Types, and Functions
Public functions include `gzwrite()`, `gzfwrite()`, `gzputc()`, `gzputs()`, `gzvprintf()`, `gzprintf()`, legacy varargs `gzprintf()` for non-stdarg builds, `gzflush()`, `gzsetparams()`, and `gzclose_w()`. Internal helpers are `gz_init()`, `gz_comp()`, `gz_zero()`, `gz_write()`, and conditionally `gz_vacate()`.

## Control Flow, State, and Persistence
Write state is lazily initialized. Compressed mode allocates input/output buffers and calls `deflateInit2()` with `MAX_WBITS + 16` to emit gzip framing; direct mode writes input bytes unchanged. Small writes accumulate in `state->in`, large writes compress directly from caller buffers, pending seek skips are emitted as zero bytes, and `gz_comp()` handles output buffer draining plus `Z_FINISH` reset. `gzclose_w()` emits pending zeros, finishes compression, releases buffers/deflate state, closes the descriptor, and preserves the strongest error.

## Dependencies and Integration Points
It depends on `gzguts.h`, `write()`, `close()`, `deflateInit2()`, `deflate()`, `deflateReset()`, `deflateParams()`, and standard formatted-output facilities when available. It consumes open/mode/skip/error state from `gzlib.c`.

## Risks and Test Signals
Risks include nonblocking partial writes, formatted-output truncation, insecure fallback formatting when explicitly enabled, parameter changes with buffered input, and integer-return API limits. Tests should cover small and large writes, `gzputc()` buffering, `gzprintf()` overflow behavior, `gzflush()` modes, `gzsetparams()`, transparent `T` mode, seek holes, and close-time trailer correctness.
