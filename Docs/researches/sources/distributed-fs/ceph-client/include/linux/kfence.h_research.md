# sources/distributed-fs/ceph-client/include/linux/kfence.h

## Purpose

`kfence.h` is the public allocator and fault-handler integration surface for Kernel Electric-Fence. It lets slab allocators occasionally return guarded heap objects, identify KFENCE pool addresses, size and free KFENCE objects, and handle faults raised by guard pages. The source was read as a complete 254-line file.

## Important APIs, Types, and Functions

Important definitions include `KFENCE_POOL_SIZE`, `__kfence_pool`, `kfence_allocation_key`, `kfence_allocation_gate`, and `kfence_sample_interval`. Public hooks include `is_kfence_address()`, `kfence_alloc_pool_and_metadata()`, `kfence_init()`, `kfence_shutdown_cache()`, `kfence_alloc()`, `kfence_ksize()`, `kfence_object_start()`, `kfence_free()`, `kfence_handle_page_fault()`, and `__kfence_obj_info()` under printk.

## Control Flow

Boot code allocates pool/metadata and initializes the sampling gate. Allocator fast paths call `kfence_alloc()`, which checks a static branch and allocation gate before falling into `__kfence_alloc()`. Free paths call `kfence_free()` on arbitrary heap addresses; KFENCE handles only pool addresses. Page faults inside the pool are routed to `kfence_handle_page_fault()` to report memory errors and make the page accessible enough for controlled continuation.

## State and Persistence Behavior

KFENCE owns a fixed pool and metadata for sampled objects. Objects persist as live, freed, or zombie allocation records until the pool slot is reused. The header itself stores only declarations and inline gate checks.

## Dependencies and Integration Points

It integrates with SLAB/SLUB allocation/free paths, memblock boot allocation, static keys, atomics, page fault handling, printk object inspection, and cache destruction.

## Risks and Edge Cases

`is_kfence_address()` is fast-path critical and must keep the range check safe when `__kfence_pool` is NULL. Allocators must never return KFENCE objects to normal freelists. `kfence_shutdown_cache()` handles the difficult case of live sampled objects during cache teardown.

## Test Signals

KFENCE selftests, sampled allocation/free paths, use-after-free and out-of-bounds fault tests, `CONFIG_KFENCE=n` build coverage, cache destroy diagnostics, and fast-path performance checks are useful.
