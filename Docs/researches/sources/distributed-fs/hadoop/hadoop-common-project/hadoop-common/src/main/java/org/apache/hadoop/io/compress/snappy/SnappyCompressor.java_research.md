# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyCompressor.java

Purpose: Hadoop `Compressor` implementation backed by Xerial Snappy, using direct buffers to bridge Hadoop's byte-array API to `Snappy.compress(ByteBuffer, ByteBuffer)`.

Important APIs and control flow: `setInput()` validates input and either copies into the direct input buffer or saves the user buffer for later chunking. `needsInput()` accounts for pending compressed output, full direct input, and saved user data. `compress()` drains pending output, initializes output buffer, feeds saved data when no input is staged, compresses the direct buffer with `Snappy.compress`, clears consumed input, sets `finished` once saved user data is exhausted, and updates byte counters.

State and persistence: maintains direct buffers, saved user buffer offsets, input length, finish flags, and read/write counters. `reset()` clears all in-memory state; `end()` is a no-op.

Dependencies and integration: implements Hadoop `Compressor`, uses `Configuration` only for `reinit()` reset, and depends on `org.xerial.snappy.Snappy`. It integrates with Hadoop compression streams and codec pooling.

Risks and test signals: test with inputs larger than 64 KiB, tiny output arrays, empty input after `finish()`, and counter values. There is no synchronization, unlike the LZ4 class, so callers must respect Hadoop compressor threading assumptions.
