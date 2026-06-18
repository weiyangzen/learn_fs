<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go

## Purpose
Tests the delayed-eviction semantics of `LRUCache`.

## Important APIs, Types, And Functions
- `TestLRUAdd` verifies duplicate `Add` returns the original cached value.
- `TestLRUGet` verifies retrieval and value identity.
- `TestLRURemove` verifies `OnEvicted` waits for all `done` callbacks.
- `TestLRUEviction` verifies LRU overflow does not finalize until references are released.

## Control Flow
Tests create small caches, attach an `OnEvicted` recorder, add/get/remove entries, call returned done functions, and assert eviction ordering/counts.

## State And Persistence
State is in-memory cache entries and a test slice of evicted keys.

## Dependencies And Integration Points
Directly covers `lrucache.go`, which is used by store reference metadata caching.

## Risks And Edge Cases
Tests focus on single-threaded behavior and do not stress concurrent callers or slow callbacks.

## Test Signals
Passing demonstrates that cached values are stable, duplicate additions do not replace data, and eviction callbacks are reference-count gated.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache_test.go -->
