# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/FileAppendTest4.java

`FileAppendTest4` is a JUnit 5 stress test for HDFS append semantics around block, packet, and checksum boundaries. It uses tiny settings: 4-byte checksums, 4-byte write packets, 8-byte blocks, replication 3, and a five-DataNode `MiniDFSCluster`.

`startUp` creates the cluster after `init` writes checksum, block size, and packet-size configuration. `testAppend` allocates deterministic content with `AppendTestUtil.initBuffer`, then runs three nested loops over initial length and two appended lengths. For each tuple it creates a unique file, writes the initial prefix, closes, reopens for append, writes the first appended range, calls `hflush`, writes the second range, closes, verifies the full file with `AppendTestUtil.checkFullFile`, and deletes the path.

Persistent state is limited to per-iteration HDFS files and the static mini-cluster lifecycle; `hflush` intentionally makes the first appended segment visible/durable before close. Dependencies include `MiniDFSCluster`, `DistributedFileSystem`, `HdfsClientConfigKeys`, `DFSConfigKeys`, JUnit lifecycle/test annotations, and `AppendTestUtil`.

Risks are runtime cost from exhaustive combinations and leftover files if a loop fails before deletion. The small block/checksum settings intentionally exercise edge cases that are sensitive to append-pipeline bugs. Test signals are file length and byte-for-byte assertions, exceptions from append/hflush/close, and path names that encode the failing length tuple.
