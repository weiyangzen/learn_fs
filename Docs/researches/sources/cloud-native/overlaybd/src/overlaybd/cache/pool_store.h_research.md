<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h

## Purpose
Declares the generic cache pool/store interfaces used by OverlayBD cache filesystems for read-through refill, eviction, quotas, pinning, and transformed store keys.

## Important APIs, Types, And Functions
Defines `ListType`, reset/resize flags, `CacheFnTransFunc`, `CacheStat`, `ICachePool`, `ICacheStore`, `IMemCacheStore`, and `IMemCachePool`. `ICachePool` opens stores, manages quotas/stat/eviction/list/reset/resize, and tracks refill concurrency. `ICacheStore` exposes cached read/write/refill, query, eviction, source-file setup, size and allocator configuration.

## Control Flow
Cache filesystems open an `ICacheStore` through a pool; reads call `preadv2`, which checks cached ranges, opens source on miss, refills missing data, and returns user data. Writes go through `pwritev2` and may extend cache state depending on open flags.

## State And Persistence
Pool state includes open-store registry, optional thread pool/vCPU, refill counters, and filename transform callback. Store state includes source/store names, source file pointer, source filesystem, cached/actual sizes, page size, allocator, refcount, and range lock.

## Dependencies And Integration Points
Uses Photon filesystem/object/range-lock/iovec primitives and cache flags from `cache.h`. Implemented by `store.cpp` and concrete cache backends.

## Risks And Test Signals
Ownership is manual through `release` and source file setters. `O_CACHE_ONLY` and write-through/write-back flags change source-open behavior. Refill range correctness depends on concrete `queryRefillRange`, `do_preadv2`, and `do_pwritev2`. Tested indirectly in `cache_test.cpp`. Source size reviewed: 290 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h -->
