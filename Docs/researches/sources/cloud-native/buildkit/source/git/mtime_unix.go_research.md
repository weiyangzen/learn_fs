# sources/cloud-native/buildkit/source/git/mtime_unix.go

## Purpose
This Unix-only file implements symlink-aware mtime setting for git source checkout paths. It exists so git source code can adjust file timestamps without following symlinks.

## Important APIs
`lchtimes(path, t)` converts a Go `time.Time` to a Unix timespec and calls `unix.UtimesNanoAt` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`.

## Control Flow
The function is a direct syscall wrapper. Both access and modification times are set to the same timestamp.

## State and Persistence
It mutates filesystem metadata on the target path. It does not store state in memory or elsewhere.

## Dependencies and Integration Points
It is built only when `!windows` applies. It depends on `golang.org/x/sys/unix` and is used by git checkout code to apply deterministic checkout or commit mtimes.

## Risks
Errors are returned directly from the syscall. Platform-specific filesystem behavior can vary, especially on filesystems with coarse timestamp resolution or limited symlink timestamp support.

## Test Signals
No direct tests in this subset. Coverage is indirect through git source checkout tests that assert mtime behavior on Unix-like systems.
