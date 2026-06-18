
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.java

## Purpose
`Bzip2Decompressor` is the native/JNI-backed `Decompressor` implementation for bzip2.

## Important APIs and Types
It implements `Decompressor`. Constructors configure conserve-memory mode and direct buffer size. Key methods include `setInput`, `needsInput`, `finished`, `decompress`, `getBytesWritten`, `getBytesRead`, `getRemaining`, `reset`, `end`, and static `initSymbols`.

## Control Flow
`setInput()` copies compressed user bytes into a direct input buffer and resets the direct output buffer to empty. `decompress()` drains any remaining direct output, otherwise calls native `inflateBytesDirect()` unless already finished, then exposes bytes to the user buffer. `needsInput()` refills the direct compressed buffer from the saved user buffer when needed.

## State and Persistence
State includes a native stream pointer, direct buffers, compressed buffer offsets/lengths, user buffer offsets/lengths, conserve-memory setting, and finished flag. Methods are synchronized. There is no durable persistence.

## Dependencies and Integration
Loaded and selected by `Bzip2Factory` when native bzip2 is configured and available. Used by `BZip2Codec` native input paths and pooled by `CodecPool`.

## Risks
As with the compressor, native lifecycle errors can leak or invalidate the stream. `getRemaining()` combines Java and native remaining bytes and is important for concatenated-stream handling in `DecompressorStream`. Dictionaries are unsupported.

## Test Signals
`TestBzip2CompressorDecompressor` validates native bzip2 decompression and multithreaded independent instances when native support is present.
