# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotMetrics.java

## Purpose
`TestSnapshotMetrics` verifies metrics emitted for snapshot operations and snapshot state. It checks FSNamesystem gauges for counts and NameNodeActivity counters for operation calls across allow, disallow, list, create, delete, rename, and diff report operations.

## Important APIs, Types, and Functions
The suite uses `MetricsAsserts.getMetrics`, `assertGauge`, `assertCounter`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, and `SnapshottableDirectoryStatus`. It reads metrics records named `NameNodeActivity` and `FSNamesystem`.

## Control Flow
`setUp` creates two files under `/TestSnapshot/sub1`. `testSnapshottableDirs` enables nested snapshots, checks zero metrics, allows snapshots on multiple directories, confirms gauges and counters, repeats `allowSnapshot` on an existing snapshottable directory to verify the operation counter increments while the gauge does not, disallows/deletes snapshottable directories, and verifies listing increments `ListSnapshottableDirOps`. `testSnapshots` checks create snapshot metrics, including a failed create attempt on a non-snapshottable directory that still increments the operation counter, then validates snapshot gauge changes for create/delete and operation counters for diff and rename.

## State and Persistence Behavior
Metrics are in-process runtime state in the `MiniDFSCluster`. The tests do not restart or persist metrics, but they tie gauges to namespace state and counters to attempted operations.

## Dependencies and Integration Points
This file integrates snapshot APIs with Hadoop metrics2 exposure. It also depends on nested snapshot allowance in `SnapshotManager` to create nested snapshottable directories for metric coverage.

## Risks and Edge Cases
The suite covers a common metrics ambiguity: counters should track attempted operations, including failures or idempotent calls, while gauges should track actual current namespace state. It also verifies delete of a snapshottable subtree decrements the snapshottable directory gauge.

## Test Signals
Signals are exact metric values after each operation sequence and an assertion that `getSnapshottableDirListing` returns the expected single surviving directory.
