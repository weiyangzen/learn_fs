# sources/cloud-native/containers-storage/drivers/driver_solaris.go

## Purpose
`driver_solaris.go` supplies Solaris+cgo graphdriver priority and ZFS mount detection.

## Important APIs, Types, And Functions
It defines `FsMagicZfs`, `Priority` as `zfs`, `FsNames`, `GetFSMagic`, `NewFsChecker`, `NewDefaultChecker`, `Mounted`, and checker structs. The cgo helper calls `statvfs`.

## Control Flow
`Mounted` calls `statvfs` on the mount path's directory and inspects `f_basetype` bytes for `"zfs"`. Non-ZFS results return `ErrPrerequisites`; ZFS returns mounted success.

## State And Persistence
Only static priority/name data exists.

## Dependencies And Integration Points
It supports graphdriver selection and refcount checking on Solaris. Dependencies include cgo, `pkg/mount`, `filepath`, `unsafe`, and logrus.

## Risks
`GetFSMagic` currently returns zero/nil, so filesystem detection is minimal. The cgo allocation helper ignores statvfs error detail and relies on `f_basetype` inspection.

## Test Signals
Solaris build/runtime tests would be needed; none are present in this subset.
