
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DecompressorStream.java

## Purpose
`DecompressorStream` is the standard `CompressionInputStream` implementation for stream-oriented decompressors and the base class for block-framed decompression.

## Important APIs and Types
It keeps a protected `Decompressor`, input buffer, EOF and closed flags, skip buffer, single-byte buffer, and `lastBytesSent` for concatenated stream handling. It implements `read`, `decompress`, `getCompressedData`, `resetState`, `skip`, `available`, `close`, and mark/reset disabling.

## Control Flow
`read()` validates the stream and arguments, then calls `decompress()`. The default decompression loop calls the decompressor until bytes are produced. If the decompressor is finished with remaining input, it resets and resends leftover bytes to support concatenated members; if finished with no remaining input, it tries to read more compressed data before EOF. If input is needed, it reads from the underlying stream and feeds the decompressor.

## State and Persistence
The stream stores current compressed input bytes in `buffer`, the last amount sent to the decompressor for leftover offset calculation, and EOF/closed flags. No persistent state is written.

## Dependencies and Integration
Used by `DefaultCodec`, `GzipCodec`, `ZStandardCodec`, native `BZip2Codec`, and as a superclass for `BlockDecompressorStream` and passthrough stream. It depends on `Decompressor.getRemaining()` semantics for concatenated streams.

## Risks
A decompressor that repeatedly returns zero without changing state can cause a loop. The leftover offset logic depends on `lastBytesSent` representing the original buffer load, so changes here can break concatenated streams. `available()` returns only 0 or 1, which is conventional but not a byte count.

## Test Signals
Gzip and zlib concatenation behavior is covered through gzip/zlib tests and SequenceFile reads. `TestCodecPool` verifies `DoNotPool` closed decompressor behavior. `TestBlockDecompressorStream` covers subclass behavior.
