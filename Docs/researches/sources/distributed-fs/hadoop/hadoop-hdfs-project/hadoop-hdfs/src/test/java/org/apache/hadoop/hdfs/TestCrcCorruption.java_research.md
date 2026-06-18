<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java

Purpose: Tests HDFS checksum/corruption handling during writes and reads, including corruption injected into packet data and entirely corrupt files across one or more DataNodes.

Important APIs, types, and functions: `DFSClientFaultInjector`, `MiniDFSCluster`, `DFSTestUtil`, `DataNode`, `ReplicaInfo`, `ExtendedBlock`, `FSDataInputStream`, `FSDataOutputStream`, `ChecksumException`, `BlockMissingException`, and `IOUtils`. The file uses Mockito to mock client fault injection.

Control flow: `setUp` installs a mocked DFS client fault injector. `testCorruptionDuringWrt` writes initial data, flushes, injects one corrupt packet followed by an uncorrupt packet and expects the final file to read successfully; it then creates the file again, injects corruption without repair, and expects write/close to fail after retry exhaustion. `testCrcCorruption` runs `thistest` twice, once with default checksum/block settings and once with 17-byte checksums and 34-byte blocks. `thistest` creates 40 replicated files, waits for replication, then on the first DataNode cycles through finalized replicas deleting meta files, truncating meta files to two bytes, or corrupting meta files. The surviving second replica should keep all files readable. `testEntirelyCorruptFileOneNode` and `testEntirelyCorruptFileThreeNodes` call a shared helper that corrupts every replica of the first block and verifies reads eventually throw instead of looping forever.

State and persistence behavior: The tests modify DataNode on-disk replica/checksum metadata and global `DFSClientFaultInjector` process state. Cluster lifetime is local to each helper/test path, and corruption state is deliberately local to the MiniDFSCluster. The mock injector is reset to non-corrupting behavior in `testCorruptionDuringWrt`'s `finally` block, but the class does not preserve and restore a previous injector instance.

Dependencies and integration points: Integrates packet checksum creation, client write fault injection, DataNode replica storage, client checksum verification, block-location retry behavior, and read exception translation.

Risks: These tests are sensitive to low-level replica/meta file layout and fault-injector semantics. They use random fixture generation and DataNode internals, so changes in checksum chunk sizing, replica storage abstraction, or client retry policy can change observable exceptions. The disabled replication-reduction validation notes a historical unresolved risk around deleting excess corrupt replicas.

Test signals: Success means injected corruption is detected rather than silently accepted, client reads either recover from good replicas or raise the expected checksum/missing-block failure when every replica is corrupt, and global fault injection state is restored after each test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java -->
