# sources/cloud-native/containers-storage/pkg/lockfile/lockfile.go

Purpose: implements process-local and inter-process lock-file coordination with read/write locks and last-writer tracking.

Important APIs, types, and functions: `Locker` interface, `LockFile`, `GetLockFile`, `GetROLockFile`, deprecated `GetLockfile`/`GetROLockfile`, `Lock`, `RLock`, `TryLock`, `TryRLock`, `Unlock`, `AssertLocked`, `AssertLockedForWriting`, `ModifiedSince`, `Modified`, `Touch`, `IsReadWrite`, `openLock`, `createLockFileForPath`, `lock`, and `tryLock`.

Control flow: lock objects are cached by absolute path and read-only mode. Acquisition first takes an in-process `sync.RWMutex`; on the first nested lock it opens the lock file and calls `rawfilelock.LockFile` or `TryLockFile`. Nested locks increment `counter` and reuse the fd. Unlock decrements, releases the raw file lock and closes the handle when the counter reaches zero, then releases the in-process RW lock. Last-write checks require the caller to hold the lock.

State and persistence: persistent state is the lock file contents storing the last-write token. In-memory state includes cached `LockFile` objects, lock counters, current fd, lock type, and compatibility `lw` for deprecated `Modified`.

Dependencies and integration points: depends on `fmt`, `os`, `filepath`, `sync`, `time`, and `github.com/containers/storage/internal/rawfilelock`. OS-specific files implement last-write read/write and timestamp checks.

Risks and edge cases: many misuse cases intentionally panic: write-locking a read-only lock, unlocking an unlocked lock, checking or recording without the right lock. Cached lock mode mismatches return errors. If raw lock acquisition panics in `lock`, callers must recover at a higher level. `AssertLocked` cannot identify ownership by goroutine.

Test signals: `lockfile_test.go` covers in-process, try-lock, multiprocess read/write/mixed locking, last-write detection, and read-only panic behavior.
