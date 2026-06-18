# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_test.go

Purpose: integration-heavy tests for lock-file concurrency, reexec child processes, and last-write detection.

Important APIs, types, and functions: `TestMain`, `subTouchMain`, `subLockMain`, `subRLockMain`, `subTouch`, `subLock`, `subRLock`, `getTempLockfile`, and tests for try locks, read/write locks, multiprocess locking, `Touch`, `RecordWrite`, `Modified`, and `ModifiedSince`.

Control flow: helper subprocesses are registered through `reexec`; children acquire a lock, close stdout to signal acquisition, wait for stdin closure, then unlock or touch. Tests coordinate with pipes to verify blocking and cross-process behavior. Concurrent tests use counters to detect simultaneous writers or writer/reader overlap.

State and persistence: tests create real temporary lock files and observe persisted last-write token changes and file mtimes. In-memory counters track critical-section overlap.

Dependencies and integration points: depends on `io`, `os`, `os/exec`, `runtime`, `sync`, `sync/atomic`, `testing`, `time`, `reexec`, `logrus`, and `testify`. It validates the `lockfile` package against actual platform file locking.

Risks and edge cases: tests can be slow due to sleeps and many subprocesses/goroutines. Some tests depend on platform lock semantics and timer granularity. Comments note coverage is not exhaustive.

Test signals: strong signals for exclusive writers, shared readers, mixed read/write exclusion, try-lock failure, read-only write panic, timestamp touching, and external modification detection.
