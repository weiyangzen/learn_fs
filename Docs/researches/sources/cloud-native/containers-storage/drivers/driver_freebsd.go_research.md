# sources/cloud-native/containers-storage/drivers/driver_freebsd.go

## Purpose
`driver_freebsd.go` provides FreeBSD graphdriver priority and mount/filesystem checking helpers.

## Important APIs, Types, And Functions
It defines `FsMagicZfs`, `Priority` as `zfs` then `vfs`, `FsNames`, `NewDefaultChecker`, `defaultChecker.IsMounted`, and `Mounted`.

## Control Flow
FreeBSD selection prefers ZFS. `Mounted` calls `unix.Statfs` on a path and compares the reported filesystem type with the requested `FsMagic`.

## State And Persistence
No persistent or mutable package state beyond static maps/slices.

## Dependencies And Integration Points
It integrates with `RefCounter` through `Checker`, with mount parsing through `pkg/mount`, and with platform graphdriver selection.

## Risks
Unlike Linux, `Mounted` does not separately verify mountpoint boundary by parent device; it only compares filesystem type. This can be less precise for nested paths.

## Test Signals
FreeBSD-specific build and driver tests would exercise it; none are included in this subset.
