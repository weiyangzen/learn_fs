# sources/compression/zlib/inflate.c

## Purpose
`inflate.c` is zlib's main decompression engine for zlib-wrapped, gzip-wrapped, and raw deflate streams. It owns stream initialization, reset, header/trailer processing, block decoding, dictionaries, sync recovery, state copying, and validation knobs.

## Important APIs, Types, and Functions
Public APIs include `inflateInit_()`, `inflateInit2_()`, `inflateResetKeep()`, `inflateReset()`, `inflateReset2()`, `inflatePrime()`, `inflate()`, `inflateEnd()`, `inflateGetDictionary()`, `inflateSetDictionary()`, `inflateGetHeader()`, `inflateSync()`, `inflateSyncPoint()`, `inflateCopy()`, `inflateUndermine()`, `inflateValidate()`, `inflateMark()`, and `inflateCodesUsed()`. Key internals are `inflateStateCheck()`, `updatewindow()`, `syncsearch()`, and the bit macros.

## Control Flow, State, and Persistence
`inflate()` is a resumable state machine over modes from `HEAD` through `DONE` or error modes. It parses zlib/gzip/raw headers, handles optional gzip fields, validates dictionaries, decodes stored/fixed/dynamic blocks, builds Huffman tables with `inflate_table()`, uses `inflate_fast()` for large buffers, validates checksums and gzip length trailers, updates the sliding window on return, and reports `Z_BUF_ERROR` when no progress is possible. Persistent state lives in `struct inflate_state`, including mode, wrapper flags, checks, window, bit accumulator, tables, and match-copy bookkeeping.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`, and uses `adler32()`, `crc32()`, allocator hooks, and zlib public stream fields. It is the core implementation behind `inflate()` users and `gzread.c`.

## Risks and Test Signals
Risks include malformed header handling, partial-call resumability, dictionary ID validation, distance/window bounds, dynamic table oversubscription, checksum/length trailer mismatches, and memory allocation failure for the window. Tests should include split-input streaming, every flush mode, zlib/gzip/raw wrappers, gzip optional fields and header CRC, preset dictionaries, sync recovery, `inflateCopy()`, and sanitizer/fuzzer malformed inputs.
