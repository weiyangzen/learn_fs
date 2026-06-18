# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_test.go

## Purpose
This test file validates the cross-platform raw file-locking primitive exposed by the `internal/rawfilelock` package. It exercises `OpenLock`, `TryLockFile`, `LockFile`, and `UnlockAndCloseHandle` through realistic filesystem paths rather than mocking the platform-specific implementations.

## Important APIs and Behavior Covered
The central tests are `TestOpenLock`, `TestOpenLockNotCreateParentDir`, and `TestTryLockFileAndLockFile`. `TestOpenLock` verifies that `OpenLock` can open an existing lock file in read-write and read-only modes, and can create a new lock file when its parent directory already exists. `TestOpenLockNotCreateParentDir` defines an important boundary: `OpenLock` creates the lock file itself but does not create missing parent directories. `TestTryLockFileAndLockFile` covers both nonblocking and blocking lock acquisition on file handles returned by `OpenLock`.

## Control Flow and State
Each test creates temporary files or paths, calls `OpenLock`, then closes handles through `UnlockAndCloseHandle`. The tests intentionally reopen the same path after unlocking to prove that handle close releases the OS lock and that subsequent opens are usable. Cleanup is done with `os.RemoveAll` or temporary directory lifetime.

## Dependencies and Integration Points
The tests depend on `os`, `filepath`, Go's `testing`, and `testify/require`. They indirectly validate the platform files `rawfilelock_unix.go` and `rawfilelock_windows.go`, plus the shared wrapper in `rawfilelock.go`. Higher-level packages such as `internal/staging_lockfile` depend on this behavior for safe staging/tempdir cleanup.

## Risks and Edge Cases
The tests do not prove multi-process exclusion; that is covered at the `staging_lockfile` layer. They also do not exercise read-lock versus write-lock compatibility, lock reentrancy, or Windows panic behavior for blocking lock failures. The parent-directory test is important because callers must create parent directories before asking rawfilelock to create/open a file.

## Test Signals
Strong signals: open/reopen behavior, read-only mode, no implicit parent creation, and both lock entry points. Missing signals: contention, stale handles, EINTR/retry behavior on Unix, and Windows `LockFileEx` failure modes.
