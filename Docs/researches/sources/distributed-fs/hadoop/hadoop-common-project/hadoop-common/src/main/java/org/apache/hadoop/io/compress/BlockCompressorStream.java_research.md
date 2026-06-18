
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockCompressorStream.java

## Purpose
`BlockCompressorStream` adapts a `Compressor` to Hadoop's block-framed compression format for codecs such as Snappy and LZ4 whose native compression operates on bounded blocks rather than indefinite zlib-style streams.

## Important APIs and Types
It extends `CompressorStream`. Constructors accept an `OutputStream`, `Compressor`, output buffer size, and compression overhead; the default constructor uses a 512-byte buffer and 18-byte zlib-style overhead. The key overrides are `write(byte[], int, int)`, `finish()`, and `compress()`.

## Control Flow
Each logical block begins with a big-endian 4-byte uncompressed length. The stream then writes one or more big-endian length-prefixed compressed chunks. `write()` flushes the current block when adding more input would exceed `MAX_INPUT_SIZE`, splits oversized user buffers into separate compressed chunks, and resets the compressor after completed blocks. `finish()` emits the current uncompressed length, marks the compressor finished, and drains compressed output.

## State and Persistence
The only local immutable state is `MAX_INPUT_SIZE = bufferSize - compressionOverhead`; inherited state includes the compressor, output buffer, and closed flag. There is no durable persistence, but the emitted wire format is stateful and must be decoded by `BlockDecompressorStream`.

## Dependencies and Integration
`SnappyCodec` and `Lz4Codec` construct this stream with codec-specific overhead calculations. It depends on `Compressor.getBytesRead()` to know the current block's uncompressed byte count and on `Compressor.reset()` being safe after each completed block.

## Risks
The framing format is Hadoop-specific; raw Snappy/LZ4 readers cannot decode it directly. Incorrect overhead values can make compressed chunks exceed buffer expectations or reduce block size unnecessarily. A compressor that reports bytes-read incorrectly will corrupt block lengths. `finish()` can emit a zero-length block for empty compressed files, which the paired block decompressor treats as EOF.

## Test Signals
`TestBlockDecompressorStream`, `TestSnappyCompressorDecompressor`, `TestLz4CompressorDecompressor`, and `CompressDecompressTester` exercise round trips, EOF handling, and the block stream pair under codec-specific compressors.
