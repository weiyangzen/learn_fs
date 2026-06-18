# sources/compression/lz4/tests/decompress-partial.c

## Purpose
This compact standalone test validates `LZ4_decompress_safe_partial()` when the compressed input buffer is exact or includes small trailing slack.

## Important APIs, Types, and Functions
`main()` uses `LZ4_compress_default()` to create an LZ4 block from a static lorem source and calls `LZ4_decompress_safe_partial()` in a loop. The fixed `BUFFER_SIZE` is 2048 bytes for source, compressed, and output buffers.

## Control Flow, State, and Persistence
After compression, the loop runs with input sizes from `cmpSize` to `cmpSize + 9`. Each decompression must return `srcLen`, avoid negative errors, and reproduce the static string byte-for-byte. The test has no persistent state, no heap allocation, and exits immediately on failure.

## Dependencies and Integration Points
It includes only stdio/string headers and `lz4.h`. It is a direct signal for the public partial decompression API and provides a simpler counterpart to dictionary and fuzz coverage.

## Risks and Test Signals
The main coverage gap is that it only targets a single small lorem payload and full target output, not a true early-stop target smaller than the source. Its signal is focused: trailing compressed input bytes must be tolerated without corrupting the decoded prefix or result size.
