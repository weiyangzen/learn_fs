# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotDeletionGc.java

## Purpose

`SnapshotDeletionGc` is the background timer that completes ordered snapshot deletion. When deletion ordering is enabled, non-earliest snapshots may first be marked deleted and renamed; this GC periodically selects a deleted first snapshot and asks the namesystem to delete it for real.

## Important APIs, Types, And Functions

The class stores `FSNamesystem`, the configured GC period, and an `AtomicReference<Timer>`. Public APIs are `schedule()` and `cancel()`. Internals include `gcDeletedSnapshot(String name)` and nested `GcTask`.

## Control Flow

`schedule` creates a daemon `Timer` once using compare-and-set and schedules `GcTask` at a fixed rate after the configured delay. Each task acquires the FS read lock, calls `SnapshotManager.chooseDeletedSnapshot`, releases the lock, and if a deleted root exists calls `namesystem.gcDeletedSnapshot(snapshotRoot, snapshotName)`. Exceptions during selection are rethrown after logging; exceptions during deletion are logged and swallowed so future timer runs can continue.

## State And Persistence Behavior

The timer state is process-local. Deleted snapshot markers live in snapshot root XAttrs persisted by snapshot/FSImage mechanisms. The GC does not persist progress directly; successful deletion creates normal namespace/edit-log effects through `FSNamesystem.gcDeletedSnapshot`.

## Dependencies And Integration Points

It depends on `FSNamesystem`, `SnapshotManager.chooseDeletedSnapshot`, `Snapshot.Root.getRootFullPathName`, HDFS read locks, configuration keys from `SnapshotManager`, Java `Timer`, and NameNode deletion APIs.

## Risks And Edge Cases

Only one timer is scheduled per instance, but `TimerTask` execution is single-threaded; a long deletion can delay subsequent runs. Selection uses read lock while deletion occurs later through namesystem APIs, so state may change between selection and deletion. If GC is not scheduled when ordered deletion is enabled, marked snapshots can accumulate. A period of zero or negative configuration would be unsafe for `Timer.scheduleAtFixedRate`.

## Test Signals

Tests should cover idempotent scheduling/canceling, no-op when no snapshots are marked deleted, selecting only first deleted snapshots, actual GC through namesystem, exception logging paths, and ordered-deletion integration where a later snapshot is marked then eventually removed after earlier snapshots clear.
