# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryDiffListFactory.java

## Purpose

`DirectoryDiffListFactory` centralizes the choice between array-backed and skip-list-backed directory diff lists. It also owns the randomized level policy used when skip-list directory diffs are enabled.

## Important APIs, Types, And Functions

`createDiffList(int capacity)` invokes a volatile `IntFunction<DiffList<DirectoryDiff>>`. `init(int interval, int maxSkipLevels, Logger log)` records skip-list configuration and installs either `DiffListBySkipList` or `DiffListByArrayList`. `randomLevel()` uses `ThreadLocalRandom` to return a level between `0` and `maxLevels`, advancing to the next level with probability `1 / skipInterval`.

## Control Flow

`SnapshotManager` calls `init` during construction using HDFS snapshot skip-list configuration keys. From then on, `DirectoryWithSnapshotFeature.DirectoryDiffList.newDiffs()` calls `createDiffList`. When a skip-list insertion occurs, `DiffListBySkipList` calls `randomLevel` for the new node.

## State And Persistence Behavior

The factory has process-wide volatile state: the constructor function, skip interval, and maximum levels. These settings are not stored in snapshot diffs or FSImage; the in-memory representation after restart follows current NameNode configuration and rebuilds from persisted linear diffs.

## Dependencies And Integration Points

The factory depends on the two `DiffList` implementations, `DirectoryDiff`, Java `ThreadLocalRandom`, and logging supplied by `SnapshotManager`. It is a configuration integration point for `dfs.namenode.snapshot.skiplist.*` behavior.

## Risks And Edge Cases

`maxSkipLevels > 0` enables skip lists without validating that `interval` is positive; a nonpositive interval could make `Random.nextInt(skipInterval)` fail. Because the state is static and volatile, tests that reinitialize it can affect other tests in the same JVM. Changing configuration across restart changes performance and internal shape, not the serialized snapshot contract.

## Test Signals

Tests should initialize with `maxSkipLevels` zero and positive values, verify created diff-list classes, exercise `randomLevel` bounds, and validate that snapshot behavior is invariant when switching implementations.
