# sources/cloud-native/moby/daemon/internal/unix_noeintr/fs_unix.go

## Purpose
Provides non-Darwin, non-Windows filesystem syscall wrappers that retry operations interrupted by signals.

## Important APIs, Types, And Functions
`Retry` runs a function until it returns something other than `unix.EINTR`. Wrappers include `Mount`, `Unmount`, `Open`, `Close`, `Openat`, `Openat2`, `Fstat`, and `Fstatat`, each capturing syscall results and returning them after retry.

## Control Flow
Each wrapper uses a closure passed to `Retry`, assigning return values on every attempt. The final non-EINTR error or nil is returned to the caller.

## State And Persistence
Operations can mutate mount state, open/close file descriptors, or read file metadata. The wrappers themselves keep no state.

## Dependencies And Integration Points
Used wherever daemon code wants uniform no-EINTR Unix syscall behavior. Excludes Darwin and Windows via build tags.

## Risks And Test Signals
`Close` retrying on EINTR can be subtle on Unix because fd state after interrupted close is platform-dependent; this package intentionally centralizes that policy. No tests are included in this subset.
