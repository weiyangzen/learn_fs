# sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile_test.go

## Purpose
This test file validates `StagingLockFile` semantics above raw OS locks, including in-process duplicate prevention, file deletion on unlock, concurrency, and real multi-process contention through `reexec`.

## Important APIs and Helpers
`TestMain` initializes reexec. `subTryLockPath` starts a child process registered by `init`, and `subTryLockPathMain` attempts `TryLockPath` on the supplied path, unlocking and deleting on success. The main tests cover `CreateAndLock`, `TryLockPath`, `UnlockAndDelete`, and path reuse.

## Control Flow and State
The tests create temp directories and lock paths, then assert the package-global `stagingLockFiles` map is empty after unlock. `TestCreateAndLockAndTryLock` verifies the same process cannot acquire a second lock for an already-owned path, then can reacquire after release. `TestTryLockPathMultiProcess` holds a lock in the parent process, launches child attempts that must fail, releases the parent lock, and verifies a child can then acquire and clean up.

## Dependencies and Integration Points
The file imports `reexec` to create controlled subprocesses. It uses `testify` assertions and the filesystem to validate deletion. It indirectly tests the rawfilelock platform implementation because subprocess contention depends on kernel-level locking, not just the in-memory map.

## Risks and Edge Cases
The concurrency test creates independent temp dirs in each goroutine, so it stresses map cleanup rather than contention for one path. The subprocess error capture names the stdout reader as `stderrBuf`, but it still checks the child message. Tests do not simulate `os.Remove` failures during `UnlockAndDelete`.

## Test Signals
High-value signals include double-unlock panic, path recreation, and parent/child contention. These are important because `tempdir.RecoverStaleDirs` assumes `TryLockPath` failure means another owner is active.
