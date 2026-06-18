# sources/distributed-fs/ceph-client/io_uring/alloc_cache.h

## Purpose
The header defines inline fast paths for the io_uring allocation cache and the hard cap on cached entries.

## Important APIs, Types, And Functions
- `IO_ALLOC_CACHE_MAX` caps generic caches at 128 entries.
- `io_alloc_cache_put()` poisons and stores an object when capacity exists.
- `io_alloc_cache_get()` pops an object, unpoisons it for KASAN, and clears the configured prefix under KASAN.
- `io_cache_alloc()` and `io_cache_free()` are the high-level allocate/free helpers.

## Control Flow
`io_cache_alloc()` returns a cached object if available, otherwise allocates a new one. `io_cache_free()` tries to cache the object, falling back to `kvfree()`.

## State And Persistence
The object stack is LIFO through `entries[nr_cached]`. Cached objects remain owned by the cache until reused or drained.

## Dependencies And Integration Points
It depends on `struct io_alloc_cache` from `io_uring_types.h`, KASAN mempool hooks, and `alloc_cache.c` for slow paths. Subsystems using it must initialize and free caches at ring lifetime boundaries.

## Risks And Edge Cases
KASAN poisoning failure forces direct free. Inline cache operations are not internally locked, so callers must use them under their own serialization if shared. `init_clear` must be enough to prevent stale fields from leaking between requests.

## Test Signals
KASAN-enabled io_uring stress, futex wait cancellation, and ring teardown tests are relevant.
