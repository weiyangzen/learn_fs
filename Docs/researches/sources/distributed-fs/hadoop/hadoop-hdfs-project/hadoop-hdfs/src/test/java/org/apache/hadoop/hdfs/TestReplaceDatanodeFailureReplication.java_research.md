# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeFailureReplication.java

Purpose: verifies write-pipeline behavior when DataNodes fail and `dfs.client.block.write.replace-datanode-on-failure.min.replication` controls whether the client can continue with fewer live replicas or must fail.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `HdfsDataOutputStream.getCurrentBlockReplication`, `ReplaceDatanodeOnFailure.write(Policy.ALWAYS, ...)`, `HdfsClientConfigKeys.BlockWrite.ReplaceDatanodeOnFailure.MIN_REPLICATION`, `SubjectInheritingThread`, `FSDataInputStream`, and rack-aware cluster setup.

Control flow: `setupCluster` configures the minimum replacement replication threshold and starts three DNs on one rack. The main helper starts one or more `SlowWriter` threads that write incrementing bytes and hflush, waits, stops DataNodes at a selected pipeline position, waits again, checks current block replication or expected failure, interrupts writers, closes streams, and verifies file contents. Dedicated tests fail the first or last DN, leave only one DN alive, and check behavior when live DNs are below the configured threshold.

State and persistence behavior: mutates active write pipelines, DataNode liveness, client block-output stream replication tracking, and partially written file contents. It does not require NameNode restart, but relies on block reports after DN failures.

Dependencies and integration points: integrates client-side pipeline replacement policy, DataTransfer write pipeline, hflush visibility, rack configuration, and DataNode stop behavior.

Risks and edge cases: slow writer timing and sleep durations make the suite timing-sensitive. Expected exception behavior depends on the precise threshold and best-effort flag. The content verifier returns after the first EOF, so it verifies files sequentially but exits the method on the first completed file; this limits multi-file verification depth.

Test signals: `getCurrentBlockReplication()` equals configured minimum for survivable cases, IOException is thrown when replacement cannot satisfy minimum replication, writers close cleanly, and file byte sequences match write order.
