# sources/cloud-native/moby/daemon/snapshotter/mount.go

## Purpose
`mount.go` implements snapshotter rootfs mounting with optional reference counting and per-target locking.

## Important APIs, Types, And Functions
`Mounter` exposes `Mount`, `Unmount`, and `Mounted`. `NewMounter` returns a `refCountMounter` wrapping `mounter`. `refCountMounter` uses `mountref.Counter` and `locker.Locker`; `mounter` handles actual target path creation and `mount.All`.

## Control Flow
`refCountMounter.Mount` computes the target, increments a mount refcount, returns early if already referenced, locks target setup, and rolls back refcount/mount/dir on error. `Unmount` decrements refcount and only unmounts/removes the target when it reaches zero. `Mounted` checks kernel mount state and then verifies an active refcount. `mounter.Mount` creates parent and target dirs with root/idmapped ownership and mounts all containerd mounts.

## State And Persistence
Persistent state includes temporary rootfs mount directories under `<home>/rootfs/<snapshotter>/<containerID>`. In-memory state tracks reference counts and locks.

## Dependencies And Integration Points
Integrates containerd mount specs, Moby mountref, locker, mountinfo checks, user identity mapping, and platform-specific `isMounted`/`unmount`.

## Risks
Reference-count correctness is critical; mismatched increments/decrements can leak mounts or unmount a rootfs still in use. Error rollback unmounts/removes only when the refcount drops to zero. Directory ownership must respect user namespace mappings.

## Test Signals
No direct tests listed; snapshotter container lifecycle integration tests should cover mount reuse, cleanup, and failure rollback.
