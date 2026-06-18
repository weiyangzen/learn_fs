# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/Snapshot.java

## Purpose

`Snapshot` represents a read-only snapshot of an HDFS subtree. It provides snapshot IDs, naming/path helpers, ID comparators, latest-covered-snapshot lookup, legacy FSImage read/write, and the `Snapshot.Root` directory view used as the snapshot root inode.

## Important APIs, Types, And Functions

Important constants are `CURRENT_STATE_ID` and `NO_SNAPSHOT_ID`. Static helpers include `generateDefaultSnapshotName`, `generateDeletedSnapshotName`, `getSnapshotPath`, `getSnapshotName`, `getSnapshotId`, `getSnapshotString`, `ID_COMPARATOR`, `ID_INTEGER_COMPARATOR`, and `findLatestSnapshot`. Instance APIs include `getId`, `getRoot`, `compareTo`, equality/hash by ID, and `write`. `Snapshot.Root` extends `INodeDirectory`.

## Control Flow

Creating a snapshot copies the source directory into a `Root`, sets its parent, and optionally sets the local snapshot name. Historical child lookups through `Root` delegate to the parent directory's snapshot-aware child-list methods. `findLatestSnapshot` walks ancestor directories and asks their diff lists to update the best prior snapshot below an anchor. Legacy read/write serialize the ID and root directory inode.

## State And Persistence Behavior

A snapshot stores immutable `id` and a `Root`. The root copy preserves ACL, XAttr, and quota features; quota features are copied rather than shared where needed. A root can be marked as deleted by an XAttr used by ordered snapshot deletion. Snapshot name is the root local name. Equality and hash code depend only on snapshot ID.

## Dependencies And Integration Points

The class integrates with `DirectorySnapshottableFeature`, `SnapshotManager`, `INodeDirectory`, FSImage serialization, `ContentSummaryComputationContext`, ACL/XAttr/quota feature classes, and HDFS `.snapshot` path conventions.

## Risks And Edge Cases

`CURRENT_STATE_ID` is intentionally near `Integer.MAX_VALUE`, and comparators rely on subtraction, so IDs must remain within the configured 28-bit snapshot ID space. `generateDefaultSnapshotName` uses wall-clock millisecond precision and can collide under very fast repeated calls, so higher layers still check duplicate names. `Root.metadataEquals` intentionally compares ACL feature references, which is stricter than value equality.

## Test Signals

Tests should verify default and deleted snapshot names, `.snapshot` path construction, ID comparator ordering with null/current state, root delegation for child/content summary access, deleted-marker XAttr behavior, quota/ACL/XAttr preservation, legacy FSImage round trip, and latest-snapshot lookup across ancestors.
