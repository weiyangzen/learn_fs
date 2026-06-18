# sources/distributed-fs/lustre-release/lustre/osc/osc_page.c research

## Purpose
`osc_page.c` implements OSC `cl_page` operations, page-to-async-page initialization, transfer pinning, per-OSC LRU slot management, VM shrinker callbacks, unevictable-page handling, and unstable writeback accounting. It is the page lifetime and memory-pressure companion to `osc_cache.c`.

## Important APIs, Types, and Functions
Important exported functions include `osc_dio_pages_init()`, `osc_page_init()`, and `osc_lru_shrink()`. Non-exported but cross-file-used functions include `osc_page_cache_add()`, `osc_index2policy()`, `osc_page_submit()`, `osc_lru_add_batch()`, `lru_queue_work()`, `osc_lru_reserve()`, `osc_lru_unreserve()`, `osc_unevict_cache_shrink()`, `osc_inc_unstable_pages()`, `osc_dec_unstable_pages()`, and `osc_over_unstable_soft_limit()`, with prototypes in `osc_internal.h`.

The file operates on `struct osc_page`, especially `ops_oap`, `ops_lru`, `ops_transfer_pinned`, `ops_srvlock`, `ops_from/ops_to`, `ops_intree`, `ops_in_lru`, and `ops_vm_locked`. It also uses client cache fields such as normal/unevictable LRU lists, LRU counters, shrinker counts, unstable counters, and shared `cl_lru_left`.

## Control Flow
Page initialization sets the default byte range, initializes the LRU link, calls `osc_prep_async_page()`, stores whether the current IO is server-lock/lockless, and registers page operations. Transient direct-IO pages get only print/clip operations and no cache LRU slot. Cacheable pages reserve an LRU slot with `osc_lru_alloc()`, preload and insert into `osc_object::oo_tree`, increment `oo_npages`, and mark `ops_intree`.

Submission and cache-add pin pages so they cannot be freed while transfer is pending. `osc_page_cache_add()` pins, calls `osc_queue_async_io()`, and either unpins on failure or marks the page as recently used. `osc_page_submit()` stamps BRW command, offset/count, sync flags, sys-resource flag, pins non-transient pages, and moves them out of the idle LRU.

Deletion reverses all page state: unpins transfer, tears down async cache state, removes the LRU slot, and deletes the page from the object radix tree. LRU shrink flow scans client LRU lists, groups pages by CL object to initialize one `CIT_MISC` IO per object, tries to own pages, moves mlocked pages to the unevictable list, discards freeable pages in folio batches, and updates counters. VM shrinker entry points count and scan all OSC clients in `osc_shrink_list`.

## State and Persistence Behavior
LRU state is in memory and controls client cache pressure, not durable storage. `osc_lru_alloc()` consumes shared LRU slots, possibly reclaiming from this or other OSC clients and waiting on `osc_lru_waitq`. `osc_lru_unreserve()` returns slots and wakes waiters. Unstable-page accounting marks pages as writeback/unstable after BRW dispatch and decrements when the request commits, using zone or node page-state counters depending on kernel feature macros. `osc_over_unstable_soft_limit()` piggybacks soft-sync pressure when global unstable pages and this OSC's unstable count exceed thresholds.

## Dependencies and Integration Points
The file depends on CL page/object ownership APIs, Linux radix tree, folio/page flags and refcounts, kernel shrinker APIs, node/zone writeback counters, client cache structures, and cache queueing in `osc_cache.c`. It integrates with `osc_object.c` through the page radix tree initialized there, with `osc_io.c` through LRU reservation and server-lock flags, with request completion through unstable-page callbacks, and with global shrinker registration state declared in `osc_internal.h`.

## Risks
Risks include page reference leaks from transfer pinning, LRU counter drift between busy/in-list/left/unevictable counters, reclaim deadlocks if page ownership is attempted under the wrong locks, radix tree duplicate or delete failures, incorrect handling of mlocked pages, and unstable-page accounting imbalance when requests are already committed. The shrinker has explicit logic to avoid infinite VM shrink loops when count and scan race with cache invalidation.

## Test Signals
Tests should cover cacheable and transient page initialization, radix tree duplicate handling, transfer pin/unpin on success and failure, page deletion while pending or in RPC, LRU reserve/reclaim under exhaustion, readahead failure to reserve slots, mlocked page migration to and from unevictable LRU, shrinker count/scan with empty and populated clients, unstable-page inc/dec including already-committed requests, and soft-sync threshold behavior.
