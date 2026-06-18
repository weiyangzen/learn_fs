# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotManager.java

## Purpose

`SnapshotManager` is the NameNode manager for snapshottable directories and snapshots. It enforces snapshot configuration and limits, creates/deletes/renames snapshots, lists snapshot metadata, computes diff reports, handles ordered deletion policy, registers JMX stats, and persists global snapshot counters.

## Important APIs, Types, And Functions

Important state includes `FSDirectory`, capture/open-file flags, descendant diff flag, snapshot limits, ordered-deletion flag, `numSnapshots`, `snapshotCounter`, and `snapshottables`. Key APIs include `setSnapshottable`, `resetSnapshottable`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `diff` overloads, `write`, `read`, `registerMXBean`, `shutdown`, `chooseDeletedSnapshot`, and helper assertions for ordered deletion. `DELETION_ORDERED` is a thread-local exposed to diff cleanup code.

## Control Flow

Construction reads configuration, validates per-directory limit not exceeding filesystem limit, and initializes `DirectoryDiffListFactory`. Creating a snapshot validates the directory, ID space, filesystem limit, and per-directory limit through `DirectorySnapshottableFeature`, then increments counters. Deletion either marks a non-earliest snapshot deleted and renames it when ordered deletion is enabled, or removes it immediately and decrements the global count. Diff calls resolve the snapshot root or allowed descendant scope and delegate recursive computation to the directory feature. JMX beans are built by iterating snapshottable directories and snapshots.

## State And Persistence Behavior

`snapshotCounter` and `numSnapshots` are written to FSImage along with snapshots. The `snapshottables` map is reconstructed during image load. Ordered deletion state is persisted through snapshot-root XAttrs and renamed snapshot roots, not through `SnapshotManager` fields alone. The manager's map is a `ConcurrentHashMap`, but higher-level operations still require FSNamesystem/FSDirectory locks.

## Dependencies And Integration Points

The manager integrates with `FSDirectory`, `FSNamesystem`, `INodeDirectory`, `DirectorySnapshottableFeature`, `LeaseManager`, FSImage formats, edit-log replay, `FSDirXAttrOp`, HDFS protocol status/report classes, MBeans, and `SnapshotDeletionGc`.

## Risks And Edge Cases

Snapshot ID rollover is unsupported after the 28-bit max. Ordered deletion requires only the first snapshot to be physically deleted; deleting later snapshots first creates XAttr-marked entries for GC. Nested snapshottable checks are O(number of snapshottable directories) and can be disabled only for tests. Descendant diff behavior is configuration-dependent. `shutdown` assumes a registered MBean name. `getSnapshottableAncestorDir` has subtle ancestor logic for files versus directories.

## Test Signals

Tests should cover config validation, snapshot ID exhaustion, filesystem and per-directory limits, nested snapshottable rejection, root snapshottable reset behavior, create/delete/rename edit-log replay, ordered deletion marking and GC selection, snapshot listings and JMX beans, descendant-scoped diffs, FSImage counter round trip, and shutdown/register behavior.
