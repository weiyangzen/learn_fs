# sources/cloud-native/buildkit/solver/resolvercache_test.go

## Purpose
This file is the focused test suite for `resolverCache` and `combinedResolverCache`. It documents the intended synchronization, value accumulation, rollback, and error propagation behavior of the resolver cache abstraction.

## Important Tests and Helpers
`TestResolverCache_SerialAccess` verifies that released non-nil values are returned to later lock holders. `TestResolverCache_ConcurrentWaiters` proves waiters block while a key is locked and receive the released value afterward. `TestResolverCache_MultipleIndependentKeys` checks isolation by key. `TestResolverCache_ReleaseNilDoesNotAdd` and `TestResolverCache_SequentialLocks` cover empty release and repeated accumulation. `mockResolverCache` implements `ResolverCache` for combined-cache tests.

The combined-cache tests validate parallel child locking, value merging, empty input behavior, rollback when one child fails, and release error propagation while still calling every child releaser.

## Control Flow
The tests use direct lock/release calls rather than a full solver job. Concurrency is exercised with `sync.WaitGroup`, result channels, and a short timeout asserting that waiter goroutines are actually blocked before release.

## State and Persistence
The tests assert in-memory state only: values persist across locks, key state is independent, and nil release avoids adding durable values. Combined-cache tests track release side effects in local slices and counters.

## Dependencies and Integration Points
The suite imports `testify/assert` and `testify/require`, plus `github.com/pkg/errors` for synthetic failure paths. It directly exercises unexported constructors because it lives in package `solver`.

## Risks Covered
The tests cover deadlocks for normal release, duplicated key values, missing rollback, and partial release failures. They do not cover a lock holder that never releases, because the production API has no context-aware wait cancellation.

## Test Signals
Strong local signal for resolver cache behavior. These tests are narrow and deterministic except for the 100 ms waiter-blocking timeout, which is short but acceptable for the intended synchronization assertion.
