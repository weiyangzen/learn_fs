<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go

## Purpose
Provides an LRU cache whose eviction callback is delayed until all external references release the value.

## Important APIs, Types, And Functions
- `LRUCache` wraps `groupcache/lru.Cache` and exposes `OnEvicted`.
- `NewLRUCache(maxEntries)` installs internal eviction behavior.
- `Get` increments a refcount and returns a one-shot `done` callback.
- `Add` returns an existing value without replacement or adds a new refcounted value.
- `Remove` evicts from LRU while respecting outstanding references.
- `refCounter` handles initialize/finalize/inc/dec semantics.

## Control Flow
Each cached value has one cache-owned reference plus caller references. LRU eviction/finalize drops the cache reference; caller `done` drops caller refs. `OnEvicted` fires only when the refcount reaches zero.

## State And Persistence
State is in-memory LRU entries, refcounts, and callbacks. No persistence.

## Dependencies And Integration Points
Used by store ref pooling to avoid removing manifest/config directories while still referenced. Depends on `github.com/golang/groupcache/lru`.

## Risks And Edge Cases
Callers must invoke `done` exactly once; leaked callbacks delay cleanup. Refcount can go negative if implementation bugs bypass the once wrapper. Callback runs while locks are held, so slow callbacks can block cache operations.

## Test Signals
Tests validate duplicate add behavior, get behavior, remove-delayed eviction, and eviction after LRU overflow once references are released.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/lrucache.go -->
