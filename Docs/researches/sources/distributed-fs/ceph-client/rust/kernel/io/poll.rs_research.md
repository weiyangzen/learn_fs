# sources/distributed-fs/ceph-client/rust/kernel/io/poll.rs

## Purpose
`io/poll.rs` provides Rust equivalents of common kernel read-poll-timeout helpers for waiting on hardware state in sleepable and atomic contexts.

## Important APIs, Types, and Functions
`read_poll_timeout` repeatedly runs a fallible operation until a condition succeeds or a monotonic timeout expires, sleeping with `fsleep`. `read_poll_timeout_atomic` repeats a fixed number of attempts, delaying with `udelay` and never sleeping.

## Control Flow
The sleepable function records `Instant::now`, calls `might_sleep`, then loops: run `op`, return on `cond`, return `ETIMEDOUT` if elapsed time exceeds timeout, optionally `fsleep`, and `cpu_relax`. The atomic variant loops `retry` times with the same op/condition check, optional busy delay, and CPU relax, then returns `ETIMEDOUT`.

## State and Persistence
No persistent state exists. The only state is loop-local timing, retry count, and the last operation result.

## Dependencies and Integration Points
It depends on `Delta`, `Instant<Monotonic>`, `fsleep`, `udelay`, `cpu_relax`, `might_sleep`, and `ETIMEDOUT`. Drivers use it with `Io::try_read*` closures for hardware readiness polling.

## Risks
The sleepable version unconditionally calls `might_sleep`, so it must not be used in atomic context. Timeout is checked after an operation, so a slow `op` can exceed timeout before the error is returned. The atomic version uses retry count rather than wall-clock timeout.

## Test Signals
Tests should cover immediate success, success after several attempts, operation error propagation, timeout behavior, zero sleep/delay values, retry count zero, and context checking for sleepable use.
