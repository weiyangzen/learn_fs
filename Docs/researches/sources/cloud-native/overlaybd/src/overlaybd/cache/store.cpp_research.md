<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp

## Purpose
Implements shared `ICacheStore` read-through, write-through/cache-only, source-open, refill, and size-management logic.

## Important APIs, Types, And Functions
Implements destructor, `preadv2`, `pwritev2`, `try_refill_range`, `async_refill`, `do_refill_range`, `set_cached_size`, `try_preadv2`, mutable wrapper methods, `open_src_file`, `pwritev2_extend`, and `tryget_size`.

## Control Flow
`preadv2` validates range, clamps EOF, checks cache hit through `try_preadv2`, handles cache-only failure, opens source on miss, and refills the missing range. `do_refill_range` range-locks the refill span, reads source into an allocated buffer, copies overlapping bytes into the caller buffer, then writes cache synchronously or via pool async worker. `pwritev2` enforces page alignment and delegates to direct cache writes or append/extend mode.

## State And Persistence
Persists cached data through concrete `do_pwritev2`; reads source data through `src_file_`. Maintains `cached_size_`, `actual_size_`, source file pointer, refill lock, and async refill refcounts.

## Dependencies And Integration Points
Uses `pool_store.h`, Photon audit/logging, IO allocator, IOVector, range lock, and optional Photon thread pool on the owning `ICachePool`.

## Risks And Test Signals
Refill is sensitive to races, partial reads, ENOSPC, and async lifetime; range locks are released by async worker after write. If the pool's refill threshold is exceeded, reads bypass cache and go directly to source. Alignment requirements differ between normal and extending writes. `cache_test.cpp` covers EOF, refill, eviction, and pressure scenarios. Source size reviewed: 427 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp -->
