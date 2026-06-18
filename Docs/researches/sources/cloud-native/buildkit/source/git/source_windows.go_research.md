# sources/cloud-native/buildkit/source/git/source_windows.go

## Purpose
Provides a Windows-specific Git executor shim for the source backend.

## Important APIs, Types, And Functions
- `runWithStandardUmask(ctx, cmd)` starts the command, kills it on context cancellation, and waits.

## Control Flow
The function starts the Git process and spawns a goroutine that either kills the process when the context is done or returns when wait completes.

## State And Persistence
No persistent state and no umask manipulation; Windows does not use POSIX umask.

## Dependencies And Integration Points
Used by `gitCLI` in `source.go` on Windows builds. Depends only on `context` and `os/exec`.

## Risks And Edge Cases
Unlike Unix implementations, this kills only the direct process rather than a process group. Many Git source tests skip on Windows due to snapshotter bind-mount limitations, so Windows behavior has weaker direct coverage.

## Test Signals
Indirect coverage is limited; Windows-specific runtime is mostly guarded by compile-time build tags and broader package behavior where supported.
