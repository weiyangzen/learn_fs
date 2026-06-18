# sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile.go

## Purpose
`staging_lockfile.go` provides a higher-level, process-aware locking abstraction for temporary staging resources. It wraps raw OS file locks with an in-process registry so a single process cannot accidentally create two `StagingLockFile` owners for the same path.

## Important APIs and Types
`StagingLockFile` stores the absolute lock-file path and a `rawfilelock.FileHandle`. `CreateAndLock(dir, pattern)` creates a unique temp file, closes it, then locks it and returns the lock object plus the basename. `TryLockPath(path)` attempts to lock a specific path, creating the file if needed. `UnlockAndDelete()` removes the lock file, unlocks/closes the handle, deletes the registry entry, and invalidates the object by clearing `file`.

## Control Flow
`tryAcquireLockForFile` canonicalizes the path with `filepath.Abs`, takes the package mutex, initializes `stagingLockFiles`, rejects duplicate ownership in the same process, opens the file with `rawfilelock.OpenLock`, and attempts a nonblocking write lock. On lock failure, it closes the raw handle before returning an error. `CreateAndLock` loops up to `maxRetries` if locking a just-created temp file fails, which handles rare name/lock races or external interference.

## State and Persistence
There are two layers of state: the filesystem lock file and the process-global `stagingLockFiles` map protected by `stagingLockFileLock`. The lock file persists until `UnlockAndDelete`, and the map entry exists only while the current process owns the lock. `UnlockAndDelete` deliberately panics on double-unlock because that violates the ownership contract.

## Dependencies and Integration Points
The file depends on `internal/rawfilelock`, `os`, `filepath`, and `sync`. It is the locking foundation for `internal/tempdir`, whose `NewTempDir` creates lock/tempdir pairs and whose stale recovery calls `TryLockPath` to distinguish active from abandoned directories.

## Risks and Edge Cases
If `CreateAndLock` fails after creating a temp file but before locking it, the current implementation retries without removing the failed candidate; later stale cleanup may remove such artifacts. `UnlockAndDelete` holds the package mutex while removing the file, which keeps registry state correct but can serialize slow filesystem operations. Callers must not construct `StagingLockFile` manually and must not use it after unlock.

## Test Signals
The paired tests verify creation, explicit path locking, duplicate lock rejection, panic on double unlock, recreation after deletion, goroutine concurrency, and subprocess contention. Those tests strongly anchor both the in-process registry and OS lock behavior.
