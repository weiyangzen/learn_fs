# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestTruncateQuotaUpdate.java

## Purpose

`TestTruncateQuotaUpdate` verifies storage-space quota deltas computed by `INodeFile.computeQuotaDeltaForTruncate` with and without snapshots and with snapshot/current block divergence.

## Important APIs, Types, and Functions

The helper builds mock `INodeFile` instances with `BlockInfoContiguous` blocks, `PermissionStatus`, fixed `BLOCKSIZE=1024`, replication `4`, and monotonically increasing block/genstamp/inode IDs. `addSnapshotFeature` creates a mocked `FileDiff`, a `FileDiffList`, injects a `DiffListByArrayList` using `Whitebox`, and attaches `FileWithSnapshotFeature`.

## Control Flow

Tests create a 2.5-block file and compute quota delta for truncation to 1.5 blocks, one block, and zero. Without snapshots, the delta removes current replicated bytes. With snapshots and no divergence, truncating inside a snapshotted block may require allocating a new full block and boundary/zero truncates do not reclaim snapshot-retained blocks. With divergence, current blocks not present in the snapshot can be reclaimed while snapshotted blocks remain charged.

## State and Persistence Behavior

All state is in-memory inode, block, and snapshot diff state. The behavior is persistence-relevant because snapshot diffs keep old block references alive after namespace operations.

## Dependencies and Integration Points

The test targets namespace quota accounting across inode block arrays, snapshot diff lists, and truncate code. It depends on internal snapshot feature representation and uses Whitebox to construct minimal state.

## Risks and Edge Cases

Quota deltas must avoid double-counting snapshotted blocks while accounting for replacement blocks needed for copy-on-truncate. The test includes a duplicated comment label in the divergence case, but assertions still cover partial and full truncations.

## Test Signals

Signals are exact replicated storage-space deltas: `-512*4`, `-1536*4`, `-2560*4`, `+1024*4`, `0`, and divergence deltas that reclaim only non-snapshotted current bytes.
