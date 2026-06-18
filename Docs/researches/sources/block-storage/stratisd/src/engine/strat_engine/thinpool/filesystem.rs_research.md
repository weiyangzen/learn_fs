# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/filesystem.rs

## Purpose
Implements `StratFilesystem`, the runtime representation of a Stratis filesystem backed by a device-mapper thin device and formatted as XFS.

## Main Components
- `StratFilesystem` stores:
  - `thin_dev: ThinDev`
  - creation timestamp,
  - cached used bytes,
  - optional size limit,
  - optional origin filesystem UUID,
  - merge-scheduled flag.
- `initialize()` creates a new thin device, formats it with XFS, assigns a Stratis filesystem UUID, and cleans up the thin device on format failure.
- `setup()` reconstructs an existing filesystem from `FilesystemSave`.
- `snapshot()` creates a thin snapshot and repairs duplicate XFS UUID issues.
- `visit_values()` decides whether a mounted filesystem should be visited and grown.
- `handle_fs_changes()` extends the thin device and runs `xfs_growfs`, rolling back the DM table if growfs fails.
- `record()` converts runtime state to `FilesystemSave`.
- `Filesystem` trait implementation exposes engine-facing filesystem properties.
- `StratFilesystemState` supports diffing size and used space.

## Filesystem Creation and Setup
`initialize()` validates that an optional size limit is not below the requested size, creates a new filesystem UUID, formats the thin device with `create_fs()`, and returns both UUID and runtime filesystem object. If formatting fails, it retries thin-device destruction and logs if cleanup leaves a dangling DM device.

`setup()` rebuilds the DM thin device using saved size and thin ID, converts the saved creation timestamp, and restores size limit, origin, and merge state.

## Snapshot Behavior
`snapshot()` creates a thin snapshot. If the origin is mounted, it temporarily mounts the snapshot with `nouuid` to force XFS log replay, unmounts it, then calls `set_uuid()` so the snapshot has a unique filesystem UUID. Snapshots inherit the origin size limit and record the origin UUID.

## Growth and Usage
`visit_values()` checks thin-device status and current mount points. Mounted filesystems are considered for growth when used bytes exceed half of total bytes. Growth size is computed by `extend_size()`, bounded by pool no-overprovision remaining size and filesystem size limit when applicable.

`handle_fs_changes()` updates the thin-device table length before running `xfs_growfs()`. If XFS growth fails and restoring the old table also fails, it returns a rollback error at `ActionAvailability::NoPoolChanges`.

`fs_usage()` reads statvfs data and returns total and used bytes.

## Metadata and API Surface
`record()` stores name, UUID, thin ID, size, creation timestamp, size limit, origin, and merge flag. `set_size_limit()` rejects limits smaller than current thin-device size and returns whether state changed. `set_merge_scheduled()` requires an origin when scheduling a merge.

`Into<Value>` produces a JSON object with size, used, size limit, and origin strings for reporting.

## Research Notes
This file bridges thin provisioning, XFS behavior, procfs mount discovery, udev naming, and engine-level filesystem state. Snapshot UUID handling and grow rollback are the most important correctness paths.
