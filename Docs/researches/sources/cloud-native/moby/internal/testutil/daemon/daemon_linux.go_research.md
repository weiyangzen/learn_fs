# sources/cloud-native/moby/internal/testutil/daemon/daemon_linux.go

## Purpose
Linux-specific daemon helpers for cleaning network namespace mounts and reading the daemon's cgroup namespace.

## Important APIs, Types, And Functions
- `cleanupNetworkNamespace` walks `<execRoot>/netns`, lazily unmounts entries, logs non-benign errors, and removes paths.
- `(*Daemon).CgroupNamespace` reads `/proc/<pid>/ns/cgroup` and trims the link target.

## Control Flow
Cleanup traverses the daemon-specific netns directory with `filepath.WalkDir`, attempts `unix.Unmount(MNT_DETACH)`, ignores `EINVAL` and `ENOENT`, and removes each path. Namespace reading uses the daemon process PID.

## State And Persistence
Cleanup mutates the daemon exec root by unmounting/removing network namespace files. `CgroupNamespace` is read-only.

## Dependencies And Integration Points
Requires Linux `/proc`, `golang.org/x/sys/unix`, and daemon process state. Complements `Daemon.Cleanup`.

## Risks And Edge Cases
Walk errors are ignored by the callback signature, so missing directories are benign. Unmount failures are logged but do not fail tests. `CgroupNamespace` requires a running daemon with a valid PID.

## Test Signals
Expected behavior is no leaked netns mounts after cleanup and a nonempty cgroup namespace link for running daemons.
