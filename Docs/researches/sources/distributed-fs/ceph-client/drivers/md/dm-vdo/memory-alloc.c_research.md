# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.c

## Purpose
`memory-alloc.c` centralizes VDO/UDS memory allocation. It chooses `kmalloc` or `vmalloc`, zeroes allocations, tracks current and peak memory usage, avoids recursive filesystem/block I/O from restricted threads via `memalloc_noio_save()`, and reports leaks at module exit.

## Important APIs, Types, and Functions
Public functions are `vdo_allocate_memory()`, `vdo_allocate_memory_nowait()`, `vdo_free()`, `vdo_reallocate_memory()`, `vdo_duplicate_string()`, `vdo_memory_init()`, `vdo_memory_exit()`, `vdo_register_allocating_thread()`, `vdo_unregister_allocating_thread()`, `vdo_get_memory_stats()`, and `vdo_report_memory_usage()`. Internal state includes `allocating_threads`, `struct vmalloc_block_info`, and cacheline-aligned `memory_stats`.

## Control Flow
Initialization sets up the spinlock and thread registry. Regular allocation validates the output pointer, returns NULL for size zero, enters NOIO context when the current thread is not registered as allocation-safe, tries `kmalloc` for page-sized-and-smaller unaligned allocations, otherwise allocates a small tracking record and retries `__vmalloc()` for up to roughly one second before logging failure. Successful allocations update stats. Free detects vmalloc addresses and removes matching tracking records before `vfree()`, or updates kmalloc stats before `kfree()`. Reallocation allocates new zeroed memory, copies the smaller of old/new sizes, and frees the old block.

## State and Persistence Behavior
Memory stats are runtime-only and protected by a spinlock. Vmalloc allocations are tracked in a linked list keyed by pointer. `vdo_memory_exit()` assertion-logs nonzero tracked bytes to catch leaks. Thread allocation permissions live in a runtime thread registry.

## Dependencies and Integration Points
The file uses Linux slab/vmalloc/mm/noio APIs, delay helpers, spinlocks, VDO logging, assertions, and thread registry helpers. Nearly all VDO modules allocate through macros in `memory-alloc.h`, making this a global accounting and failure behavior point.

## Risks and Edge Cases
The vmalloc tracking record itself is allocated through `vdo_allocate()`, creating nested accounting that must be freed carefully. `remove_vmalloc_block()` logs if a pointer is not found. Alignment is considered only in the kmalloc/vmalloc choice; callers requiring cache alignment use the header wrapper. Incorrect thread registration can cause allocation from I/O paths without NOIO protection or noisy false warnings.

## Test Signals
Tests should cover kmalloc and vmalloc paths, zero-size allocation, allocation failure, nowait allocation, reallocation growth/shrink/free, duplicate string, stats current/peak values, leak detection at exit, NOIO behavior for unregistered threads, and freeing unknown or stale pointers through fault injection.
