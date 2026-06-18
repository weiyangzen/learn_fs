# sources/distributed-fs/ceph-client/include/linux/mm_types_task.h

## Purpose
`mm_types_task.h` contains MM data types embedded in `struct task_struct` without forcing scheduler headers to include the much larger `mm_types.h`. It provides lightweight counters, page-fragment caches, batched TLB flush tracking, and lazy MMU state used by task and network/MM paths.

## Important APIs, Types, And Functions
The file defines resident set counter indexes (`MM_FILEPAGES`, `MM_ANONPAGES`, `MM_SWAPENTS`, `MM_SHMEMPAGES`, `NR_MM_COUNTERS`), `struct page_frag`, `struct page_frag_cache`, `struct tlbflush_unmap_batch`, and `struct lazy_mmu_state`. `ALLOC_SPLIT_PTLOCKS` determines whether page-table locks are allocated separately based on spinlock size. `PAGE_FRAG_CACHE_MAX_SIZE` and `PAGE_FRAG_CACHE_MAX_ORDER` size page-fragment cache allocation.

## Control Flow And State
There are no functions, but the structs define runtime state. `page_frag_cache` packs an encoded page pointer, pfmemalloc bit, order, current offset, and biased page count to reduce `_refcount` cacheline traffic during repeated fragment allocations. `tlbflush_unmap_batch` holds optional architecture batch state plus flags indicating whether a flush is required and whether a dirty writable PTE was unmapped. `lazy_mmu_state` tracks nesting of lazy MMU enable and pause sections.

## Dependencies And Integration Points
Dependencies include alignment/type headers, `asm/page.h`, and optionally `asm/tlbbatch.h`. Integration points include `task_struct`, RSS accounting in `mm_struct`, network page-fragment allocation, page-table locking policy, TLB unmap batching, and architecture-specific TLB flush code.

## Risks And Test Signals
Risks include counter order mismatch with `kernel/fork.c`, page-fragment integer width overflow on small systems, stale dirty writable TLB entries before I/O, and architecture batch semantics that fail the promised barrier/flush ordering. Test signals are RSS counter initialization checks, network fragment stress, high-order page fragment allocation tests, batched unmap/TLB shootdown tests, and architecture builds with and without `CONFIG_ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH`.
