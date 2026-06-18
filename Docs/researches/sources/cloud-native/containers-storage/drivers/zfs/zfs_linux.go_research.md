<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go

## Purpose
This Linux companion supplies root filesystem validation and detach unmount behavior for the ZFS driver.

## Important APIs, Types, And Functions
`checkRootdirFs` uses `graphdriver.GetFSMagic` and requires `FsMagicZfs`. `getMountpoint` returns the ID unchanged. `detachUnmount` calls `unix.Unmount(..., unix.MNT_DETACH)`.

## Control Flow
If filesystem magic is not ZFS, the helper logs backing filesystem information and returns an error wrapping `graphdriver.ErrPrerequisites`.

## State And Persistence
No persistent state is modified; unmount affects kernel mount state.

## Dependencies And Integration Points
`zfs.Init`, `zfs.Get`, and `zfs.Put` depend on these helpers for platform behavior.

## Risks And Test Signals
The root directory must already reside on ZFS unless `zfs.fsname` is supplied. Tests require Linux with ZFS available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go -->
