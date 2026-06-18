# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSeekBug.java

Purpose: Regression coverage for historical seek bugs in `FSDataInputStream` against both HDFS and local filesystems. It validates large buffered reads followed by small backward/forward seeks, negative seek rejection, and seek-past-EOF rejection.

Important APIs and types: `FSDataInputStream.seek`, `FSDataInputStream.getPos`, `IOUtils.readFully`, `ChecksumFileSystem.getRawFileSystem`, `MiniDFSCluster`, `DFSTestUtil.createFile`, `FileSystem.getLocal`, and JUnit `assertThrows`.

Control flow: `seekReadFile` opens with a 4096-byte buffer, reads an initial 128 bytes, then reads a large 100000-byte range and seeks to 96036 to verify bytes match the deterministic random payload. `smallReadSeek` unwraps checksum filesystems, uses a buffer size of 1, seeks to 100000, then performs nearby seeks to exercise HADOOP-922 behavior. `testSeekBugDFS` creates a 1 MiB HDFS file and runs both helpers. `testNegativeSeek` and `testSeekPastFileSize` create files, perform a valid seek, then assert an `IOException` for invalid offsets. `testSeekBugLocalFS` repeats the main seek check on LocalFS.

State and persistence behavior: Each test creates temporary data (`seektest.dat` or `seekboundaries.dat`) with deterministic seed `0xDEADBEEF`, then deletes or closes cluster resources. LocalFS uses `GenericTestUtils.getTempPath`.

Dependencies and integration points: Exercises HDFS client stream buffering, local raw filesystem behavior, DFS block sizing/default replication, and checksum wrapper behavior.

Risks and test signals: The tests depend on exact byte identity from deterministic random data and on invalid seeks throwing during `seek`. Passing signals that buffered and positioned seek semantics preserve stream position and data integrity across DFS and LocalFS.
