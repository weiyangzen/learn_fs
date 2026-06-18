# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffListBySkipList.java

## Purpose

`DiffListBySkipList` is an optimized `DiffList<DirectoryDiff>` for directory snapshot diffs. It keeps a linear list for normal indexed access while adding skip pointers that cache combined `ChildrenDiff` values across ranges, reducing the cost of snapshot child-list reconstruction, snapshot deletion, and snapshot diff computation over long diff histories.

## Important APIs, Types, And Functions

The outer class implements `DiffList<DirectoryDiff>`. `SkipListNode` stores one `DirectoryDiff`, a level-0 `next` pointer, and an array of `SkipDiff` entries for higher levels. `SkipDiff` stores the target node and the pre-combined `ChildrenDiff` over that skip. Key methods are `addFirst`, `addLast`, `remove`, `binarySearch`, `iterator`, `getMinListForRange`, and the internal `combineDiff`, `findPreviousNodes`, and node `setSkipDiff4Target` helpers.

## Control Flow

Insertions choose a random level from `DirectoryDiffListFactory.randomLevel()`. `addLast` finds predecessor nodes for all relevant levels, links the new node, and updates predecessors with combined child diffs that cover the skipped interval. `addFirst` inserts before the current first node and, for higher levels, computes combined diffs that include the new element when the new skip has a target. `remove` unlinks the node at every level and either nulls stale skip diffs for tail deletion or combines predecessor and removed-node skip diffs to preserve interval summaries. `getMinListForRange` walks from the starting node, greedily selecting the highest skip whose target remains within the target snapshot ID, returning either the original diff or a synthetic `DirectoryDiff` carrying a combined `ChildrenDiff`.

## State And Persistence Behavior

The persisted state is still just the owning directory diff list; skip levels and cached combined diffs are rebuilt in memory as diffs are loaded with `addFirst`. `skipNodeList` preserves the same indexed order expected by `DiffList`, while `head` and skip pointers are an auxiliary acceleration structure. No skip metadata is written to FSImage.

## Dependencies And Integration Points

This class is selected by `DirectoryDiffListFactory` when the configured max skip levels is positive. It depends on `DirectoryWithSnapshotFeature.DirectoryDiff` and `ChildrenDiff.combinePosterior` to merge directory child changes. It is consumed by directory child-list reconstruction, directory snapshot cleanup, and diff report generation via `DirectoryDiffList.getDiffListBetweenSnapshots`.

## Risks And Edge Cases

Correctness depends on skip interval summaries matching the linear diff sequence after insertions and removals. Bugs in `remove` can leave stale combined diffs and produce incorrect snapshot child views. The implementation assumes sorted chronological diff insertion patterns and uses `Collections.binarySearch` over `skipNodeList`; arbitrary insertion is not supported. Random level generation can produce uneven structures, though indexed fallback remains available. The code is not internally synchronized and depends on NameNode locking.

## Test Signals

Tests should compare skip-list and array-list results for child-list reconstruction, `getMinListForRange`, snapshot deletion at head, middle, and tail, and repeated FSImage load with `addFirst`. Stress tests should use many snapshots, random child creates/deletes, and different skip intervals/max levels to verify output reports and quota/block cleanup match the array-list implementation.
