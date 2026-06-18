# sources/distributed-fs/ceph-client/lib/lru_cache.c

Purpose: DRBD-origin helper that tracks a bounded active set of labeled objects with LRU eviction and explicit transaction/commit support for persistent cache-set changes.

Important APIs/types/functions: `lc_create()`, `lc_destroy()`, `lc_reset()`, `lc_try_lock()`, `lc_find()`, `lc_is_used()`, `lc_get()`, `lc_get_cumulative()`, `lc_try_get()`, `lc_put()`, `lc_del()`, `lc_committed()`, `lc_element_by_index()`, and seq dump/stat helpers.

Control flow: creation preallocates all objects from a kmem cache, embeds `struct lc_element` at caller-specified offset, and populates the free list. Lookup uses a hash table keyed by current or pending number. `lc_get()` hits increment refcount and move to in-use; misses may mark the cache dirty, select a free/LRU element, move it to `to_be_changed`, and require the caller to persist/commit the change. `lc_committed()` promotes pending new numbers to active numbers. `lc_put()` moves unused elements to LRU.

State/persistence: maintains free, in-use, lru, and to-be-changed lists; hash slots; element array; usage/stat counters; pending change count; and flags such as locked, dirty, starving, and paranoia.

Dependencies/integration: callers must provide external locking/transaction serialization and a kmem cache. Seq helpers integrate with debug/proc style reporting.

Risks: PARANOIA macros BUG on concurrent misuse. Dirty/starving/locked protocol is subtle. Returned miss elements may not yet have `lc_number == requested`, so callers must inspect numbers and commit.

Test signals: no direct subset tests. Useful tests should cover hits, misses, pending-change limits, starving behavior, commit promotion, LRU eviction, cumulative lookup, and stats.
