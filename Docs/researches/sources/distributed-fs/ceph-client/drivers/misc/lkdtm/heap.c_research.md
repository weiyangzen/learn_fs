# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/heap.c

## Purpose
`heap.c` contains LKDTM heap and page allocator hardening tests. It provokes slab/vmalloc overflows, use-after-free reads and writes, init-on-alloc/free checks, buddy-page poisoning checks, double free, cross-cache free, and non-slab slab free handling.

## Important APIs, Types, and Functions
Important functions are `lkdtm_VMALLOC_LINEAR_OVERFLOW()`, `lkdtm_SLAB_LINEAR_OVERFLOW()`, `lkdtm_WRITE_AFTER_FREE()`, `lkdtm_READ_AFTER_FREE()`, `lkdtm_KFENCE_READ_AFTER_FREE()`, buddy allocator tests, init-on-alloc tests, `lkdtm_SLAB_FREE_DOUBLE()`, `lkdtm_SLAB_FREE_CROSS()`, `lkdtm_SLAB_FREE_PAGE()`, `lkdtm_heap_init()`, and `lkdtm_heap_exit()`. It owns three `struct kmem_cache *` globals used for free-integrity tests.

## Control Flow
The overflow tests allocate kernel memory and intentionally write just past valid bounds. Use-after-free tests allocate, initialize, free, and access memory again, then attempt to observe allocator poisoning. KFENCE loops until a KFENCE-backed allocation appears or a timeout expires. Init tests fill memory, free it, reallocate, and scan for stale bytes. Free-integrity tests allocate from dedicated caches and then free invalidly.

## State and Persistence
State is limited to `double_free_cache`, `a_cache`, and `b_cache`, created during LKDTM init and destroyed at module exit. Test allocations are transient.

## Dependencies and Integration Points
Uses slab, vmalloc, buddy allocator APIs, scheduler timing, KFENCE helpers, init-on-alloc/free boot parameters, and LKDTM configuration reporting. It exports `heap_crashtypes` for `core.c`.

## Risks
Many tests corrupt memory if hardening does not catch them. Some checks are probabilistic or allocator-layout dependent, such as getting the same object back after free or obtaining a KFENCE allocation before timeout.

## Test Signals
Expected signals are KASAN/KFENCE/SLUB/vmalloc guard faults, poisoning differences on read-after-free, stale-byte absence under init-on-alloc/free, detected double/cross/non-slab frees, and explanatory `FAIL` lines when the configured hardening is missing or ineffective.
