# sources/cloud-native/containers-storage/drivers/chroot_windows.go

## Purpose
`chroot_windows.go` provides the Windows implementation of `chrootOrChdir`, where true chroot is unavailable.

## Important APIs, Types, And Functions
`chrootOrChdir(path string) error` calls `syscall.Chdir(path)` and wraps errors with context.

## Control Flow
Windows reexec helpers can only change the working directory, not the process root.

## State And Persistence
It changes only process-local current working directory.

## Dependencies And Integration Points
It satisfies the shared chown helper API for Windows builds.

## Risks
Because it cannot isolate paths with chroot semantics, callers must avoid treating this as a security boundary. In practice Windows chown support is also stubbed.

## Test Signals
Build coverage only in this subset.
