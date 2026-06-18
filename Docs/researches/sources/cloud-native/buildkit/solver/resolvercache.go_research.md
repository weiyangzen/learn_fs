# sources/cloud-native/buildkit/solver/resolvercache.go

## Purpose
This file implements the per-job `ResolverCache` contract. It serializes remote resolution work by key, lets later callers observe values published by earlier releases, and can combine several resolver caches into one parallel fan-out cache.

## Important APIs
`newResolverCache()` constructs the mutex-protected map. `(*resolverCache).Lock(key)` either acquires the key immediately or waits for the current holder to release it. The returned `release(value)` optionally appends a non-nil value to the key's accumulated values. `combinedResolverCache` returns a `combinedCache`, whose `Lock` calls all child caches concurrently and merges values and releasers.

## Control Flow
For a local cache, `Lock` creates or finds an `entry`. If it is unlocked, it marks it locked and returns a clone of current values plus a release closure. If locked, it appends a wait channel, blocks until release closes it, then rechecks the map and takes the lock if still present. Release appends the value, wakes all waiters, clears waiting channels, unlocks the entry, and deletes the key if there are still no values.

For a combined cache, each child `Lock` runs in its own goroutine. Values and releasers are collected under a mutex. If any child fails, all already-acquired releasers are called with nil for rollback.

## State and Persistence
All state is process memory. Values persist for a key until the cache object is discarded; nil releases do not add values and can delete an empty entry.

## Dependencies and Integration Points
It depends on `sync` and `slices`. The interface is exposed through `JobContext.ResolverCache()` and used by source resolvers to deduplicate registry or remote resolution decisions inside a solve.

## Risks
`Lock` waits without a context, so a caller that never invokes release can block all waiters indefinitely. Combined cache releases are sequential; a slow child release delays the combined release. Only the first release error is reported.

## Test Signals
`resolvercache_test.go` covers serial accumulation, concurrent waiters, independent keys, nil release deletion, sequential locks, combined value merge, empty combined caches, rollback on child error, and release error propagation.
