<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go -->
# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go

## Purpose
`rawfilelock.go` exposes the low-level file lock wrapper used by higher-level storage locking packages.

## Important APIs, Types, And Functions
`LockType` has `ReadLock` and `WriteLock`. `FileHandle` aliases the platform-specific `fileHandle`. Public functions are `OpenLock`, `TryLockFile`, `LockFile`, `UnlockAndCloseHandle`, and `CloseHandle`.

## Control Flow
`OpenLock` opens or creates a lock file with read-only or read-write flags and wraps open errors as `os.PathError`. `TryLockFile` calls the platform lock function in non-blocking mode; `LockFile` blocks. Close helpers delegate to platform-specific unlock/close primitives.

## State And Persistence
The lock file path is created if needed. Actual lock state is kernel/OS file-lock state tied to the file handle lifecycle.

## Dependencies And Integration Points
Higher-level `internal/staging_lockfile` and `pkg/lockfile` should be preferred by most callers. Platform-specific files implement `openHandle`, `lockHandle`, `unlockAndCloseHandle`, and `closeHandle`.

## Risks And Edge Cases
The comments emphasize that closing a file handle can release locks, making this primitive unsafe for multiple goroutines sharing the same path. `CloseHandle` is explicitly for corrupted/error paths because Unix cannot close without unlocking.

## Test Signals
Tests for this package are outside the requested file list, but the API is small and high-risk because lock misuse can corrupt storage state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go -->
