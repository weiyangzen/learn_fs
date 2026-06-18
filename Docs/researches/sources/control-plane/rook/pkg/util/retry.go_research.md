# sources/control-plane/rook/pkg/util/retry.go

## Purpose
`retry.go` provides generic retry loops with fixed delay or timeout semantics.

## Important APIs, Types, and Functions
`Retry(maxRetries, delay, f)` retries a function returning error until success or retry count is exceeded. `RetryFunc` returns `(done bool, err error)`. `RetryWithTimeout(f, period, timeout, description)` polls until done, timeout, or a terminal error with `done=true`.

## Control Flow, State, and Persistence
Both functions sleep using `time.After()`. `RetryWithTimeout()` starts a timeout channel once and intentionally calls `f()` one final time after timeout to avoid edge races. Errors during non-done polling are logged and retried.

## Dependencies and Integration Points
It depends on time, fmt, pkg/errors, and the package logger from `file.go`. It is used by reconciliation paths waiting for Kubernetes or Ceph state.

## Risks
There is no context cancellation. `Retry()` treats `maxRetries` as retries after the first attempt, so total attempts are `maxRetries + 1`. `RetryWithTimeout()` can run slightly longer than timeout and period and can block indefinitely if `f()` blocks.

## Test Signals
No direct mapped tests. Useful tests would cover attempt counts, terminal error behavior, timeout final retry, and zero/negative timing values.
