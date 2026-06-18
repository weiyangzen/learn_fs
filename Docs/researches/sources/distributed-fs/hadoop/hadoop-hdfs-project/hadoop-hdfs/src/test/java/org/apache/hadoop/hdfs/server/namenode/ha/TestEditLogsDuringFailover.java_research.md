# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogsDuringFailover.java

## Purpose
`TestEditLogsDuringFailover` checks edit-log file handling when HA NameNodes start, restart, and fail over. It verifies that standbys do not consume in-progress logs at startup, and that a NameNode transitioning to active finalizes and reads abandoned in-progress shared edits safely.

## Important APIs, Types, And Functions
The tests use `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HAUtil.setAllowStandbyReads`, `NNStorage` edit-file naming helpers, `FSImageTestUtil.createAbortedLogWithMkdirs`, and `NameNodeAdapter.getFileInfo`. Important methods are `testStartup`, `testFailoverFinalizesAndReadsInProgressSimple`, `testFailoverFinalizesAndReadsInProgressWithPartialTxAtEnd`, `testFailoverFinalizesAndReadsInProgress`, `assertNoEditFiles`, and `assertEditFiles`.

## Control Flow
`testStartup` starts both NameNodes in standby and asserts that local and shared edit directories contain no edit files. It transitions NN0 active, verifies that only NN0 local dirs and shared edits get an in-progress segment, writes `/test`, restarts the standby, and asserts the standby neither finalized shared edits nor applied the in-progress segment. After another mkdir and NN0 restart, it transitions NN1 active and checks both edits are visible. The failover helper creates a fake aborted in-progress shared log, optionally appends a partial transaction, transitions a NameNode active, and verifies it can read the complete mkdir operations, ignore the partial tail, finalize the old segment, and open a new segment.

## State And Persistence
The file directly inspects NameNode storage directories and shared edits files. Persistent state includes generated `edits_inprogress_*` and finalized `edits_*` files plus mkdir transactions. It globally disables edit-log fsync for test speed.

## Dependencies And Integration Points
This test integrates NameNode storage layout, shared edits storage, FSImage test utilities, failover activation, and RPC namespace operations. It also uses `GenericTestUtils.assertGlobEquals` to enforce exact directory contents.

## Risks
Incorrect handling can double-replay edits, start replay in the middle of a segment, finalize a segment while a standby is merely starting, or fail activation when a partial transaction exists at the end of an abandoned log. Because it inspects filenames, changes to edit-log naming or txid numbering require coordinated test updates.

## Test Signals
Success is exact edit-file presence or absence, null/non-null file info checks for `/test` and `/test2`, successful activation after reading fake logs, and expected finalized plus next in-progress segment names in the shared edits directory.
