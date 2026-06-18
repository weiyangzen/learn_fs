<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzlib.c -->
# sources/compression/zstd/zlibWrapper/gzlib.c

## Purpose
`gzlib.c` implements gzip file functions common to read and write paths: opening, buffering policy, seeking/telling, offset reporting, EOF/error handling, and shared error-message construction.

## Important APIs, Types, and Functions
Important functions include `gz_open()`, `gzopen()`, `gzopen64()`, `gzdopen()`, optional `gzopen_w()`, `gzbuffer()`, `gzrewind()`, `gzseek64()`, `gzseek()`, `gztell64()`, `gztell()`, `gzoffset64()`, `gzoffset()`, `gzeof()`, `gzerror()`, `gzclearerr()`, and internal `gz_error()`. `gz_reset()` initializes common read/write stream state.

## Control Flow
`gz_open()` validates path input, allocates `gz_state`, parses the mode string, opens a path or accepts an existing descriptor, records the read start offset, and calls `gz_reset()`. `gzseek64()` normalizes seek requests into a forward skip when possible, rewinds for backward reads, performs raw file seeks for transparent reads, and otherwise records a pending skip for the next read/write call. Error accessors read and clear `state.state->err` and `state.state->msg`.

## State and Persistence
The file owns creation and initialization of the per-handle `gz_state`. It records path strings for diagnostics, current uncompressed position, requested buffer size, mode, compression parameters, direct flag, file descriptor, and pending seek. It persists errors as allocated messages prefixed with the path.

## Dependencies and Integration Points
It depends on descriptor APIs (`open`, `lseek`/`lseek64`, `_wopen` on Windows), `gzguts.h`, and the read/write modules that consume initialized state. The wrapper integration is indirect through the included wrapper header and through later `inflate`/`deflate` calls in read/write code.

## Risks
Mode parsing ignores unknown flags, which preserves zlib behavior but can hide user mistakes. `gzbuffer()` must be called before buffer allocation. Seek semantics on compressed streams are implemented by skipping uncompressed data, so backward seeks can be expensive. Error-message allocation can convert an original error into `Z_MEM_ERROR`.

## Test Signals
Tests should cover all open modes, descriptor opens, append offset behavior, buffer sizing before/after initialization, rewind, forward/backward seeks, transparent reads, compressed reads, write seek zero-fill behavior through downstream code, error retrieval, and clearerr behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzlib.c -->
