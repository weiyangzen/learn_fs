
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Decompressor.java

## Purpose
`Decompressor` is the pluggable streaming decompression engine interface used by decompression streams and pooled codec instances.

## Important APIs and Types
Methods include `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.

## Control Flow
Callers provide compressed input when `needsInput()` is true, call `decompress()` until bytes are produced or terminal state changes, inspect `finished()` and `getRemaining()` to handle concatenated streams, and reset or end the instance for reuse or cleanup.

## State and Persistence
Implementations own compressed input buffers, decompressed output buffers, byte counters, and native state. The interface itself has no storage.

## Dependencies and Integration
Implemented by zlib, gzip, Snappy, LZ4, ZStandard, native bzip2, dummy bzip2, and passthrough stubs. `DecompressorStream` depends on `getRemaining()` to preserve concatenated stream data.

## Risks
Callers must keep the input buffer stable until `needsInput()` becomes true. Incorrect remaining-byte accounting breaks concatenated streams. Implementations that require dictionaries cannot be satisfied by generic Hadoop streams and currently cause EOF-like behavior in `DecompressorStream`.

## Test Signals
Codec-specific decompressor tests, `TestCodecPool`, `TestBlockDecompressorStream`, and native bzip2 tests exercise this lifecycle.
