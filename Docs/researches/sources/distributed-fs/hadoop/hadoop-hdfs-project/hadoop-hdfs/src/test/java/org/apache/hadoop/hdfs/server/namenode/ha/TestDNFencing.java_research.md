# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDNFencing.java

## Purpose
`TestDNFencing` is a regression and integration suite for DataNode fencing during HDFS HA failover. It verifies that queued block invalidations, block reports, append-related replica states, and standby `PendingDataNodeMessages` do not cause data loss or corrupt replicas when a standby becomes active while the former active still has deletion commands in flight.

## Important APIs, Types, And Functions
The fixture builds a two-NameNode, three-DataNode `MiniDFSCluster` using `MiniDFSNNTopology.simpleHATopology()`, small block size, long redundancy interval, high replication streams, a short edit-tailing period, and a custom `RandomDeleterPolicy`. Core tests are `testDnFencing`, `testNNClearsCommandsOnFailoverAfterStartup`, `testNNClearsCommandsOnFailoverWithReplChanges`, `testBlockReportsWhileFileBeingWritten`, `testQueueingWithAppend`, and `testRBWReportArrivesAfterEdits`. Helpers include `doMetasave`, `waitForTrueReplication`, `getTrueReplication`, and the nested `RandomDeleterPolicy`.

## Control Flow
Most tests create or append files, force replication changes or block reports, deliberately leave `nn1` believing it is active by aborting edit logs and entering safe mode, then transition `nn2` to active. They trigger heartbeats, full block reports, deletion reports, redundancy rescans, and postponed-misreplicated-block rescans before asserting that the new active converges to safe metadata. Append tests exercise RBW, FINALIZED, OP_ADD, OP_UPDATE_BLOCKS, and OP_CLOSE ordering across failover. `testRBWReportArrivesAfterEdits` delays a DataNode block report to the standby with a Mockito `DelayAnswer`.

## State And Persistence
Persistent state under test is HDFS namespace edits and block replica metadata. The suite stresses transient NameNode state: invalidation queues, pending reconstruction, pending DataNode messages, postponed misreplicated blocks, corrupt replica accounting, and actual DataNode on-disk replica files. `RandomDeleterPolicy` randomizes excess-replica deletion to force the two NameNodes to choose different replicas, amplifying fencing bugs.

## Dependencies And Integration Points
The tests integrate `MiniDFSCluster`, `HATestUtil`, `NameNodeAdapter`, `BlockManagerTestUtil`, `DataNodeTestUtils`, `InternalDataNodeTestUtils`, `AppendTestUtil`, `DFSTestUtil`, `DatanodeProtocolClientSideTranslatorPB`, and Mockito. They validate coordination among HA state transitions, edit log tailing, DataNode heartbeats/block reports, block manager invalidation, and client failover filesystems.

## Risks
The risky behavior is split-brain-like command delivery: a DataNode may hold deletion commands from the old active while the new active needs a different replica set. Regressions can appear as under-replication, pending replication that never drains, corrupt replicas after RBW reports are replayed too late, or non-readable files even though namespace edits appear correct. Tests are timing-sensitive because they rely on reports, heartbeats, delayed RPCs, and redundancy monitor work.

## Test Signals
Success is signaled by zero postponed misreplicated blocks, zero under-replicated and pending-replication counts, zero corrupt replica blocks, successful `DFSTestUtil.readFile` or `AppendTestUtil.check`, and a true physical replica count after DataNode deletions. The metasave logging is diagnostic only.
