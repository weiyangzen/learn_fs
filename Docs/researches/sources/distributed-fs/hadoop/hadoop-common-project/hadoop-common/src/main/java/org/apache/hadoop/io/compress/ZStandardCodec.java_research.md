
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/ZStandardCodec.java

## Purpose
`ZStandardCodec` provides Zstandard compression/decompression, including configurable compression level, optional worker threads, buffer sizing, pooling, and direct decompression.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. Static helpers include `getLibraryName`, `getCompressionLevel`, `getCompressionWorkers`, `getCompressionBufferSize`, and `getDecompressionBufferSize`. It creates `ZStandardCompressor`, `ZStandardDecompressor`, and `ZStandardDirectDecompressor`, and returns `.zst`.

## Control Flow
Buffer size comes from `io.compression.codec.zstd.buffersize`; zero means use compressor/decompressor recommended sizes. Compression level and worker count are read from configuration, with negative workers rejected immediately. Output/input stream creation uses `CodecPool`; supplied-compressor streams use standard `CompressorStream`/`DecompressorStream`.

## State and Persistence
State is the mutable `Configuration conf`. Native/JNI state is owned by the compressor/decompressor implementations. No persistent metadata is stored by the codec itself.

## Dependencies and Integration
Depends on `ZStandardCompressor`, `ZStandardDecompressor`, `CommonConfigurationKeys`, and the zstd-jni library name. Integrated with codec factory extension discovery and direct decompression consumers.

## Risks
Methods assume `conf` is set. Negative worker configuration throws, so validation should happen near job setup. Threaded compression can alter resource usage significantly. Buffer size zero delegates to native recommendations, which may vary across library versions.

## Test Signals
`TestZStandardCompressorDecompressor` covers codec streams, direct decompression, buffer sizes, compression workers, and invalid negative worker configuration. `TestCompressionStreamReuse` covers zstd stream reset.
