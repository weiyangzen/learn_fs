# sources/compression/zlib/examples/fitblk.c

## Purpose
Demonstrates how to produce a zlib stream that fits within a caller-specified compressed byte budget. It reads uncompressed data from stdin and writes a compressed stream to stdout, using multiple compression/decompression passes to land close to, but not over, the requested size.

## APIs, Types, And Functions
The program uses public zlib APIs `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, and `inflateEnd()`. `partcompress()` compresses stdin into a bounded output buffer until either the buffer fills or input ends. `recompress()` inflates from an existing compressed buffer and recompresses into another bounded buffer. Constants `RAWLEN`, `EXCESS`, and `MARGIN` control intermediate buffering, the first-pass overrun allowance, and final completion slack.

## Control Flow
`main()` parses the target size, allocates `blk`, initializes a deflate stream, and performs a first compression pass into `size + EXCESS`. If all input already fits with at least `EXCESS` bytes spare, it writes the result directly. Otherwise it initializes inflate, resets deflate, recompresses the first overfilled stream into `tmp`, resets both streams, then recompresses only `size - MARGIN` bytes of that second stream into the final `size` buffer and asserts that the stream reaches `Z_STREAM_END`.

## State And Persistence
State is limited to stack buffers, two heap buffers (`blk`, `tmp`), and zlib stream state. There is no file persistence beyond stdin/stdout. `def.total_in` is used for reporting how much uncompressed input made it into the final stream. The program exits on errors via `quit()`.

## Dependencies And Integration
Depends on libc and `zlib.h`. It is an example of using zlib's streaming reset APIs and validates that zlib streams can be treated as intermediate bounded artifacts. It assumes the final consumer accepts a valid zlib-wrapped stream, not raw deflate or gzip.

## Risks And Test Signals
Risks include fragile empirical constants (`EXCESS`, `MARGIN`), assertion-based internal error handling, memory allocation failures, and poor results for very small requested sizes or unusual data. It does not guarantee exact fill, only `<= size`. Test signals are round-tripping the emitted stream with `inflate`, checking output length for many target sizes and data distributions, verifying behavior when input fits early, and running with read/write error injection.
