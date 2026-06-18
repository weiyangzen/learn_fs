<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h -->
# sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h

## Purpose
This header declares the page fragment cache API used to allocate small aligned fragments from cached pages, commonly for networking buffers.

## Important APIs, types, and functions
It defines `PAGE_FRAG_CACHE_ORDER_MASK` depending on maximum fragment cache size, `PAGE_FRAG_CACHE_PFMEMALLOC_BIT`, `encoded_page_decode_pfmemalloc()`, `page_frag_cache_init()`, `page_frag_cache_is_pfmemalloc()`, `page_frag_cache_drain()`, `__page_frag_cache_drain()`, `__page_frag_alloc_align()`, `page_frag_alloc_align()`, `page_frag_alloc()`, and `page_frag_free()`.

## Control flow
Callers initialize a cache, allocate fragments with size/GFP/alignment, and eventually drain/free. Alignment wrapper checks power-of-two alignment and passes an encoded mask. The encoded page value carries page order and pfmemalloc metadata.

## State and persistence
State persists in `struct page_frag_cache` (not defined here) through its `encoded_page` and offset/count fields in mm task types. Cached pages persist until drained or exhausted.

## Dependencies and integration points
It depends on bits/log2, mm task page-frag cache types, GFP allocation, page allocator, pfmemalloc semantics, and networking memory allocation paths.

## Risks and test signals
Risks include alignment mask misuse, pfmemalloc propagation errors, cache drain leaks, fragment size exceeding cache order, and high-order page assumptions when `PAGE_SIZE` differs from max cache size. Test network RX/TX allocations, pfmemalloc sockets, alignment-sensitive users, cache drain on teardown, high-order and base-page configs, and WARN on non-power-of-two alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h -->
