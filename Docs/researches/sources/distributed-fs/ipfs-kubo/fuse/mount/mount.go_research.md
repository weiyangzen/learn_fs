<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go

## Purpose

This file defines the generic mount abstraction and platform-specific force-unmount command selection used by FUSE lifecycle code.

## Important APIs, Types, and Functions

`Mount` exposes `MountPoint`, `Unmount`, and `IsActive`. `ForceUnmount` tries `umount` first, then a GOOS-specific fallback from `UnmountCmd`. `UnmountCmd` selects `diskutil umount force` on Darwin, `fusermount3 -u` or `fusermount -u` on Linux, and errors elsewhere. `ForceUnmountManyTimes` retries with delay. `Closer` wraps a mount as `io.Closer`.

## Control Flow, State, and Integration

Force unmount runs the command in a goroutine and times out after seven seconds. Multi-retry unmount is used by `fuse.go` after `server.Unmount` fails. The code does not persist state; it invokes host tools.

## Dependencies, Risks, and Test Signals

Dependencies are `os/exec`, `runtime`, and system unmount helpers. Risks include missing helper binaries, unsupported FreeBSD fallback despite build support elsewhere, command hangs, and error string differences. Node external-unmount tests call `UnmountCmd` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go -->
