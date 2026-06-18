# sources/compression/zstd/tests/fuzz/seekable_roundtrip.c

## Purpose

`seekable_roundtrip.c` fuzzes the zstd seekable format by compressing an input into a seekable stream, then randomly selecting an offset and length and verifying seekable decompression returns the matching slice of the original input.

## Important APIs And Functions

The entry point uses `ZSTD_seekable_createCStream()`, `ZSTD_seekable_initCStream()`, `ZSTD_seekable_compressStream()`, `ZSTD_seekable_endStream()`, `ZSTD_seekable_create()`, `ZSTD_seekable_initBuff()`, and `ZSTD_seekable_decompress()`. It sizes the compressed buffer as `ZSTD_compressBound(size) + ZSTD_seekTableFooterSize`.

## Control Flow

The fuzzer reserves prefix bytes for parameter choices, allocates compressed and decompressed buffers, selects compression level, checksum flag, requested uncompressed slice length, and offset. It initializes the seekable compressor, streams all input through it, finalizes the stream, then initializes a seekable reader over the resulting in-memory buffer.

For decompression, it repeatedly calls `ZSTD_seekable_decompress()` for the same `(offset, uncompressedSize)` request until the accumulated decompressed byte count reaches the requested length or a zero-size return stops progress. It asserts exact requested byte count and compares the output with `src + offset`.

## State And Persistence

`stream` and `zscs` are static seekable decompression/compression contexts. They persist under `STATEFUL_FUZZING` and are freed after each input otherwise. The compressed and decompressed buffers are per input.

## Dependencies And Integration Points

This target integrates zstd's seekable extension (`zstd_seekable.h`) with normal zstd compression bounds and fuzz data production. It tests in-memory seek table parsing, checksum option handling, streaming compression, and random-access decompression.

## Risks And Edge Cases

Edges include empty input, zero-length reads, reads ending at the final byte, checksum on/off, repeated decompression calls that must make progress, and compressed buffer sizing that accounts only for the footer overhead. If the seekable format emits more metadata than expected, compression could overrun the expected bound and assert.

## Test Signals

The primary signal is exact slice equality for arbitrary offsets and lengths. Failures point to seek table generation/parsing errors, checksum interaction bugs, offset accounting problems, or state reuse issues in seekable contexts.
