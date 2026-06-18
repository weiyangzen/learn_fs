# sources/control-plane/ceph-csi/internal/health-checker/checker.go

## Purpose
`checker.go` defines the shared runtime state and lifecycle helpers for health checkers. It does not perform a check itself; concrete checkers embed `checker`, call `initDefaults()`, and provide `runChecker`.

## Important APIs, Types, And Functions
`command` is the private control-channel command type, with `stopCommand` as the only command. `checker` stores interval, timeout, a read/write mutex, `isRunning`, health result, last error, last update time, command channel, and the concrete `runChecker` callback. `initDefaults()`, `start()`, `stop()`, and `isHealthy()` are the common implementation used by `fileChecker` and `statChecker`.

## Control Flow And State
`initDefaults()` sets a 60 second interval, 15 second timeout, healthy initial status, current `lastUpdate`, and a default panic callback. `start()` only launches a goroutine if `isRunning` is false. `stop()` sends a `STOP` command synchronously to the checker goroutine. `isHealthy()` marks a checker unhealthy when no successful update has happened within `interval + timeout`, then returns a consistent `healthy, err` pair under a read lock.

## Dependencies And Integration Points
This file depends only on `fmt`, `sync`, and `time`. It is consumed through the `ConditionChecker` interface in `manager.go`, with concrete behavior supplied by `filechecker.go` and `statchecker.go`.

## Risks And Edge Cases
`isRunning` is read and written without mutex protection, so concurrent `start()`, `stop()`, and tests can race under the Go race detector. `stop()` can block forever if called before the goroutine is ready to receive or after the checker loop has exited. `start()` sets `isRunning` inside the goroutine, so rapid duplicate starts may launch more than one checker.

## Test Signals
Coverage comes indirectly from file/stat checker and manager tests. The tests exercise lifecycle and health reads, but they do not check timeout-induced unhealthy state, duplicate starts, race behavior, or `stop()` blocking paths.
