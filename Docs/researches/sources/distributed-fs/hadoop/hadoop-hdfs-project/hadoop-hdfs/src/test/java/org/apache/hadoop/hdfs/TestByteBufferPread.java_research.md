<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java

Purpose: Validates positional read (`pread`) and `readFully` behavior when reading into heap and direct `ByteBuffer` instances.

Important APIs, types, and functions: `FSDataInputStream.read(long, ByteBuffer)`, `FSDataInputStream.readFully(long, ByteBuffer)`, heap `ByteBuffer.allocate`, direct `ByteBuffer.allocateDirect`, buffer `position`, `limit`, `hasRemaining`, and content checks with `assertArrayEquals`.

Control flow: `setup` starts a three-DataNode cluster with 4 KiB HDFS blocks and writes a deterministic 12-block random file. `testPreadWithHeapByteBuffer` and `testPreadWithDirectByteBuffer` run the same helper matrix. Helpers read the whole file with repeated preads, attempt a read into a full buffer, read into a half-limited buffer, read into a buffer whose initial position is half full, pread starting at the file midpoint, and use `readFully` for the entire file.

State and persistence behavior: Static test state includes the cluster, filesystem, deterministic byte array, file path, and seeded `Random`. The test file persists only for the class lifetime and is deleted during `shutdown`.

Dependencies and integration points: Exercises HDFS client input streams, positional read code paths, block boundary traversal across a multi-block file, direct-buffer handling, and standard Java NIO buffer state semantics.

Risks: The shared `Random` is advanced by helper calls that fill dummy buffers, but those bytes are only compared to same-call snapshots. The file content is deterministic, making regressions reproducible. The suite is less exhaustive than legacy `TestPread` and focuses on ByteBuffer-specific behavior.

Test signals: Success means reads advance buffer positions correctly, respect limits and existing positions, do not modify full buffers, return correct half-file slices for positioned reads, and produce byte-for-byte equality for both heap and direct buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java -->
