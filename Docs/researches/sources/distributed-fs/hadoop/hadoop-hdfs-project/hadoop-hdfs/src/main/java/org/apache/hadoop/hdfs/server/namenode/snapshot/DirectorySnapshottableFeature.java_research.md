# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectorySnapshottableFeature.java

## Purpose

`DirectorySnapshottableFeature` extends `DirectoryWithSnapshotFeature` for directories where snapshots may be created. It tracks snapshot roots by name, enforces per-directory quota, creates/removes/renames snapshots, captures open files when configured, and computes full or paginated snapshot diff reports.

## Important APIs, Types, And Functions

Important state includes `snapshotsByNames`, a name-sorted `List<Snapshot>`, and `snapshotQuota`. Key APIs include `getSnapshot`, `getSnapshotById`, `getSnapshotList`, `renameSnapshot`, `setSnapshotQuota`, `addSnapshot`, `removeSnapshot`, `computeDiff` overloads, `getSnapshotByName`, `findRenameTargetPath`, and test-oriented `dumpTreeRecursively`.

## Control Flow

Snapshot creation obtains the next ID from `SnapshotManager`, checks quota and duplicate names, creates a `Snapshot`, appends a `DirectoryDiff` marked with the snapshot root, inserts the snapshot by name, updates modification times, and optionally records modifications for open leased files beneath the snapshot root. Removal searches by name, finds the prior covering snapshot, validates ordered-deletion rules, sets reclaim context, calls `snapshotRoot.cleanSubtree`, removes the name entry only after cleanup, and updates mtime. Diff computation resolves `from` and `to` snapshot objects, then recursively walks the earlier snapshot tree, collecting directory `ChildrenDiff`s and file changes while detecting renames through `INodeReference.WithName`.

## State And Persistence Behavior

The name-sorted snapshot list and quota are persisted by FSImage snapshot sections. The chronological diff order lives in the inherited diff list. Snapshot roots preserve metadata through `Snapshot.Root` copies. Ordered deletion can rename/mark snapshots as deleted before a later GC removes them, so snapshots may remain visible internally with a deleted marker and generated `name#id` name.

## Dependencies And Integration Points

The feature integrates with `INodeDirectory`, `SnapshotManager`, `LeaseManager`, `DirectoryWithSnapshotFeature`, `FileWithSnapshotFeature`, `SnapshotDiffInfo`, `SnapshotDiffListingInfo`, `FSImage` loaders/savers, `INodeReference` rename tracking, content summary and quota accounting, and NameNode RPCs for create/delete/rename/list/diff snapshot operations.

## Risks And Edge Cases

There are two orderings to preserve: names in `snapshotsByNames` and chronological IDs in diffs. Rename must reinsert at the correct binary-search position. Diff code must handle null snapshots as current state, descendant-scoped diffs, renames whose target left the snapshot root, and resume paths in paginated diff listing. Snapshot deletion during edit-log replay has special tolerance for old ordered-deletion logs. Open-file capture can fail snapshot creation if lease scanning or modification recording fails.

## Test Signals

Tests should cover duplicate snapshot names, rename ordering, quota limits, snapshot deletion with and without ordered deletion, FSImage round trips, open-file capture, full and paginated diff reports, rename reports under and outside snapshot roots, descendant-scoped diff when enabled, and content summary counts for snapshots and snapshottable directories.
