
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressorStream.java

## Purpose
`CompressorStream` is the standard `CompressionOutputStream` implementation for stream-oriented compressors such as zlib/gzip/zstd and a base for block framing.

## Important APIs and Types
It keeps a protected `Compressor`, output buffer, and closed flag. Constructors validate the output stream, compressor, and buffer size. It implements `write(byte[], int, int)`, `compress`, `finish`, `resetState`, `close`, and single-byte `write`.

## Control Flow
`write()` validates bounds, rejects writes after the compressor is finished, feeds data with `setInput`, and drains output while `needsInput()` is false. `finish()` marks the compressor finished and drains until `finished()` is true. `close()` delegates to `CompressionOutputStream.close()` once and then marks the stream closed.

## State and Persistence
State lives in the compressor and the reusable byte buffer. `resetState()` resets only the compressor, not the underlying output stream. No durable state beyond emitted compressed bytes.

## Dependencies and Integration
Constructed by `DefaultCodec`, `GzipCodec`, `ZStandardCodec`, and native bzip2 paths. `BlockCompressorStream` extends it and overrides framing behavior.

## Risks
The stream assumes the compressor's `needsInput` and `finished` contracts are accurate. It does not explicitly check `closed` in `write()`, so writes after close fail through underlying stream or compressor state rather than a local guard.

## Test Signals
`TestCompressionStreamReuse`, SequenceFile compression tests, and codec-specific round-trip tests validate stream reuse, finish, and data integrity.
