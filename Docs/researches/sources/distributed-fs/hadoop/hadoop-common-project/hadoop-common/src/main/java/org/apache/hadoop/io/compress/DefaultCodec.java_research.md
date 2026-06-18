
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DefaultCodec.java

## Purpose
`DefaultCodec` is Hadoop's default deflate/zlib codec. It exposes zlib compression and decompression through standard Hadoop streams and supports direct decompression.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. It delegates compressor/decompressor type and instance creation to `ZlibFactory`, constructs `CompressorStream`/`DecompressorStream`, and returns `.deflate`.

## Control Flow
No-argument stream creation uses `CompressionCodec.Util` and `CodecPool`. Supplied-compressor streams use the configured `io.file.buffer.size`. Direct decompressor creation calls `ZlibFactory.getZlibDirectDecompressor(conf)`.

## State and Persistence
State is the mutable `Configuration conf`. No persistent data is stored; compressed output is zlib/deflate stream data.

## Dependencies and Integration
Depends on `ZlibFactory` and `IO_FILE_BUFFER_SIZE_*`. It is registered by default in `CompressionCodecFactory` when no codec list is supplied and is widely used by SequenceFile/TFile tests.

## Risks
Many methods assume `conf` is non-null; normal construction through `ReflectionUtils` with `Configurable` should set it, but direct callers must do so. Behavior varies with native zlib availability and zlib configuration.

## Test Signals
`TestSequenceFile`, `TestSequenceFileAppend`, `TestCodecPool`, `TestCodecFactory`, and stream reuse tests exercise the default codec heavily.
