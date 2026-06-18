
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Lz4Codec.java

## Purpose
`Lz4Codec` provides Hadoop's LZ4 compression using block-framed streams.

## Important APIs and Types
It implements `Configurable` and `CompressionCodec`. It creates `Lz4Compressor`, `Lz4Decompressor`, `BlockCompressorStream`, and `BlockDecompressorStream`, and returns `.lz4`.

## Control Flow
No-argument streams use `CompressionCodec.Util` and the pool. Output computes buffer size from `io.compression.codec.lz4.buffersize`, computes compression overhead as `bufferSize / 255 + 16`, and constructs a block compressor stream. Compressor creation also reads `io.compression.codec.lz4.use.lz4hc` to select high-compression mode. Input uses the same configured buffer size for block decompression.

## State and Persistence
State is the mutable `Configuration conf`. The wire format is Hadoop's block framing around LZ4 compressed chunks, not necessarily a raw `.lz4` container format.

## Dependencies and Integration
Depends on `Lz4Compressor`, `Lz4Decompressor`, `CommonConfigurationKeys`, `CodecPool`, and `CodecConstants`. It is discoverable through configured codec lists and factory tests.

## Risks
Methods assume `conf` is set. Buffer size and overhead must remain consistent enough between compressor and decompressor. The `.lz4` extension may suggest interoperability, but the stream framing is Hadoop-specific.

## Test Signals
`TestLz4CompressorDecompressor`, `CompressDecompressTester`, and `TestCodecFactory` validate LZ4 round trips, block streams, and discovery.
