
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodec.java

## Purpose
`CompressionCodec` is Hadoop's core codec contract tying together compression streams, decompression streams, compressor/decompressor factory methods, implementation types, and default filename extension.

## Important APIs and Types
The interface declares stream creation methods with and without supplied `Compressor`/`Decompressor`, type factories, `createCompressor`, `createDecompressor`, and `getDefaultExtension`. Nested `Util` creates streams using `CodecPool` and ensures borrowed instances are returned on stream close.

## Control Flow
Implementations either construct streams directly or delegate no-argument stream creation to `Util`. `Util.createOutputStreamWithCodecPool` borrows a compressor, calls the codec's compressor-specific stream factory, returns the compressor on construction failure, or records it as tracked on success. Input follows the same pattern for decompressors.

## State and Persistence
The interface itself has no state. The nested utility temporarily owns pooled instances and transfers close-time ownership to `CompressionInputStream`/`CompressionOutputStream` via package-private tracking setters.

## Dependencies and Integration
Every Hadoop codec implementation in this subset implements this interface. `CompressionCodecFactory`, SequenceFile/TFile code, MapReduce input and output formats, and file extension discovery depend on it.

## Risks
Implementations must keep `getCompressorType`/`createCompressor` and `getDecompressorType`/`createDecompressor` consistent or `CodecPool` reuse will be wrong. Streams constructed with user-supplied compressors are not automatically returned to the pool unless created through `Util`.

## Test Signals
`TestCodecFactory`, `TestCodecPool`, `TestCompressionStreamReuse`, SequenceFile tests, and codec-specific round-trip tests collectively validate this contract.
