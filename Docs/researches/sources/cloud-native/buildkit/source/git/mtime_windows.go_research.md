# sources/cloud-native/buildkit/source/git/mtime_windows.go

## Purpose
This Windows-only file provides a no-op implementation of `lchtimes` for git source checkout timestamp handling.

## Important APIs
`lchtimes(_ string, _ time.Time) error` always returns nil.

## Control Flow
There is no branching or syscall. The function intentionally ignores its arguments.

## State and Persistence
It does not modify filesystem state. On Windows builds, callers that invoke `lchtimes` get successful no-op behavior.

## Dependencies and Integration Points
It is built only on Windows and imports `time` to match the shared signature. It satisfies the platform-specific function used by git checkout code.

## Risks
Because it is a no-op, Windows checkouts will not get the symlink timestamp behavior provided on Unix. This is likely intentional because Windows symlink timestamp semantics differ and may not be needed by current callers.

## Test Signals
No direct tests in this subset. Windows-specific git checkout mtime behavior would need platform CI coverage.
