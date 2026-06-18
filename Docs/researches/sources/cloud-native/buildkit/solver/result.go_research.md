# sources/cloud-native/buildkit/solver/result.go

## Purpose
This file implements shared and split wrappers for solver `Result`, `CachedResult`, and `ResultProxy` lifetimes. It lets multiple consumers clone references while ensuring the underlying result or proxy is released exactly once after all split references are released.

## Important APIs
`NewSharedResult` wraps a `Result`. `(*SharedResult).Clone` replaces the stored main reference with one half of `dup` and returns the other half. `NewCachedResult` attaches exportable cache keys to a result. `NewSharedCachedResult`, `CloneCachedResult`, and `clonedCachedResult.CacheKeys` preserve cache-key access across cloned cached results. `SplitResultProxy` does the same split-release logic for `ResultProxy`.

## Control Flow
`dup` creates two `splitResult` values sharing an atomic semaphore. Each split has its own atomic `released` guard. On release, the split detects double release, logs an error, and returns it; otherwise it increments the shared semaphore and only calls the underlying `Result.Release` when both halves have released. `SharedResult.Clone` repeats this pattern under a mutex, creating a chain of split results as more clones are requested.

## State and Persistence
State is in memory: a mutex protects the current main reference, and atomics protect per-split and shared release counts. No data is persisted, but release timing controls cache reference and snapshot lifetimes elsewhere in the solver.

## Dependencies and Integration Points
It depends on BuildKit logging, `pkg/errors`, and the solver result interfaces from `types.go`. Scheduler/cache code returns `SharedCachedResult` instances so multiple jobs or merged edges can consume the same cached result safely.

## Risks
Release correctness depends on every clone eventually being released. A missing release leaks the underlying result. A double release returns an error and logs, but cannot undo side effects from any previous release chain. Cache keys in `clonedCachedResult` are delegated to the original cached result, so callers must treat cache-key slices as immutable.

## Test Signals
`scheduler_test.go` includes `TestSlowCacheErrorResultCloneRelease`, which checks that a result returned inside `SlowCacheError` is not released with the job and releases exactly once when the error-held result is explicitly released.
