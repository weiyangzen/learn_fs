# File Research: sources/block-storage/thin-provisioning-tools/src/utils/future.rs

## Purpose
Provides a tiny thread-backed future abstraction without async/await.

## Main Components
- `spawn_future<F, T>(work)` creates an `mpsc` channel, spawns a thread, runs `work`, sends the result, and returns a `FnOnce() -> T` closure that blocks on receive.

## Behavior
The returned closure is the join/retrieve handle. Calling it blocks until the worker sends the result. The worker thread itself is not joined explicitly; successful result delivery is the synchronization point.

Type bounds require both the work closure and its result to be `Send + 'static`.

## Failure Behavior
The function panics if:
- the worker panics before sending,
- sending fails,
- receiving fails.

## Research Notes
This is useful for simple parallel computations where the caller wants delayed blocking. It does not propagate panics as structured errors and does not expose cancellation.
