# sources/distributed-fs/ceph-client/io_uring/alloc_cache.c

## Purpose
`alloc_cache.c` provides a small reusable object cache for io_uring subsystems that frequently allocate per-request auxiliary objects, notably futex wait data.

## Important APIs, Types, And Functions
- `io_alloc_cache_init()` allocates the pointer array, initializes counts and element sizing, and returns `false` on success.
- `io_alloc_cache_free()` drains cached entries through a caller-provided free function and frees the pointer array.
- `io_cache_alloc_new()` allocates a new element with `kmalloc()` and clears configured initial bytes.

## Control Flow
Initialization allocates an array of object pointers. Allocation paths in the header try cached entries first, then call `io_cache_alloc_new()`. Freeing drains all cached objects and clears `entries`.

## State And Persistence
State is stored in `struct io_alloc_cache`: `entries`, `nr_cached`, `max_cached`, `elem_size`, and `init_clear`. Cached objects persist until reused or the owning ring frees the cache.

## Dependencies And Integration Points
It depends on `kvmalloc_array`, `kvfree`, and the inline helpers in `alloc_cache.h`. `futex.c` uses it for `struct io_futex_data`.

## Risks And Edge Cases
The initializer’s false-on-success convention is easy to misuse. Cache sizing must match actual object size and any required zeroed prefix. Draining uses a supplied free function; passing the wrong function would corrupt memory ownership.

## Test Signals
Futex wait stress tests, KASAN, and allocation-failure injection can validate cache reuse, cleanup, and error handling.
