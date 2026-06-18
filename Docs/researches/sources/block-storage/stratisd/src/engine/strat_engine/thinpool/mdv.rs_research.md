# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mdv.rs

## Purpose
Manages the metadata volume, a linear device formatted as XFS and mounted privately to store per-filesystem JSON metadata records.

## Main Components
- `MetadataVol` owns:
  - `dev: LinearDev`
  - `mount_pt: PathBuf`
- `initialize()` formats the linear device and calls setup.
- `setup()` mounts the metadata volume and ensures the `filesystems` directory exists.
- `save_fs()` atomically writes or updates a filesystem JSON record.
- `rm_fs()` removes a filesystem JSON record durably.
- `filesystems()` loads all saved filesystem records.
- `teardown()` unmounts, removes the mount point, and removes the DM device.
- `Drop` attempts to unmount if explicit teardown was not called.
- `remove_temp_files()` removes stale temporary files from interrupted saves.

## Mount and Directory Behavior
The mount point is under `NS_TMPFS_LOCATION` and named with the pool UUID. `setup()` creates the mount directory, mounts XFS, treats `EBUSY` as already mounted, creates the `filesystems` subdirectory, and removes stale `.temp` files.

## Persistence Behavior
`save_fs()` serializes `FilesystemSave` to JSON, writes it to a `.temp` file, calls `sync_all()` on the temp file, renames it to `<uuid>.json`, then fsyncs the containing directory. This avoids truncated metadata files after interrupted writes and makes the rename durable.

`rm_fs()` removes `<uuid>.json`; missing files are treated as idempotent success. When a file is actually removed, it fsyncs the directory so the unlink is durable.

`filesystems()` iterates metadata records, ignores `.temp` entries, reads each file completely, and deserializes JSON.

## Teardown and Drop
`teardown()` checks whether the mount point is actually a mount by comparing `stat()` device IDs with the parent directory. If mounted, it retries unmount. It then attempts to remove the mount directory and removes the associated DM device by name.

`Drop` uses similar mount detection and retry unmount logic, warning instead of returning errors.

## Limits
`max_fs_limit()` estimates the maximum number of filesystem records by dividing metadata-volume total sectors by `XFS_MIN_FILE_ALLOC_SIZE`, set to 8 sectors or 4 KiB.

## Research Notes
This file is the durability core for per-filesystem metadata. The write-temp/rename/fsync pattern is deliberate crash-safety behavior and should be preserved.
