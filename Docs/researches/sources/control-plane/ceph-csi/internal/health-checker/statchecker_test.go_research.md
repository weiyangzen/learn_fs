# sources/control-plane/ceph-csi/internal/health-checker/statchecker_test.go

## Purpose
`statchecker_test.go` validates the basic lifecycle of the stat-based health checker.

## Important APIs, Types, And Functions
`TestStatChecker` constructs a checker with `newStatChecker`, type asserts it to `*statChecker`, shortens the interval, starts it, checks `isRunning`, repeatedly calls `isHealthy()`, and stops it.

## Control Flow And Test Behavior
The test uses a temporary directory, sleeps for goroutine startup, and polls health for ten seconds while the checker ticks every five seconds.

## Dependencies And Integration Points
The test depends on the package-private concrete type to tune timing and on host filesystem behavior for `os.Stat`.

## Risks And Edge Cases
The test reads `isRunning` without synchronization and has wall-clock sleeps. It mainly verifies that the happy path does not fail; it does not assert a stat call actually happened before early health reads.

## Test Signals
The test confirms normal stat checking against a live directory. Missing coverage includes missing path after startup, permission errors, stalled `os.Stat`, duplicate starts, and stop blocking.
