<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go

## Purpose
This FreeBSD companion supplies platform-specific ZFS root checks, mountpoint naming, and unmount behavior.

## Important APIs, Types, And Functions
`checkRootdirFs` verifies `unix.Statfs_t.Fstypename` starts with `zfs`. `getMountpoint` returns the ID unchanged. `detachUnmount` uses `unix.MNT_FORCE`.

## Control Flow
The filesystem check stats the rootdir and returns `graphdriver.ErrPrerequisites` when it is not ZFS.

## State And Persistence
No state is persisted here; functions inspect filesystem type and unmount existing ZFS mountpoints.

## Dependencies And Integration Points
`zfs.go` calls these helpers during initialization and mount cleanup.

## Risks And Test Signals
The Fstypename byte comparison is platform-specific and intentionally low-level. FreeBSD test coverage must validate the expected statfs layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go -->
