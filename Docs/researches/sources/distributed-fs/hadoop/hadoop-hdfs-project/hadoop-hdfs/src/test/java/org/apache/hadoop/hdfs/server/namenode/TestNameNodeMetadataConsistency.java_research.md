# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetadataConsistency.java

## Purpose
Integration tests for NameNode behavior when DataNodes report blocks with generation stamps in the future. It verifies the special handling applies during startup safe mode and not during normal operation.

## Important APIs, Types, and Functions
- Uses `MiniDFSCluster.changeGenStampOfBlock`, `DFSTestUtil.getFirstBlock`, `DataNodeTestUtils.runDirectoryScanner`, `cluster.stopDataNode/restartDataNode`, and `cluster.restartNameNode`.
- Mutates block manager state using `BlockInfo.delete` and `BlockManager.removeBlock` under `FSNamesystem.writeLock(RwLockMode.BM)`.
- Uses `BlockManagerTestUtil.setStartupSafeModeForTest` and `cluster.triggerBlockReports`.
- Checks `NameNode.getBytesWithFutureGenerationStamps` and `FSNamesystem.getSafeModeTip`.

## Control Flow
- `InitTest` starts a one-DataNode cluster with directory scan interval 1.
- `testGenerationStampInFuture` writes a file, increments its on-disk block generation stamp, runs scanner, stops DataNode, restarts NameNode, removes the stored block from NameNode memory, marks block manager as startup safe mode, restarts DataNode, waits for bytes-with-future-gen-stamps to equal file length, and checks safemode reason.
- `testEnsureGenStampsIsStartupOnly` performs a similar future-generation-stamp setup without setting startup safe mode and expects the future-byte count to remain zero.
- `waitForNumBytes` repeatedly triggers block reports until the expected count appears.

## State and Persistence Behavior
- Directly manipulates DataNode on-disk block metadata generation stamp and NameNode in-memory block map.
- Restart and startup-safe-mode flags determine whether the future-generation report contributes to special metrics/safemode.

## Dependencies and Integration Points
- Integrates DataNode scanner/block reports, block manager metadata consistency checks, NameNode safemode logic, and mini-cluster restart controls.

## Risks and Edge Cases
- Invasive block-manager mutation requires correct BM write lock handling.
- Timing-sensitive around scanners and block reports.
- Assumes future generation stamp change survives DataNode restart/report.

## Test Signals
- Strong targeted signal for metadata consistency protection during startup and for avoiding false positives during non-startup operation.
