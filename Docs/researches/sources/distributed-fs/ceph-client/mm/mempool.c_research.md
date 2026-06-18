<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempool.c -->
# sources/distributed-fs/ceph-client/mm/mempool.c

## Purpose

`mempool.c` implements Linux generic memory pools: preallocated emergency reserves used by subsystems that must make bounded, deadlock-resistant allocations under memory pressure. It provides lifecycle, resize, single and bulk allocation, refill/free logic, debug poisoning, KASAN support, fault-injection hooks, and common slab/kmalloc/page backends. The complete 766-line file was read.

## Important APIs, Types, and Functions

Public APIs include `mempool_init_node()`, `mempool_init_noprof()`, `mempool_create_node_noprof()`, `mempool_exit()`, `mempool_destroy()`, `mempool_resize()`, `mempool_alloc_bulk_noprof()`, `mempool_alloc_noprof()`, `mempool_alloc_preallocated()`, `mempool_free_bulk()`, `mempool_free()`, `mempool_alloc_slab()`, `mempool_free_slab()`, `mempool_kmalloc()`, `mempool_kfree()`, `mempool_alloc_pages()`, and `mempool_free_pages()`. Important internal helpers include `add_element()`, `remove_element()`, `mempool_alloc_from_pool()`, `mempool_adjust_gfp()`, `poison_element()`, `check_element()`, and KASAN poison/unpoison helpers. Fault attributes `fail_mempool_alloc` and `fail_mempool_alloc_bulk` are created at late init.

## Control Flow

Initialization sets the spinlock, minimum reserve, callback pointers, waitqueue, and element array, then preallocates `max(1, min_nr)` elements. Allocation first adjusts GFP flags to avoid global emergency reserves and page allocator retries, then tries the caller-supplied allocator with a non-reclaiming first pass. If allocation fails or fault injection forces reserve use, `mempool_alloc_from_pool()` removes an element under the pool lock. Sleepable callers wait on the pool waitqueue with periodic timeouts when the reserve is empty; non-sleeping callers can return `NULL`.

Bulk allocation repeats the same pattern across an array, using normal allocation first and dipping into reserves for missing slots. Freeing uses a barrier-paired fast check of `curr_nr`; if the pool is below `min_nr`, it returns elements to the reserve under lock and wakes waiters. If the pool is already full, `mempool_free()` calls the backend free function. Resize can shrink by freeing extra reserve elements or grow by reallocating the element pointer array and filling new reserve slots opportunistically.

## State and Persistence Behavior

The durable pool state is `struct mempool`: `min_nr`, `curr_nr`, backend callbacks, `pool_data`, reserve `elements[]`, spinlock, and waitqueue. Reserved elements stay poisoned and KASAN-poisoned while in the pool and are unpoisoned when removed. Zero-minimum pools still allocate storage for one reserve slot and have explicit free-side wake/refill handling to avoid sleeping waiters being stranded.

## Dependencies and Integration Points

The file depends on slab and page allocators, KASAN mempool hooks, SLUB debug poisoning constants, kmemleak trace updates, waitqueues, `io_schedule_timeout()`, fault-injection debugfs, writeback-related scheduling context, and exported mempool APIs used by block, filesystem, networking, and storage paths that cannot tolerate allocation recursion deadlocks.

## Risks and Edge Cases

Callers must not use `__GFP_ZERO` with `mempool_alloc()`, must size bulk requests no larger than `min_nr`, and must ensure `mempool_destroy()` does not race with `mempool_resize()`. Backend callbacks may sleep, so context rules depend on both GFP flags and callback behavior. Barrier pairing between allocation and free protects rare lockless handoff cases; weakening it can lose reserve refills or wakeups. Debug poisoning is skipped under KASAN because KASAN may store metadata in freed objects. Zero-minimum pools have special behavior and should not be assumed to guarantee progress beyond one returned preallocated slot.

## Test Signals

Useful tests include fault-injection forcing reserve use, bulk allocation with partially prefilled arrays, allocation under `GFP_NOWAIT` and `GFP_KERNEL`, wait/wakeup behavior with empty pools, resize grow/shrink while allocations occur, zero-minimum pool allocation/free cycles, KASAN and SLUB poisoning mismatch detection, slab/kmalloc/page backend coverage, and kmemleak trace update checks for reserve-sourced elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempool.c -->
