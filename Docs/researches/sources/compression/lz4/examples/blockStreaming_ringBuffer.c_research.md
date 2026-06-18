# sources/compression/lz4/examples/blockStreaming_ringBuffer.c

## Purpose
This example demonstrates streaming compression and decompression with ring buffers, including an intentionally different decode ring-buffer size to show that compressor and decoder buffers do not need to be synchronized exactly.

## Important APIs, Types, and Functions
It uses `LZ4_stream_t`, `LZ4_streamDecode_t`, `LZ4_compress_fast_continue()`, and `LZ4_decompress_safe_continue()`. Constants define `MESSAGE_MAX_BYTES`, `RING_BUFFER_BYTES`, and `DECODE_RING_BUFFER`. Helper functions read and write host-endian `int32_t` block sizes and raw payloads.

## Control Flow
`test_compress()` reads random-length chunks into a static ring buffer, compresses each chunk, writes size and payload, and wraps when the next maximum message would not fit. `test_decompress()` reads each compressed block, decodes into its own ring buffer, writes output, and wraps based on decode capacity. `main()` compresses, decompresses, and compares.

## State and Persistence
The LZ4 contexts and ring buffers hold prior block history needed by continue-mode APIs. Output files are `<input>.lz4s-0` and `<input>.lz4s-0.dec`.

## Dependencies and Integration Points
It is compiled by the examples build and links against the local LZ4 library. The random chunking uses `rand()` without an explicit seed, which gives deterministic default sequences on many C libraries but is not guaranteed as a format contract.

## Risks
The stream format is example-only and host-endian. File open failures are not handled defensively. Random chunk size can make behavior platform-dependent if `rand()` differs, though the output is immediately decoded by the same run. Production ring-buffer use must respect `LZ4_decoderRingBufferSize()` guidance.

## Test Signals
The expected success signal is `Verify : OK` after compress/decompress/compare. It is also useful to run with small and larger files to exercise wraparound.
