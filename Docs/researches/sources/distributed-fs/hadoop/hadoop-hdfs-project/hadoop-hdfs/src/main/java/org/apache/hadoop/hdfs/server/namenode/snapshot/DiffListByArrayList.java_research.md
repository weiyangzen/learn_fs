# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListByArrayList.java

## Purpose

`DiffListByArrayList` is the simple `DiffList<T>` implementation used for ordered snapshot diff lists when skip-list acceleration is disabled. It wraps a Java `ArrayList` and exposes the minimal indexed, searchable, iterable, append/prepend, and range APIs expected by `AbstractINodeDiffList` and directory/file snapshot diff consumers.

## Important APIs, Types, And Functions

The class is generic over `T extends Comparable<Integer>`, which matches diff objects comparable by snapshot ID. The public surface is `get`, `isEmpty`, `size`, `remove`, `addLast`, `addFirst`, `binarySearch`, `iterator`, and `getMinListForRange`. `getMinListForRange` returns `list.subList(startIndex, endIndex)`, so callers receive the raw chronological range without pre-combined diff shortcuts.

## Control Flow

Creation flows through `DirectoryDiffListFactory.createDiffList` or direct construction with an initial capacity. Snapshot diff insertion appends for normal in-memory operations and prepends during FSImage load because serialized diffs are read in reverse order. Binary search delegates to `Collections.binarySearch` against snapshot IDs. Deletion delegates to `ArrayList.remove`.

## State And Persistence Behavior

State is only the in-memory list. The class does not serialize itself; its contents are persisted by `SnapshotFSImageFormat` or `FSImageFormatPBSnapshot` through the owning diff list. In ordered snapshot deletion mode, `remove` asserts that only index `0` is removed, matching the first-snapshot-only deletion invariant.

## Dependencies And Integration Points

It depends on `DiffList`, `INodeDirectory` only for the interface signature, and `SnapshotManager.isDeletionOrdered()` for the deletion assertion. It integrates with `DirectoryWithSnapshotFeature.DirectoryDiffList`, `FileDiffList`, and FSImage loaders through `addFirst`/`addLast` ordering semantics.

## Risks And Edge Cases

Range reconstruction is linear and can be expensive for directories with many snapshots. `subList` is a view, so structural changes to the backing list while a caller holds the range would be unsafe. The ordered-deletion invariant is enforced only by `assert`, so production JVMs without assertions rely on callers to obey it. Index arguments are not validated beyond `ArrayList` exceptions.

## Test Signals

Useful tests cover binary-search insertion-point behavior, reverse-order FSImage load via repeated `addFirst`, ordered deletion rejecting nonzero removals when assertions are enabled, and equivalence with `DiffListBySkipList.getMinListForRange` for the same diff sequence.
