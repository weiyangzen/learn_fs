# sources/cloud-native/moby/daemon/snapshotter/mount_unix.go

## Purpose
`mount_unix.go` provides non-Windows mount-state and unmount helpers for snapshotter rootfs mounts.

## Important APIs, Types, And Functions
`isMounted` calls `mountinfo.Mounted`. `unmount` calls containerd `mount.Unmount(target, unix.MNT_DETACH)`.

## Control Flow
The refcounted mounter uses `isMounted` when constructing the counter and `unmount` during cleanup. Detached unmount lets cleanup proceed even when references are being released asynchronously.

## State And Persistence
The functions read mount table state and unmount mount points. No in-memory state is stored.

## Dependencies And Integration Points
Depends on Moby mountinfo, containerd mount package, and `golang.org/x/sys/unix`.

## Risks
`MNT_DETACH` can hide busy mount cleanup issues. `isMounted` ignores mountinfo errors and returns false, which can affect refcount recovery.

## Test Signals
Covered indirectly by snapshotter mount lifecycle tests on Unix platforms.
