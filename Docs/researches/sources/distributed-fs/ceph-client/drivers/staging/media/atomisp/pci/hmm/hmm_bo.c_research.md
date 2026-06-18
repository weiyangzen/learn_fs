<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c` implements the HMM buffer-object allocator behind AtomISP ISP memory management. It manages ISP virtual address ranges, free/allocated rbtrees, whole-range list ordering, physical page backing, MMU mapping, vmap/mmap exposure, and kref lifetime.

## Important APIs, Types, and Functions

Important APIs are hmm_bo_device_init/exit(), hmm_bo_alloc/release(), search helpers, page allocation/free, MMU bind/unbind, vmap/vunmap/flush, kref helpers, and hmm_bo_mmap(). Internal helpers handle BO initialization, free-tree search, address lookup, split/merge, and removal from size-bucket chains.

## Control Flow

Device init creates the ISP MMU client, sets the virtual range, creates a BO slab cache, seeds one free BO covering the whole range, and inserts it into the free rbtree. Allocation searches the free rbtree by page count, splits larger blocks, inserts allocated blocks by start address, and later page allocation fills either private uncacheable pages or pages derived from a vmalloc buffer. Binding maps each page into the ISP MMU and flushes the TLB range. Release unmaps, frees pages/vmaps as needed, erases the allocated rbtree node, merges adjacent free list neighbors, and reinserts the merged block into the free tree.

## State and Persistence Behavior

Persistent runtime state lives in `struct hmm_bo_device`: MMU client, slab cache, free and allocated rbtrees, the ordered `entire_bo_list`, locks, range start/size, and init flag. Each BO stores start/end, page count, status bits, page array, type, vmap pointer, mmap count, kref, and neighbor links for equal-sized free blocks.

## Dependencies and Integration Points

It depends on Linux rbtrees, lists, mutex/spinlock/kref, page allocation, vmalloc-to-page, cacheability changes, vmap/vunmap, remap_pfn_range, and AtomISP ISP MMU map/unmap/flush hooks. `hmm.c` is its main consumer.

## Risks and Edge Cases

There are several allocator-sensitive edge cases: device init leaks/destroys inconsistently if BO allocation fails after cache creation; `__bo_search_and_remove_from_free_rbtree()` assumes a non-empty root; mmaped BO release intentionally does nothing, so leaked refs can pin address space; freeing private pages always calls `set_pages_array_wb()` and must match successful uncacheable setup; and all byte-range users must avoid crossing BO limits. Concurrency depends on correct rbtree/list lock pairing and BO mutex ordering.

## Test Signals

Use allocation fragmentation tests with split/merge verification, equal-size free-chain tests, page allocation failure injection, MMU map failure rollback, bind/unbind TLB flush checks, vmalloc-backed BO tests, cached/uncached vmap transitions, mmap size mismatch and close/open refcount tests, and cleanup with outstanding mapped or bound BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm_bo.c -->
