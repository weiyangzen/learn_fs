<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native.go

## Purpose
Implements the portable native snapshotter, which materializes each active snapshot as a full copied directory on the backing filesystem rather than using overlay composition.

## Important APIs, Types, And Functions
`snapshotter` stores `root` and `*storage.MetaStore`. Public snapshotter methods are `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, and `Close`. Helpers are `createSnapshot`, `getSnapshotDir`, and `mounts`.

## Control Flow
`NewSnapshotter` creates the root, `metadata.db`, and `snapshots/`. `Prepare` and `View` call `createSnapshot`; active snapshots and parentless views get a temporary directory, active snapshots copy the first parent directory into it, metadata is created in a write transaction, and the temp dir is renamed to the snapshot ID. `Commit` computes disk usage and commits active metadata. `Remove` removes metadata, renames the directory to `rm-<id>`, then deletes it after the transaction.

## State And Persistence
Persistent state is `metadata.db` plus one directory under `snapshots/<id>` per snapshot. Active usage is scanned with `fs.DiskUsage`; committed usage is stored in metadata. Temporary `new-*` directories and `rm-*` directories represent in-flight creation/removal.

## Dependencies And Integration Points
Uses containerd mount and snapshot storage APIs, `continuity/fs` copy/disk usage helpers, platform-specific `mountType`/`defaultMountOptions`, and containerd logging.

## Risks And Edge Cases
Copying parents is expensive and copies only the first parent, matching snapshot chain semantics. Security xattrs are ignored during copy because they often cannot be copied. Failed rollback after directory rename can leave orphaned or inconsistent directories.

## Test Signals
`native_test.go` runs the containerd snapshotter suite as root on non-Windows systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native.go -->
