# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/page.c

## Purpose
Implements the page-level mechanics for io-cache: page lookup/creation/destruction, LRU pruning, wait queues, child read fault callbacks, read-result assembly, and page error handling.

## Important APIs, types, and functions
`__ioc_page_get()` looks up a rounded offset in the inode `rbthash` and refreshes page LRU position. `__ioc_page_create()` allocates and inserts a page. `__ioc_page_destroy()` removes and frees pages unless waiters force the page stale. `ioc_prune()` and `__ioc_inode_prune()` evict least-recent pages across priority buckets. `__ioc_wait_on_page()` queues a frame for a page range. `ioc_fault_cbk()` stores child `readv` data into the page and wakes waiters. `__ioc_frame_fill()` converts page data into per-frame `ioc_fill_t` fragments. `ioc_frame_unwind()` merges fragments into the final read reply.

## Control flow
`ioc_dispatch_requests()` from `io-cache.c` creates page waiters and starts faults. The child `readv` callback updates mtime validation state, copies vectors/iobrefs into the page, marks the page ready, fills each waiting frame, and lets `ioc_waitq_return()` decrement frame wait counts. A frame unwinds only after all page waiters have returned, so multi-page reads can complete in any fault order while still assembling the output by offset.

## State and persistence behavior
State is the in-memory page table, page LRU, wait queues, cached iovec/iobref references, ready/stale flags, and cache-used byte accounting. No durable data is stored; cached data is discarded on flush, prune, error, forget, or process shutdown.

## Dependencies and integration points
Depends on io-cache structures, Gluster iovec/iobref helpers, rbthash, child `readv`, memory accounting types, message IDs, and table/inode locks. It is tightly integrated with `io-cache.c` for dispatch/validation and `ioc-inode.c` for inode lifecycle.

## Risks and test signals
Risks include underflow/overflow in range math, copying zero or short pages incorrectly, stale-page destruction while waiters exist, `cache_used` divergence from actual iobref size, wait-count imbalance, lost errors when one page of a multi-page read fails, and memory leaks around `iov_subset()` or iobref merge failures. Tests should cover EOF short reads, sparse/zero-filled reads, simultaneous faults for the same page, page pruning during in-flight reads, child read errors, multi-page result ordering, and cache accounting after every destroy path.
