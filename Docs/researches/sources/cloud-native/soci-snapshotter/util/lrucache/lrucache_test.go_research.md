# sources/cloud-native/soci-snapshotter/util/lrucache/lrucache_test.go

Purpose: this file tests the reference-count-aware LRU cache behavior.

Important tests: `TestAdd` confirms a first add stores the value and a duplicate add returns the original cached value with `added=false`. `TestGet` verifies retrieving an existing value succeeds. `TestRemove` checks explicit removal does not trigger eviction while borrowed references remain, then triggers after all `done` callbacks are called. `TestEviction` fills a size-two cache, overflows it, confirms callbacks are delayed until references are released, and verifies duplicate calls to the same `done` are ignored.

Control flow and state: tests capture evicted keys in a slice via `OnEvicted`. They intentionally hold references returned by `Add` and `Get` to validate delayed finalization.

Dependencies and integration points: tests the local wrapper over groupcache LRU without external resources.

Risks and gaps: no tests cover cache capacity zero, callback reentrancy/deadlock, concurrent access, changing `OnEvicted` after insertion, or `Remove` of missing keys. Tests do not call all returned `done` functions for overflow-added entries, which is acceptable for the targeted assertions but leaves some reference-count paths unobserved.

Test signal quality: strong for the package's central delayed-eviction contract; missing for concurrency and callback behavior.
