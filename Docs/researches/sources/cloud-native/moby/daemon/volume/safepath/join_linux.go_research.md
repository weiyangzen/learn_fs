# sources/cloud-native/moby/daemon/volume/safepath/join_linux.go

## Purpose
Linux implementation of secure subpath joining that returns a temporary bind mount pinned to the validated target.

## Important APIs, Types, And Functions
`Join(ctx, path, subpath)` is the public API. Helpers include `safeOpenFd`, `tempMountPoint`, and `cleanupSafePath`.

## Control Flow
`Join` resolves base/subpath, locks the OS thread, opens the resolved subpath with `safeOpenFd`, creates a temp file or directory mountpoint based on fd type, bind mounts `/proc/self/fd/<fd>` to that temp path, and returns a `SafePath` with cleanup. `safeOpenFd` opens the base with `O_PATH|O_DIRECTORY|O_NOFOLLOW`, tries `openat2` with `RESOLVE_BENEATH|NO_MAGICLINKS|NO_SYMLINKS`, falls back to Kubernetes safe-open on `ENOSYS`, maps `EXDEV` to escape and `ENOENT/ELOOP` to inaccessible. Cleanup unmounts with `MNT_DETACH` and removes the temp path.

## State And Persistence
Creates temporary filesystem entries and kernel bind mounts; `SafePath.Close` must remove them. No daemon metadata is persisted.

## Dependencies And Integration Points
Used by `MountPoint.Setup` for volume/image subpaths. Depends on unix syscalls, `/proc/self/fd`, no-EINTR wrappers, and Kubernetes-derived fallback logic.

## Risks
Requires mount permissions and Linux kernel support. Cleanup leaks can leave temp mounts. Correct fd lifetime and thread locking are important to avoid racing mount source resolution.

## Test Signals
Join tests cover escaping symlinks, safe symlinks inside base, symlink replacement after join, and close invalidation.
