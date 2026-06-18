<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs.go

## Purpose
`zfs.go` implements the Linux/FreeBSD ZFS graphdriver using ZFS datasets, snapshots, clones, and legacy mounts.

## Important APIs, Types, And Functions
`zfsOptions` stores dataset name, mount path, and mount options. `Driver` holds the root dataset, options, a mutex-protected filesystem cache, and mount ref counter. Important functions include `Init`, `parseOptions`, `lookupZfsDataset`, `cloneFilesystem`, `Create`, `Get`, `Put`, `Remove`, `Status`, `Metadata`, `parseStorageOpt`, and `setQuota`.

## Control Flow
`Init` checks for the `zfs` command and `/dev/zfs`, parses options, derives the backing dataset from rootdir if not configured, enumerates child filesystems, creates the base directory, and returns a naive diff wrapper. Creating a base layer creates a ZFS filesystem with `mountpoint=legacy`, optionally sets quota, mounts it temporarily to adjust permissions/ownership/label behavior, and unmounts. Creating a child layer snapshots the parent dataset, clones the snapshot, marks the clone in cache, and destroys the snapshot with deferred deletion. `Get` mounts the dataset at `<base>/graph/<id>`, supports `ro` through remount, and ref-counts mounts. `Put` decrements, detach-unmounts, and removes the mountpoint. `Remove` destroys datasets recursively and updates the cache.

## State And Persistence
Persistent state is stored in ZFS datasets, snapshots/clones during creation, dataset quota properties, and mountpoint directories under `<base>/graph`. In-memory state is the dataset cache and ref counter. `ListLayers` is intentionally unsupported because arbitrary datasets can resemble layers.

## Dependencies And Integration Points
The driver uses `github.com/mistifyio/go-zfs/v3`, graphdriver naive diff/updater wrappers, mount helpers, idtools, SELinux labels, tempdir type compatibility, directory usage, and platform helpers in `zfs_linux.go`/`zfs_freebsd.go`.

## Risks And Edge Cases
The driver depends on external `zfs` tooling, `/dev/zfs`, correct dataset discovery, and legacy mount behavior. Snapshot names use `time.Now().Nanosecond()`, which may collide under rapid operations. Destroy retry logic handles aborted builds when datasets already exist. Read-only mounts first mount read-write to set state, then remount, which can surprise strict callers. Dedup and ListLayers are effectively unsupported.

## Test Signals
`zfs_test.go` runs graphtest lifecycle tests and quota tests, but requires a real ZFS environment and Linux build for the listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs.go -->
