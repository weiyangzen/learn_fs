# sources/compression/zlib/infback.c

## Purpose
`infback.c` implements zlib's callback-driven raw deflate inflater. It is designed for applications that provide input and consume output through callbacks while supplying the sliding window buffer.

## Important APIs, Types, and Functions
The public entry points are `inflateBackInit_()`, `inflateBack()`, and `inflateBackEnd()`. It uses `struct inflate_state`, `inflate_table()`, `inflate_fixed()`, `inflate_fast()`, and callback types `in_func` and `out_func`. Macros such as `PULLBYTE()`, `NEEDBITS()`, `ROOM()`, `LOAD()`, and `RESTORE()` implement the bit-buffer and callback control mechanics.

## Control Flow, State, and Persistence
Initialization validates version, window size, callbacks, and caller-supplied window storage, then allocates inflate state. `inflateBack()` resets to `TYPE`, decodes stored/fixed/dynamic deflate blocks, builds dynamic Huffman tables, optionally delegates literal/length decoding to `inflate_fast()`, writes full windows through `out()`, and returns unused input. State persists only in the z_stream state and caller window for the duration of the session.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It shares optimized decoding with normal `inflate.c`, but expects raw deflate blocks and a caller-managed I/O model.

## Risks and Test Signals
Risks include callback starvation being reported as `Z_BUF_ERROR`, invalid distance checks against the caller window, dynamic table errors, and linking both callback and normal inflate variants with assembler replacements. Tests should cover stored, fixed, dynamic, malformed block types, out-callback failure, in-callback failure, and exact unused-input reporting.
