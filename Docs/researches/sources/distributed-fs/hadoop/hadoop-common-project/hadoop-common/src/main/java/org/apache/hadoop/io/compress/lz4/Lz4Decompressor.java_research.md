# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Decompressor.java

Purpose: Hadoop `Decompressor` adapter for LZ4 using `LZ4SafeDecompressor` and direct buffers.

Important APIs and control flow: construction allocates direct compressed and uncompressed buffers and initializes safe decompression through lz4-java. `setInput()` stores the caller buffer, copies up to `directBufferSize` into the compressed direct buffer, and resets the uncompressed buffer to empty. `needsInput()` first drains uncompressed output, then reloads saved input if present, otherwise asks for more input. `decompress()` drains pending uncompressed bytes, or calls `decompressDirectBuf()` for the current compressed chunk, marks `finished` after saved input is consumed, and returns up to `len`.

State and persistence: tracks compressed buffer length, saved user buffer offsets, direct buffers, and a `finished` flag. `getRemaining()` deliberately returns 0 because Hadoop's block decompressor stream should not use it here. `reset()` reinitializes buffer positions and saved input counters.

Dependencies and integration: implements Hadoop `Decompressor`, depends on lz4-java. It does not support dictionaries and has no direct decompressor nested class in this file.

Risks and test signals: important tests include chunk boundaries at direct-buffer size, partial output reads, malformed LZ4 data exceptions from lz4-java, and ensuring `needsInput()` does not release user buffers early. Note the logger is created with `Lz4Compressor.class.getName()`, which is harmless but can confuse log attribution.
