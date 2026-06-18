# sources/control-plane/csi-lib-utils/slowset/slowset_test.go

## Purpose

This test file verifies `SlowSet` insertion, expiration, and timing behavior.

## Important Behavior

`TestSlowSet` defines table-driven cases with retention/resync durations and closures that operate on a `SlowSet`. Each subtest creates a set, overrides `resyncPeriod`, starts `Run` in a goroutine, defers closing the stop channel, then executes the scenario. Cases verify that repeated `Add` does not change stored data, keys expire after retention, keys remain before retention, `TimeRemaining` is positive and below retention, and `Contains` returns false once a present key is expired.

## State, Dependencies, and Integration

Tests use real time sleeps from 100 to 301 ms and direct access to `s.workSet` because they are in the same package. There is no external dependency beyond Go testing/time.

## Risks and Test Signals

Real-time sleeps can be flaky on overloaded CI systems, especially boundary tests around 300/301 ms. The tests cover public methods and `Run` cleanup indirectly, but they do not stress concurrent access. Passing `go test ./slowset` is the signal.
