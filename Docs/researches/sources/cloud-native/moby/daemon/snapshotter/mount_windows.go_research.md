# sources/cloud-native/moby/daemon/snapshotter/mount_windows.go

## Purpose
`mount_windows.go` provides Windows implementations of snapshotter mount helpers.

## Important APIs, Types, And Functions
`isMounted` always returns false. `unmount` calls `mount.Unmount(target, 0)`.

## Control Flow
The common mounter compiles on Windows and delegates unmounts to containerd without Unix flags.

## State And Persistence
No in-memory state is stored. Unmount may affect snapshotter mount state through containerd.

## Dependencies And Integration Points
Depends on containerd's mount package.

## Risks
Always returning false means the refcount counter cannot recover existing mounted state the way Unix can.

## Test Signals
Windows snapshotter integration coverage is the relevant signal.
