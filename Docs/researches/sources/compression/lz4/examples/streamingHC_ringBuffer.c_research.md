# sources/compression/lz4/examples/streamingHC_ringBuffer.c

## Purpose
This example mirrors the ring-buffer streaming example but uses LZ4 high-compression mode for compression and normal safe streaming decode for decompression.

## Important APIs, Types, and Functions
It includes `lz4hc.h` and `lz4.h`. Compression uses `LZ4_streamHC_t` and `LZ4_compress_HC_continue()`. Decompression uses `LZ4_streamDecode_t` and `LZ4_decompress_safe_continue()`. Helpers read and write `int32_t` sizes and compare decoded output to input.

## Control Flow
`test_compress()` reads random-length chunks into a static ring buffer, compresses with the HC stream, writes size and payload, and wraps the input offset. `test_decompress()` reads each block, decodes into an intentionally larger decode buffer, writes decoded bytes, and wraps. `main()` supports an optional `-p` pause flag, compresses, decompresses, compares, and optionally waits for Enter.

## State and Persistence
The HC stream retains compression history in the ring buffer, and decode state tracks previous decoded bytes. Persistent files are `<input>.lz4s-9` and `<input>.lz4s-9.dec`.

## Dependencies and Integration Points
It is built by the examples Makefile and links against both regular and HC LZ4 APIs. The sample demonstrates that HC compression produces blocks compatible with standard LZ4 decompression.

## Risks
Like the other streaming examples, the file format is custom and host-endian. Error handling is minimal, and random chunking can vary by C library. The optional pause is interactive and unsuitable for automated runs unless omitted.

## Test Signals
`make test` expects `Verify : OK`. Useful extended tests include files that force ring-buffer wraparound and comparisons between HC and regular streaming output sizes.
