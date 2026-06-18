# sources/cloud-native/containers-storage/drivers/driver_linux.go

## Purpose
`driver_linux.go` defines Linux filesystem magic constants, filesystem names, default driver priority, and mount checking helpers.

## Important APIs, Types, And Functions
It defines many `FsMagic*` constants, `Priority` (`overlay`, `aufs`, `btrfs`, `zfs`, `vfs`), `FsNames`, `GetFSMagic`, `NewFsChecker`, `fsChecker.IsMounted`, `NewDefaultChecker`, `defaultChecker.IsMounted`, `isMountPoint`, and `Mounted`.

## Control Flow
`GetFSMagic` performs `unix.Statfs` on the parent directory of the requested root path and logs unknown types. `Mounted` checks statfs type at the mount path and then confirms mountpoint status by comparing device IDs against the parent directory. The checker wrappers make this usable by `RefCounter`.

## State And Persistence
Static constants/maps define platform behavior. No mutable state is persisted.

## Dependencies And Integration Points
AUFS, Btrfs, overlay, and driver selection use these constants and helpers. It depends on `pkg/mount`, `x/sys/unix`, `filepath`, and logrus.

## Risks
`GetFSMagic` uses `filepath.Dir(rootpath)`, so callers must pass roots whose parent exists. `isMountPoint` returns true alongside stat errors, leaving the error for callers to interpret. Accurate mount detection is critical for refcounting and cleanup.

## Test Signals
Concrete driver initialization and mount tests indirectly validate these helpers.
