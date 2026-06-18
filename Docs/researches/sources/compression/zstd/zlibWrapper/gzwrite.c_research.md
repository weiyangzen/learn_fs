<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzwrite.c -->
# sources/compression/zstd/zlibWrapper/gzwrite.c

## Purpose
`gzwrite.c` implements the write side of `gzFile`, including buffered writes, gzip compression, transparent direct writes, formatted writes, flush/parameter changes, seek-by-zero-fill, and write-close finalization.

## Important APIs, Types, and Functions
Internal functions are `gz_init()`, `gz_comp()`, `gz_zero()`, and `gz_write()`. Public functions include `gzwrite()`, `gzfwrite()`, `gzputc()`, `gzputs()`, `gzvprintf()`, `gzprintf()`, `gzflush()`, `gzsetparams()`, and `gzclose_w()`.

## Control Flow
The first write lazily initializes input and output buffers and, unless transparent mode is requested, initializes `deflateInit2()` with gzip headers (`MAX_WBITS + 16`). `gz_write()` consumes pending seek requests by compressing zero bytes, buffers small writes, and sends large writes directly to `gz_comp()`. `gz_comp()` writes directly when `direct` is true or loops through `deflate()`, flushing full output buffers to the descriptor. `gzclose_w()` handles pending zero-fill, finishes the stream with `Z_FINISH`, frees buffers, ends deflate state, closes the descriptor, and releases the handle.

## State and Persistence
Per-handle write state includes buffers, `x.pos` as the uncompressed offset, compression level/strategy, pending seek/skip, and the embedded `z_stream`. Formatted output uses the double-sized input buffer to reserve room for `vsnprintf()`. There is no on-disk metadata beyond the compressed or direct byte stream written to the descriptor.

## Dependencies and Integration Points
The file uses the wrapper-resolved `deflate*()` family through `gzguts.h`. This means gzip-file writes may use zlib or ZSTD behavior depending on wrapper global compression mode. It also depends on POSIX `write()`/`close()` and the shared `gz_error()`.

## Risks
`gzsetparams()` can call `deflateParams()` after flushing with `Z_BLOCK`; wrapper ZSTD compression reports unsupported block/full flush in its deflate implementation, so changing parameters may behave differently under ZSTD mode. Formatted output has historical zlib compatibility branches with tricky buffer-fit checks. Direct mode bypasses compression but still uses the `gz*` state machine.

## Test Signals
Tests should write compressed and transparent data, close and reopen for verification, exercise small and large writes, `gzputc`, `gzputs`, `gzprintf`, `gzflush`, `gzsetparams`, forward seek zero-fill, write errors, and `gzclose_w()` finalization under both zlib and wrapper-ZSTD modes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzwrite.c -->
