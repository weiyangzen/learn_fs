# Research: sources/distributed-fs/ceph-client/mm/page_frag_cache.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_frag_cache.c` implements the page fragment cache allocator. It provides a small framework for carving arbitrary-sized aligned fragments out of an order-0 or higher-order page while using the underlying page refcount to track outstanding fragments. The primary consumers are the network stack and network drivers, where fragments back `sk_buff` heads or skb fragment data.

## Important APIs, Types, and Functions

The central caller-owned type is `struct page_frag_cache`, declared in `linux/page_frag_cache.h`. This file maintains its `encoded_page`, `offset`, and `pagecnt_bias` fields. Public functions are `page_frag_cache_drain()`, `__page_frag_cache_drain()`, `__page_frag_alloc_align()`, and `page_frag_free()`.

Internal helpers are `encoded_page_create()`, `encoded_page_decode_order()`, `encoded_page_decode_virt()`, and `encoded_page_decode_page()`. `encoded_page_create()` packs the page virtual address, allocation order, and pfmemalloc bit into one unsigned long. The companion `encoded_page_decode_pfmemalloc()` is provided by the header.

## Control Flow

Allocation enters `__page_frag_alloc_align()`. If the cache has no encoded page, `__page_frag_cache_refill()` first tries to allocate `PAGE_FRAG_CACHE_MAX_ORDER` when page size is smaller than the maximum fragment-cache size, using flags that avoid direct reclaim and warn/retry behavior. If that fails, it falls back to an order-0 page. The encoded page records order and pfmemalloc state.

After refill, the allocator adds a large reference-count bias to the page instead of incrementing the refcount for every fragment. `nc->pagecnt_bias` starts at `PAGE_FRAG_CACHE_MAX_SIZE + 1`, `nc->offset` starts at zero, and each fragment allocation decrements the bias while advancing an aligned offset. If the requested fragment would exceed the page size, the code either returns NULL for requests larger than one base page when the cache is only order-0, or subtracts the remaining bias from the page. If the page refcount reaches zero and the cached page is not pfmemalloc, the same page is recycled by resetting its page count and offset; otherwise it is freed and the cache refills.

Draining uses `page_frag_cache_drain()` for a full cache and `__page_frag_cache_drain()` for a caller-supplied page/count pair. The drain subtracts the unused bias from the page refcount and frees the underlying allocation with `free_frozen_pages()` if the count reaches zero. Individual fragments are released with `page_frag_free()`, which finds the head page for the virtual address and frees the compound allocation when the last reference drops.

## State and Persistence Behavior

All state is transient and caller-owned. A `struct page_frag_cache` keeps one current page, a byte offset into that page, and a bias representing references pre-acquired by the cache but not yet handed out as fragments. Fragment lifetime is represented in the page's refcount. There is no persistence outside RAM.

Pfmemalloc state is preserved in the encoded page. When a pfmemalloc cached page is exhausted, it is returned to the page allocator instead of being recycled, preventing emergency-reserve pages from silently backing normal network buffers beyond their intended use.

## Dependencies and Integration Points

Dependencies include page allocation/free APIs from `mm/internal.h`, GFP flag definitions, NUMA memory node selection through `numa_mem_id()`, page refcount helpers, compound page order, virtual-to-page translation, and exported symbols for network and driver modules. Integration is primarily with skb allocation paths and drivers that cache page fragments for RX/TX buffers.

## Risks and Edge Cases

The encoded pointer relies on page alignment and bit masks. `BUILD_BUG_ON()` checks ensure the order and pfmemalloc bits fit below `PAGE_SIZE`; changing constants without preserving those invariants would corrupt decoded addresses. Refcount biasing is also delicate: failing to drain the cache leaks references and pages, while subtracting the wrong count can prematurely free a page still referenced by fragments.

Low-memory behavior intentionally falls back to order-0 pages. Large fragment requests can then fail even though the cache exists, and the code avoids freeing that cache page immediately to avoid worsening pressure. Callers must handle NULL returns. Pfmemalloc fragments require downstream networking code to respect emergency memory restrictions.

## Test Signals

Useful tests include network stack fragment allocation/free stress, fragment sizes around alignment and page-size boundaries, high-order refill failure forcing order-0 fallback, large-fragment NULL behavior, cache drain after partial use, last-fragment free of compound and order-0 pages, pfmemalloc page handling under memory pressure, KASAN/page-ref debug checks for use-after-free or refcount leaks, and module build coverage for exported APIs.
