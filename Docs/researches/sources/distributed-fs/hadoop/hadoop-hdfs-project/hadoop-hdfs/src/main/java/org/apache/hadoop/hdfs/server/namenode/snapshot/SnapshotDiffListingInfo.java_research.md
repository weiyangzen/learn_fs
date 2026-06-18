# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDiffListingInfo.java

## Purpose

`SnapshotDiffListingInfo` accumulates a bounded page of snapshot diff entries for the listing-style snapshot diff API controlled by `dfs.snapshotDiff-report.limit`. It tracks where computation stopped so clients can resume across RPC calls.

## Important APIs, Types, And Functions

Important state includes `maxEntries`, `snapshotRoot`, `snapshotDiffScopeDir`, `from`, `to`, `lastPath`, `lastIndex`, and separate `modifiedList`, `createdList`, and `deletedList`. Main APIs are `addDirDiff`, `addFileDiff`, `setLastPath`, `setLastIndex`, `getEarlier`, `getLater`, `isFromEarlier`, and `generateReport`.

## Control Flow

As recursive diff traversal finds a changed directory, `addDirDiff` first emits a modified directory entry if room remains, then appends created entries from the `ChildrenDiff`, then deleted entries, computing rename targets for deleted `WithName` references. If the page fills, it records the parent path and an index into the created/deleted stream and returns false to stop traversal. File changes are added as modified entries or set the last path if the page is full. `generateReport` returns the page plus cursor state.

## State And Persistence Behavior

The object is request-scoped and not persisted. Cursor fields `lastPath` and `lastIndex` are returned to clients in `SnapshotDiffReportListing` so the next RPC can resume. The class stores paths as byte arrays to match internal HDFS path handling.

## Dependencies And Integration Points

It depends on `SnapshotDiffReportListing`, `ChildrenDiff`, inode/reference classes, `DFSUtilClient` path byte helpers, and `ChunkedArrayList`. It is produced by `DirectorySnapshottableFeature.computeDiff` and returned by `SnapshotManager.diff` listing overload.

## Risks And Edge Cases

The index cursor spans created and deleted lists by offsetting deleted indexes by created-list size; off-by-one errors can duplicate or skip entries. `maxEntries` applies across all three lists. Resume path logic in the caller must align with `lastPath` and `lastIndex`. Rename target discovery is scoped to `snapshotDiffScopeDir`, which can differ from the root.

## Test Signals

Tests should force page boundaries before directory modify entries, inside created lists, inside deleted lists, and at file modifications. They should verify resume cursor correctness, no duplicate/skipped entries across pages, rename target inclusion, direction flags, and zero/one-entry limits.
