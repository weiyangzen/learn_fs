
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SnappyCodec.java

## Purpose
`SnappyCodec` provides Hadoop's Snappy compression using block-framed streams and direct decompression support.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. It creates `SnappyCompressor`, `SnappyDecompressor`, `SnappyDirectDecompressor`, `BlockCompressorStream`, and `BlockDecompressorStream`, and returns `.snappy`.

## Control Flow
No-argument streams borrow compressors/decompressors from `CodecPool`. Output reads `io.compression.codec.snappy.buffersize`, computes overhead as `bufferSize / 6 + 32`, and uses `BlockCompressorStream`. Input uses `BlockDecompressorStream` with the same configured buffer size. Direct decompression always creates a new `SnappyDirectDecompressor`.

## State and Persistence
State is the mutable `Configuration conf`. Stream output is Hadoop's length-prefixed block format containing Snappy-compressed chunks.

## Dependencies and Integration
Depends on Snappy compressor/decompressor classes and `CommonConfigurationKeys`. Integrated with factory discovery, block stream tests, and direct decompression consumers.

## Risks
Methods assume `conf` is set. Direct decompressor behavior differs from `BlockDecompressorStream` and may require complete block destination space. Hadoop framing may not be interoperable with non-Hadoop Snappy file formats.

## Test Signals
`TestSnappyCompressorDecompressor`, `CompressDecompressTester`, and `TestCodecFactory` cover block round trips, direct decompression, edge cases, and discovery.
