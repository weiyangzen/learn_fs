# sources/control-plane/ceph-csi/internal/health-checker/filechecker_test.go

## Purpose
`filechecker_test.go` validates the basic lifecycle and timestamp helpers for the file-backed health checker.

## Important APIs, Types, And Functions
`TestFileChecker` constructs a checker through `newFileChecker`, type asserts it to `*fileChecker`, shortens the interval, starts it, probes `isRunning`, repeatedly checks `isHealthy()`, and stops it. `TestWriteReadTimestamp` writes and reads a timestamp in a temporary directory.

## Control Flow And Test Behavior
Both tests run in parallel and use `t.TempDir()` to isolate filesystem state. The lifecycle test sleeps one second after start and then polls health ten times at one second intervals, while the checker interval is five seconds.

## Dependencies And Integration Points
The tests use the concrete `fileChecker` type rather than only the `ConditionChecker` interface so they can tune the interval and inspect `isRunning`.

## Risks And Edge Cases
The lifecycle test is timing-sensitive and assumes the goroutine starts within one second. It observes `isRunning` without synchronization. Because initial health is true and the first check happens later, the test can pass before much real I/O has occurred.

## Test Signals
The file confirms normal temporary-directory operation and JSON timestamp round trip. Missing coverage includes failed writes, failed reads, corrupt timestamp files, stale update timeout, duplicate starts, and blocking stop behavior.
