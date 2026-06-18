# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHASafeMode.java

## Purpose
`TestHASafeMode` is a broad slow suite for safe mode behavior in HA clusters. It validates client retry while active is in safe mode, standby safe-block accounting while edits and block reports arrive in difficult orders, failover into safe mode, replication queue suppression, `isInSafeMode` routing, open-file recovery after crash, snapshot trash root creation, and transition restrictions when safe mode should block active or observer state.

## Important APIs, Types, And Functions
The fixture starts a two-NameNode, three-DataNode cluster with small blocks, frequent heartbeats and edit tailing, and snapshot trash disabled. Key helpers are `restartStandby`, `restartActive`, `assertSafeMode`, and `banner`. Tests include `testClientRetrySafeMode`, `testEnterSafeModeInANNShouldNotThrowNPE`, `testEnterSafeModeInSBNShouldNotThrowNPE`, block-added/removed variants, `testAppendWhileInSafeMode`, `testComplexFailoverIntoSafemode`, `testSafeBlockTracking`, `testBlocksAddedWhileStandbyIsDown`, `testNoPopulatingReplQueuesWhenExitingSafemode`, `testNoPopulatingReplQueuesWhenStartingActiveInSafeMode`, `testIsInSafemode`, `testOpenFileWhenNNAndClientCrashAfterAddBlock`, `testSafeModeExitAfterTransition`, `testNameNodeCreateSnapshotTrashRootOnHASetup`, and transition-blocking tests for active/observer.

## Control Flow
The tests create and delete block-heavy files, roll edit logs, restart active or standby NameNodes with long safe mode extension, trigger block reports/deletion reports, wait for standby catch-up, and assert safe/total block counts through safe mode status strings. Append tests move blocks between under-construction and completed states. Crash recovery manually calls `addBlock` to create a block known only to the NameNode, restarts NameNode and DataNode, then opens and recovers the lease. Transition tests enter safe mode manually and expect configured failures for active or observer transitions.

## State And Persistence
Persistent state includes HDFS files, edits, fsimages, block replicas, snapshot trash roots, and leases. Transient state includes startup safe mode flags, manual safe mode flags, safe and total block counters, minimum live DataNode thresholds, pending deletion and replication queues, missing block counts, standby pending messages, and client last active routing.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `DFSTestUtil`, `HATestUtil`, `NameNodeAdapter`, `BlockManagerTestUtil`, `DFSClientAdapter`, `DFSOutputStream`, `DistributedFileSystem`, `SafeModeAction`, `LambdaTestUtils`, and `SubjectInheritingThread`. The suite connects safe mode with HA failover, block manager accounting, edit tailing, DataNode reporting, client retry, snapshot support, and lease recovery.

## Risks
This is a high-risk area because safe mode accounting depends on ordering among edits, full block reports, incremental block received/deletion reports, and HA transitions. Regressions can leave standby stuck in safe mode, count safe blocks below zero, populate replication queues too early, mark blocks missing during startup, or allow unsafe active/observer transitions. Several assertions parse human-readable safe mode strings, making message changes visible test breaks.

## Test Signals
Signals include successful delayed client mkdir after safe mode exit, safe mode status matching expected safe/total counts, no NPE from repeated enter-safe-mode calls, zero under-replicated/pending-replication queues in standby safe mode paths, correct standby exception for direct `isInSafeMode`, successful lease recovery after crash, snapshot `.Trash` creation only when enabled on the active, and expected `ServiceFailedException` when configured safe mode prevents active or observer transition.
