# sources/compression/zlib/examples/zpipe.c

## Purpose
`zpipe.c` is a compact example program showing correct streaming use of zlib `deflate()` and `inflate()` on `stdin` and `stdout`. With no arguments it compresses; with `-d` it decompresses.

## Important APIs, Types, and Functions
The main routines are `def(FILE *source, FILE *dest, int level)`, `inf(FILE *source, FILE *dest)`, `zerr(int ret)`, and `main()`. They use `z_stream`, `deflateInit()`, `deflate()`, `deflateEnd()`, `inflateInit()`, `inflate()`, and `inflateEnd()`, with `CHUNK` fixed at 16384 bytes.

## Control Flow, State, and Persistence
Compression repeatedly reads input chunks, selects `Z_FINISH` only at source EOF, drains deflate output until the output buffer is not full, then asserts stream completion. Decompression reads input chunks, inflates until each output buffer is not full, converts `Z_NEED_DICT` to `Z_DATA_ERROR`, and reports incomplete streams as data errors. State is limited to local buffers, the zlib stream, and standard I/O binary mode; no files are opened directly.

## Dependencies and Integration Points
It depends on `zlib.h`, libc file I/O, and platform-specific `_setmode()` wrappers for DOS/Windows-like systems. It is an example and smoke-test style integration for the public zlib stream API.

## Risks and Test Signals
Risks are mainly example limitations: fixed buffer size, stdin/stdout-only operation, and assert usage that assumes zlib contract invariants. Useful signals are byte-exact compression/decompression round trips, correct nonzero returns on invalid compressed input, and binary-mode preservation on Windows.
