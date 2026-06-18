
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockDecompressorStream.java

## Purpose
`BlockDecompressorStream` is the inverse of `BlockCompressorStream`. It reads Hadoop's block-framed compressed stream and feeds length-prefixed compressed chunks into a `Decompressor`.

## Important APIs and Types
It extends `DecompressorStream` and overrides `decompress`, `getCompressedData`, and `resetState`. It tracks `originalBlockSize` and `noUncompressedBytes` to know when a logical uncompressed block is complete.

## Control Flow
At the start of each block, `decompress()` reads a 4-byte uncompressed block length. A zero length is treated as EOF for a compressed empty file. It repeatedly calls `decompressor.decompress`; when the decompressor needs input, `getCompressedData()` reads the next 4-byte compressed chunk length and then exactly that many bytes from the underlying stream. The block ends once `noUncompressedBytes` reaches `originalBlockSize`.

## State and Persistence
Local state is the current logical block size and number of uncompressed bytes already returned for that block. The inherited buffer can grow if a compressed chunk length exceeds the current buffer. `resetState()` clears block counters and resets the decompressor.

## Dependencies and Integration
It depends on the exact big-endian framing emitted by `BlockCompressorStream`. It is used by `SnappyCodec` and `Lz4Codec`, and test fakes validate edge cases independent of native libraries.

## Risks
Malformed lengths can force large buffer allocation or lead to EOF exceptions. A decompressor that returns zero without `needsInput`, `finished`, or `needsDictionary` changing can spin. The class reports EOF if compressed input ends while fetching a chunk, so truncated data may be seen as EOF in some paths and as `EOFException` in others depending on where truncation occurs.

## Test Signals
`TestBlockDecompressorStream` checks block stream EOF paths and fake decompressor behavior. Snappy and LZ4 compressor/decompressor tests exercise this stream with real block codecs.
