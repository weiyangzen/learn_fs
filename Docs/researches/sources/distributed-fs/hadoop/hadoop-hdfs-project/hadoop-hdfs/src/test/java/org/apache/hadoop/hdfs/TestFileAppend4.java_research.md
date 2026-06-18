# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend4.java

## Purpose

`TestFileAppend4.java` focuses on append and sync recovery around HDFS-200 and HDFS-142. The complete 396-line file was read. It tests lease recovery after a writer finalizes a block but stalls before `completeFile`, recovery followed by a different lease holder writing, needed-replication updates for appended blocks, and failure behavior when the last block has no live locations.

## Important APIs, Types, and Functions

Key APIs are `NamenodeProtocols.complete`, `DFSClient.create`, `FSDataOutputStream.append`, `GenericTestUtils.DelayAnswer`, Mockito `spy/doAnswer`, `LeaseExpiredException`, `cluster.setLeasePeriod`, `DFSTestUtil.waitReplication`, `LocatedBlocks`, `FSDirectory`, and `INodeFile`. The helper `recoverFile` repeatedly opens the file for append under a short lease period, closes the recovered stream, and fails if recovery takes longer than a minute.

## Control Flow

Each test configures short heartbeats, reconstruction intervals, and client socket retries. `testRecoverFinalizedBlock` spies the NameNode RPC, delays `complete`, closes a DFSClient stream on a separate thread until the delay triggers, interrupts the lease renewer, and has another user recover the file; when the original close resumes it must fail because the file is no longer open. `testCompleteOtherLeaseHoldersFile` repeats but has the new lease holder append data before releasing the old close, expecting a lease-owner mismatch. Replication and insufficient-location tests create files, append, start/stop DataNodes, wait for replication state, and inspect the inode to ensure failed append leaves the file closed.

## State and Persistence Behavior

State includes delayed NameNode completion RPCs, lease-renewer thread state, NameNode lease ownership, block replication queues, and inode under-construction flags.

## Dependencies and Integration Points

The test integrates DFSClient lease renewal, NameNode protocol completion, block manager replication accounting, DataNode liveness recognition, and low-level namespace inspection through `FSDirectory`.

## Risks and Edge Cases

Risks include old writers completing files after lease recovery, recovery taking too long, appended blocks not entering needed-replication queues, and failed append transitions leaving an inode under construction.

## Test Signals

Signals are expected `LeaseExpiredException` messages, successful recovery append open, `DFSTestUtil.waitReplication` to replication 2, expected IO failure for insufficient locations, and `!inode.isUnderConstruction()` after failed append.
