# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestTruncatedInputBug.java

Purpose: regression test for HADOOP-1489, where `BufferedInputStream.mark()` interaction with checksum reads could truncate local input.

Important APIs/types/functions: `FileSystem.getLocal`, `FSDataInputStream`, `DataOutputStream`, `seek`, `mark`, config key `io.file.buffer.size`, and `getFileStatus`.

Control flow/state/persistence: writes a zero-filled file of four IO buffers, opens it with the same buffer size, seeks near the end beyond initially buffered data, reads a few bytes, calls `mark(1)`, then reads to EOF and asserts the final position equals file size. The filesystem is closed in `finally`.

Dependencies/integration points: targets `ChecksumFileSystem`/local FS input buffering. Uses real temp local file data under `GenericTestUtils.getTestDir`.

Risks/test signals: catches a narrow but important read-after-seek/mark truncation regression. The note states fixed code makes `mark()` a no-op, so any future mark support must preserve full reads.
