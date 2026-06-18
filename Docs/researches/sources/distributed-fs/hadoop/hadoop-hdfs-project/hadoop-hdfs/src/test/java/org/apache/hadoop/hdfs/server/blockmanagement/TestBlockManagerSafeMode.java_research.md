
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManagerSafeMode.java

## Purpose
`TestBlockManagerSafeMode` is a white-box unit suite for `BlockManagerSafeMode`. It validates the safe-mode state machine, safe-block counters, extension timing, datanode thresholds, future-generation-stamp handling, extension configuration parsing, monitor interval logging, and user-facing safe-mode tips.

## Important APIs, Types, and Functions
The test uses `BlockManagerSafeMode.BMSafeModeStatus` values `OFF`, `PENDING_THRESHOLD`, and `EXTENSION`; mocked `FSNamesystem`; a spied `BlockManager`; a spied `DatanodeManager`; and `Whitebox` access to private `status`, `blockSafe`, `datanodeThreshold`, and `extension`. Helpers include `setSafeModeStatus`, `setBlockSafe`, `setDatanodeThreshold`, `getblockSafe`, `waitForExtensionPeriod`, `injectBlocksWithFugureGS`, and mock setup for decrement paths.

## Control Flow and State
`setupMockCluster` configures safe-mode threshold, extension, and minimum datanodes, initializes NameNode metrics, and stubs locks/running state. Initialization tests assert `activate` moves status to `PENDING_THRESHOLD`. `testCheckSafeMode1` through `testCheckSafeMode10` cover threshold pending, extension entry, zero-extension exit, active-transition blocking, monitor-driven exit, zero total blocks, and valid/invalid monitor interval logging. Counter tests increment and decrement contiguous and striped safe blocks, ensuring counters cap at threshold and become no-ops after leaving safe mode. Datanode threshold tests vary live-node counts and configured minimums. Future-GS tests verify normal exit is blocked, force exit clears bytes-in-future, and safe-mode tips include loss warnings.

## Dependencies and Integration Points
The file integrates with `DFSConfigKeys`, `NameNode.initMetrics`, `GenericTestUtils.waitFor`, `LogCapturer`, `BlockReportReplica`, `NumberReplicas`, and lock-mode-aware FSNamesystem mocks. It intentionally avoids MiniDFSCluster and points readers to broader safe-mode integration suites.

## Risks and Test Signals
Risks include timing flakiness in monitor-thread tests, brittle private-field reflection, and typoed helper names that still compile but obscure intent. Test signals are precise for state transitions, counter boundaries, extension parsing of raw milliseconds and time suffixes, and safe-mode user messages under normal, datanode-threshold, and future-GS conditions.
