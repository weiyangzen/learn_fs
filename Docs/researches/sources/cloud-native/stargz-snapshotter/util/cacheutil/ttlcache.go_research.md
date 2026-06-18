<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go

## Purpose
Implements a TTL cache with reference-counted values so entries expire only after their timer fires and all active users release them.

## Important APIs, Types, And Functions
- `TTLCache` stores refcounted entries and a TTL duration.
- `NewTTLCache(ttl)` constructs the map.
- `Get` returns value plus `done(evict bool)` and increments references.
- `Add` inserts or returns existing value and starts/resets timer semantics.
- `Remove` forces eviction when references drain.
- `evictLocked` and `decreaseOnceFunc` coordinate timer and caller releases.
- `refCounterWithTimer` holds value, key, count, timer, and evicted flag.

## Control Flow
Adding creates a timer that marks the entry evicted after TTL. Active callers hold references through `done`; eviction removes the map entry and final cleanup waits for refs to reach zero. A caller can request eviction through the boolean done argument.

## State And Persistence
All state is in-memory maps, timers, and refcounts. No persistence.

## Dependencies And Integration Points
A general utility for short-lived reference-sensitive caches. It uses `time.Timer` and synchronization primitives.

## Risks And Edge Cases
Timer/refcount interactions are subtle; callers must call done once. Very short TTLs can expire while values are in use, making future gets miss even though cleanup waits. Boolean `done` semantics require careful caller discipline.

## Test Signals
Tests cover add/get/remove, overwritten removal, TTL expiration, and quick done behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache.go -->
