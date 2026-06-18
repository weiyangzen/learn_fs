# sources/compression/zlib/gzlib.c

## Purpose
`gzlib.c` implements common `gzFile` operations shared by reading and writing: open, descriptor wrapping, buffer sizing, seeking, telling, offset reporting, EOF/error handling, and internal error-message management.

## Important APIs, Types, and Functions
Public functions include `gzopen()`, `gzopen64()`, `gzdopen()`, optional `gzopen_w()`, `gzbuffer()`, `gzrewind()`, `gzseek64()`, `gzseek()`, `gztell64()`, `gztell()`, `gzoffset64()`, `gzoffset()`, `gzeof()`, `gzerror()`, and `gzclearerr()`. Key internals are `gz_open()`, `gz_reset()`, `gz_error()`, `gz_intmax()`, `LSEEK`, and Windows CE `gz_strwinerror()`.

## Control Flow, State, and Persistence
`gz_open()` parses mode flags, allocates `gz_state`, preserves a display path, opens or adopts the descriptor, records the initial read position, and calls `gz_reset()`. Seeking normalizes `SEEK_SET`/`SEEK_CUR` into uncompressed skip state, rewinding for backward reads and synthesizing zero output for forward write seeks elsewhere. Errors are stored in `state->err` and optional allocated `state->msg`.

## Dependencies and Integration Points
It depends on `gzguts.h`, POSIX-like `open()`, `lseek()`, `fcntl()`, `close()` elsewhere, and Windows wide-character support. `gzread.c` and `gzwrite.c` consume the initialized `gz_state` and pending `skip` requests.

## Risks and Test Signals
Risks include mode-string ambiguity, nonblocking descriptor flags, large-file truncation through narrow APIs, allocation failure while constructing path/error messages, and seeking in transparent versus compressed streams. Tests should cover mode combinations (`r`, `w`, `a`, `T`, `G`, `e`, `x`, `N`), rewind, forward/backward seek, tell/offset consistency, and error clearing.
