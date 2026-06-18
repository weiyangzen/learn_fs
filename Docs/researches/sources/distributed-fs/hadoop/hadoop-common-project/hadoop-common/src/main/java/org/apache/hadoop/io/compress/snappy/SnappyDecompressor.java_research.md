# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyDecompressor.java

Purpose: Hadoop `Decompressor` plus nested `DirectDecompressor` implementation for Snappy using Xerial's ByteBuffer API.

Important APIs and control flow: `setInput()` stores caller bytes and copies a direct-buffer chunk. `needsInput()` drains pending uncompressed bytes, then refills compressed direct input from saved data or asks for more. `decompress()` drains pending uncompressed output or calls `Snappy.uncompress` through `decompressDirectBuf()`. `decompressDirect(ByteBuffer,ByteBuffer)` temporarily swaps the instance buffers to operate directly on caller-provided direct buffers, advances source/destination positions, and restores original state in `finally`.

State and persistence: holds direct buffers, compressed input length, saved user input offsets, and `finished`. `getRemaining()` intentionally returns 0 for `BlockDecompressorStream`. `SnappyDirectDecompressor` adds `endOfInput` to combine direct source exhaustion with frame completion.

Dependencies and integration: implements Hadoop `Decompressor`/`DirectDecompressor`, depends on Xerial Snappy, and uses direct buffers asserted by direct decompressor calls.

Risks and test signals: cover array and direct-buffer paths, nonzero destination positions, partial outputs, corrupt compressed data, and reset after direct decompression. The direct path assumes Snappy consumes the whole source or throws.
