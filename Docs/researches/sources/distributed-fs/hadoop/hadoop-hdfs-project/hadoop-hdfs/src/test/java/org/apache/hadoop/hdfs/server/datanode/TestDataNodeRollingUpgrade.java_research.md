# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeRollingUpgrade.java

## Purpose

`TestDataNodeRollingUpgrade` verifies DataNode behavior during HDFS rolling upgrade prepare, finalize, rollback, regular upgrade after rolling upgrade, block trash handling, layout-version changes, and DataXceiver peer tracking.

## Important APIs, Types, and Functions

Key helpers are `startCluster`, `shutdownCluster`, `triggerHeartBeats`, `getBlockForFile`, `getTrashFileForBlock`, `deleteAndEnsureInTrash`, `ensureTrashRestored`, `isTrashRootPresent`, `isBlockFileInPrevious`, `startRollingUpgrade`, `finalizeRollingUpgrade`, `rollbackRollingUpgrade`, `rollingUpgradeAndFinalize`, and static `addDataNodeLayoutVersion`. The suite uses `DFSAdmin -rollingUpgrade prepare/finalize`, `MiniDFSCluster` restart APIs, `BlockLocalPathInfo`, `ReplicaInfo`, `BlockPoolSliceStorage`, `DataNodeLayoutVersion`, and `LayoutVersion.updateMap`.

## Control Flow

Setup starts a one-DataNode cluster with one-MiB block size and captures the NameNode, DataNode, filesystem, and block pool ID. Rolling-upgrade prepare enters safemode, runs DFSAdmin prepare, triggers heartbeats, and expects dataset trash enabled. Deleting a file during rolling upgrade moves its block file from current storage into DataNode trash. Finalize runs DFSAdmin finalize, triggers heartbeats, and expects trash disabled and deleted files to remain deleted. Rollback stops the DataNode, restarts the NameNode with `-rollingupgrade rollback`, restarts the DataNode with `-rollback`, and expects trash-restored blocks and contents.

The layout-change tests start rolling upgrade, delete files into trash, stop the DataNode, inject an older DataNode layout version, restart to trigger layout upgrade, and verify trash is moved to `previous`. Finalize removes `previous`; rollback restores the first two files and leaves no trash/previous block files. `testDatanodeRUwithRegularUpgrade` performs a rolling upgrade/finalize, restarts NameNode with regular `-upgrade`, writes another file, and finalizes upgrade. `testDatanodePeersXceiver` opens three DFS clients and streams, writes large buffers, and checks DataNode peer/xceiver accounting remains internally consistent before and after close.

## State and Persistence Behavior

The suite directly validates on-disk block files, trash directories, `previous` directories, DataNode block pool storage, and layout-version metadata. It uses `@TempDir` for cluster base storage. Rolling upgrade state is persisted through NameNode/DataNode restart and rollback paths. File contents are read before deletion and compared after rollback.

## Dependencies and Integration Points

It integrates DataNode FsDataset block-local path lookup, block pool trash, NameNode rolling-upgrade commands, DFSAdmin, MiniDFSCluster restart/rollback options, layout-version feature maps, client DFS streams, and DataXceiver peer tracking. It is a critical persistence regression suite for upgrade safety.

## Risks and Edge Cases

The tests are tagged slow and have long timeouts because upgrade/rollback and heartbeats are timing-heavy. They assume test files have a single block. `addDataNodeLayoutVersion` mutates global layout-version state for testing. The path rewrite in `isBlockFileInPrevious` depends on storage directory naming. A failed cleanup or missed heartbeat can make trash state appear stale.

## Test Signals

Signals include dataset trash enabled/disabled at the right phases, block files moving from current to trash, trash restoration after rollback, deleted files remaining deleted after finalize, file contents matching after rollback, block files moving to and out of `previous` across layout changes, successful regular upgrade after rolling finalize, and stable peer/xceiver counts around multiple open streams.
