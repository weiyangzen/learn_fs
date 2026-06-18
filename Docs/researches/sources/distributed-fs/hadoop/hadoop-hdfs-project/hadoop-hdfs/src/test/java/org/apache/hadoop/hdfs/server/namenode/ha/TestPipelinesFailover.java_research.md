# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPipelinesFailover.java

Purpose: stress and regression coverage for HDFS write pipelines, block allocation/completion idempotence, lease recovery, block synchronization, and DataNode failure handling across HA NameNode failover.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology(NN_COUNT)`, `FSDataOutputStream`, `AppendTestUtil`, `DistributedFileSystem.recoverLease`, `BlockManagerTestUtil`, `RetryInvocationHandler`, `DatanodeProtocolClientSideTranslatorPB.commitBlockSynchronization`, `InternalDataNodeTestUtils.spyOnBposToNN`, `DelayAnswer`, `HAStressTestHarness`, and `MultithreadedTestUtil`.

Control flow: `doWriteOverFailoverTest` writes a block and a half, flushes, fails over either gracefully or by restarting the old active, verifies the new active has no pending/corrupt/missing block state, then either forces another `allocateBlock` or closes to test `completeFile` idempotence before checking contents. DN-failure tests continue writes after failover, stop DNs, fail back, and validate data. Lease recovery tests create an under-construction file, fail over, recover the lease as another user, and then fail back. The synchronization test delays a DN's `commitBlockSynchronization`, fails over while delayed, confirms the old standby rejects the write, and retries recovery on the new active. The stress test runs many pipeline/lease recovery threads while a harness triggers replication work and periodic failovers.

State and persistence behavior: exercises under-construction file leases, block IDs and generation stamps, edit-log replay to standbys, client retry/failover state, DataNode-to-NameNode block recovery RPCs, and pipeline membership after DN loss.

Dependencies and integration points: integrates client failover, block manager accounting, DataNode BPOfferService RPC translators, user impersonation, shell debug collection, and HA stress harness threads.

Risks and test signals: risks include duplicate block allocation, file completion replay bugs, lost block locations, lease recovery stuck on the old active, and failed pipeline updates after DN loss. Signals include full file content checks, block-manager zero-count assertions, expected standby write rejection during delayed synchronization, and multi-threaded stress completion without propagated exceptions.
