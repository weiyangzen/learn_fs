# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadWhileWriting.java

Purpose: tests visibility and lease recovery semantics when one client reads a file while another client has written and flushed but not closed it, then a different user appends after soft lease expiry.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSOutputStream.hflush`, `HdfsDataInputStream.getVisibleLength`, `UserGroupInformation`, `RecoveryInProgressException`, `RemoteException`, lease limits via `cluster.setLeasePeriod`, and `DFSTestUtil.getFileSystemAs`.

Control flow: the test starts a four-DN cluster, shortens heartbeat and soft lease limits, creates a file, writes half a block, and hflushes without closing. `checkFile` opens as another user, checks visible length, and reads expected byte values. The original lease renewer is interrupted; after sleeping beyond soft lease limit a different UGI opens a new filesystem and retries `append` until lease recovery completes, writes another half block, and closes. A final read checks the full block.

State and persistence behavior: exercises under-construction file length visibility, client lease renewal, soft lease expiry, append lease recovery, and completed-file length after close. The hard lease remains long so the scenario specifically depends on soft-limit takeover.

Dependencies and integration points: integrates DFS output hflush, HDFS visible length semantics, lease renewer, append recovery RPCs, UGI-based clients, and cross-user filesystem access.

Risks and edge cases: timing-sensitive due to sleep-based lease expiry and retry loops. `append` catches only `RecoveryInProgressException` wrapped in `RemoteException`. The test writes the same byte sequence twice with offset zero, so final read expects modulo half-block sequence repeated rather than a strictly increasing full-block sequence.

Test signals: `getVisibleLength() >= expectedsize`, byte-by-byte read equality, append eventually succeeds after recovery, and no unexpected RemoteException escapes.
