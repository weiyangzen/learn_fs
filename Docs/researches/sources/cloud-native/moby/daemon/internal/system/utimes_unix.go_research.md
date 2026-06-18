# sources/cloud-native/moby/daemon/internal/system/utimes_unix.go

## Purpose
Provides `LUtimesNano`, a symlink-preserving timestamp update helper for Linux and FreeBSD.

## Important APIs, Types, And Functions
`LUtimesNano(path string, ts []syscall.Timespec) error` converts two syscall timespecs to `unix.Timespec` and calls `unix.UtimesNanoAt` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`.

## Control Flow
The function updates access and modification times on the link itself. It returns syscall errors except `ENOSYS`, which is ignored for compatibility with systems lacking the syscall.

## State And Persistence
Mutates filesystem timestamps on the named path, specifically not following symlinks.

## Dependencies And Integration Points
Used by archive/extraction code that must preserve symlink metadata. Depends on `golang.org/x/sys/unix`.

## Risks And Test Signals
The function assumes `ts` has at least two elements and will panic otherwise. Ignoring `ENOSYS` means callers may believe timestamps were applied when the kernel could not support it. Tests verify symlink timestamp changes without target-file changes and error on missing paths.
