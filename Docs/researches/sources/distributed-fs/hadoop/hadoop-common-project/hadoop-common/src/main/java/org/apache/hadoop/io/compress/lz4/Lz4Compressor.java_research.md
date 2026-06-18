# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Compressor.java

Purpose: Hadoop `Compressor` adapter backed by `net.jpountz.lz4`, supporting regular and high-compression LZ4 modes with direct ByteBuffer staging.

Important APIs and control flow: constructors select `LZ4Factory.fastestInstance().fastCompressor()` or `highCompressor()`, allocate direct input and output buffers, and size the output buffer using the LZ4 compress-bound formula. `setInput()` validates user arrays, copies data into the direct input buffer when possible, or stores the user buffer for later chunking. `needsInput()` returns false while compressed output, a full input buffer, or saved user data remains. `compress()` drains pending compressed bytes first, then fills the input direct buffer from saved data if needed, calls `compressDirectBuf()`, clears input state, updates byte counters, and returns up to the caller's requested length.

State and persistence: state includes direct buffers, saved user buffer offsets, `finish`/`finished`, `uncompressedDirectBufLen`, `bytesRead`, and `bytesWritten`. No persistent storage; `reset()` clears buffers/counters and `end()` is a no-op.

Dependencies and integration: implements Hadoop `Compressor`, uses `Configuration` only for `reinit()` reset semantics, and depends on lz4-java. It is used by Hadoop block compression streams that follow the `needsInput()`/`setInput()`/`compress()` contract.

Risks and test signals: test with input larger than direct buffer, empty `compress()` calls, small output buffers, `finish()`/`finished()` transitions, and both HC/non-HC construction. The class is synchronized; behavior changes should preserve thread safety and direct-buffer position/limit discipline.
