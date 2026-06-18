<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go

## Purpose

`fuse.go` implements the generic `Mount` wrapper around go-fuse server lifecycle. It tracks active state, detects external unmounts, and provides robust unmount fallback.

## Important APIs, Types, and Functions

`ErrNotMounted` signals inactive mounts. The private `mount` type stores mountpoint, `fuse.Server`, active flag, lock, and `sync.Once`. `NewMount` applies platform options, calls `fs.Mount`, starts a goroutine watching `server.Wait`, and returns a `Mount`. `Unmount`, `IsActive`, and `setActive` manage lifecycle state.

## Control Flow, State, and Integration

On normal unmount, `server.Unmount` clears active state. If unmount fails, it calls `ForceUnmountManyTimes`. If the mount is externally unmounted, the `server.Wait` goroutine marks it inactive so later `Unmount` returns `ErrNotMounted`. This wrapper is used by `/ipfs`, `/ipns`, and `/mfs`.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse, locks, and `fuse/mount` force-unmount helpers. Risks include double unmount races, external unmount state not propagating, and force unmount failures. `fuse/node/mount_test.go` validates external unmount detection for all three mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go -->
