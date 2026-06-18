<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzread.c -->
# sources/compression/zstd/zlibWrapper/gzread.c

## Purpose
`gzread.c` implements the read side of zlib-style `gzFile` access for the wrapper, including transparent file reads, gzip/ZSTD header detection, decompression, seeking-by-skipping, character reads, line reads, pushback, direct-mode detection, and read-close cleanup.

## Important APIs, Types, and Functions
Internal functions are `gz_load()`, `gz_avail()`, `gz_look()`, `gz_decomp()`, `gz_fetch()`, `gz_skip()`, and `gz_read()`. Public functions include `gzread()`, `gzfread()`, `gzgetc()`, `gzgetc_()`, `gzungetc()`, `gzgets()`, `gzdirect()`, and `gzclose_r()`.

## Control Flow
Reads start with `gz_read()`, which honors pending seeks, copies existing output, fetches more output, or decompresses directly into large user buffers. `gz_fetch()` drives the `LOOK`/`COPY`/`GZIP` state machine. `gz_look()` allocates buffers and initializes an inflate stream on first use, reads enough input to inspect magic bytes, then enters compressed mode for gzip magic `1f 8b` or ZSTD magic prefix `28 b5`, transparent copy mode for plain input, or EOF/trailing-garbage handling. `gz_decomp()` loops through `inflate()`, translating zlib return codes into `gz_error()` state.

## State and Persistence
Read state is stored in `gz_state`: input buffer, double-sized output buffer, `how`, `direct`, `eof`, `past`, `x.have`, `x.next`, `x.pos`, and the embedded `z_stream`. `gzungetc()` mutates output-buffer state and position to allow pushback. `gzclose_r()` frees buffers, ends inflate state, closes the descriptor, and frees the handle.

## Dependencies and Integration Points
Because `gzguts.h` includes `zstd_zlibwrapper.h`, calls to `inflateInit2()`, `inflateReset()`, `inflate()`, and `inflateEnd()` can be wrapper-resolved. `gz_look()` adds a wrapper-specific two-byte ZSTD magic recognition path so `gz*` reads can feed ZSTD frames into the wrapper's inflate implementation.

## Risks
Only the first two bytes of the ZSTD magic are checked at the `gz_look()` level; full confirmation is delegated to wrapper inflate. Partial headers and transparent-mode detection keep upstream zlib tradeoffs, including ambiguity for one-byte gzip-like files. `gzgets()` treats embedded NULs as user responsibility. Direct and compressed state transitions are delicate around concatenated streams and trailing garbage.

## Test Signals
Strong tests include reading gzip, ZSTD, and transparent files; concatenated compressed streams; trailing garbage; short and partial headers; direct reads into large user buffers; `gzgetc`, `gzungetc`, and `gzgets`; seeking forward/backward; EOF and error reporting; and read-close behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzread.c -->
