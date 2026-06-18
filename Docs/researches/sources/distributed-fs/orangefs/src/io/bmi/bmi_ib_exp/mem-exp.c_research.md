# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/mem-exp.c

## Purpose
Implements memory allocation, registration caching, deregistration, and cache flushing for the experimental InfiniBand BMI method. It reduces repeated HCA memory registration cost by keeping active and reusable memory-region entries around `memcache_entry_t` records.

## Important APIs, Types, And Functions
The private `memcache_device_t` holds active entries, a mutex, a free-chunk list, and provider callbacks for register/deregister. Internal helpers are `memcache_add`, `memcache_del`, `memcache_lookup_cover`, and `memcache_lookup_exact`. Public internal entry points are `memcache_memalloc`, `memcache_memfree`, `memcache_register`, `memcache_preregister`, `memcache_deregister`, `memcache_init`, `memcache_shutdown`, and `memcache_cache_flush`.

## Control Flow
`memcache_memalloc` first looks for an exact-size reusable free chunk for allocations larger than the eager limit. On a miss it calls `malloc`, then registers large buffers immediately through the provider callback. `memcache_memfree` keeps registered large allocations in `free_chunk_list` instead of freeing them, deregistering when their refcount drops to zero. `memcache_register` is used for user-provided send/receive buflists: each segment is matched against an existing covering registration or registered as a new region, and the resulting entries are stored in `buflist->memcache`. `memcache_deregister` decrements the stored entries after RDMA completion or cancellation and invokes provider deregistration when counts reach zero. `memcache_shutdown` frees active and cached free chunks, while `memcache_cache_flush` discards zero-refcount cached entries after provider registration pressure.

## State And Persistence
All state is runtime memory under `memcache_device_t`. Active and free lists keep `memcache_entry_t` objects with buffer address, length, refcount, and provider memory keys. Free-list entries may retain the actual malloced buffer for reuse, so memory persists beyond BMI `memfree` until shutdown or flush.

## Dependencies And Integration Points
The module depends on OrangeFS gen locks, quicklists via `ib-exp.h`, provider-specific memory registration callbacks supplied by `openib-exp.c` or `vapi-exp.c`, and generic allocation/error helpers. `ib-exp.c` calls it for BMI memory allocation, optimistic buffer registration, RTS/CTS/RDMA paths, cancellation cleanup, and final shutdown.

## Risks And Test Signals
The comments explicitly note the absence of a dreg-style consistency check for user buffers that may be freed or reused outside BMI. `memcache_preregister` returns immediately with "Can not do this any more", so `BMI_OPTIMISTIC_BUFFER_REG` is effectively disabled despite being accepted. `memcache_register` allocates `buflist->memcache` before all provider registrations are known to succeed, and failures log through non-fatal `error()`, leaving callers without a clear error return. Reusing free chunks can retain substantial pinned memory. Test signals include refcount accounting under overlapping buflists, registration failure/ENOMEM flush behavior, repeated memalloc/memfree reuse, cancellation deregistration for every RDMA state, and leak checks at shutdown.
