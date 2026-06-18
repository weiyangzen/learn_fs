<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c` is the public HMM entry layer for AtomISP ISP memory management. It exposes allocation, free, load/store, memset, cache flush, physical address lookup, user mmap, and kernel vmap operations for ISP virtual addresses backed by `hmm_bo.c` buffer objects.

## Important APIs, Types, and Functions

Important APIs are hmm_init(), hmm_cleanup(), hmm_alloc(), hmm_create_from_vmalloc_buf(), hmm_free(), hmm_load(), hmm_flush(), hmm_store(), hmm_set(), hmm_virt_to_phys(), hmm_mmap(), hmm_vmap(), hmm_flush_vmap(), and hmm_vunmap(). The file also owns the global `bo_device`, `dummy_ptr`, and `hmm_initialized` variables.

## Control Flow

Initialization calls `hmm_bo_device_init()` with the Merrifield ISP MMU client and ISP virtual address range, marks the subsystem initialized, and allocates a dummy first page because address zero is treated as invalid. Allocation lazily initializes HMM if needed, rounds bytes to pages, allocates a BO, allocates private or vmalloc-backed pages, and binds them into the ISP MMU. Free performs lookup by BO start, unbinds, frees pages, and drops the BO reference. Load/store/set operations locate the BO containing the ISP pointer, prefer an existing or temporary vmap, otherwise walk page-by-page with `kmap_local_page()`, and flush cache lines for CPU/ISP coherency.

## State and Persistence Behavior

State persists in the global `bo_device` rbtree/list allocator, per-BO page arrays and MMU mappings, vmap status bits, and the dummy allocation. There is no file-backed persistence; the durable side effect is live ISP MMU mappings and page cacheability until cleanup/free.

## Dependencies and Integration Points

It depends on Linux page/vmap/kmap/cacheflush APIs, AtomISP logging through `atomisp_dev`, `hmm_bo` primitives, and the ISP MMU implementation from `sh_mmu_mrfld`. It integrates with CSS memory-manager callers that exchange `ia_css_ptr` ISP virtual addresses.

## Risks and Edge Cases

Range validation checks that an address belongs to a BO but most operations do not verify that `bytes` stays inside the BO, so cross-BO or out-of-range copy lengths are a review risk. `hmm_init()` sets `hmm_initialized` even if device init fails. Cache flushing and cached/uncached vmap transitions are subtle, and `hmm_virt_to_phys()` returns `-1` in a physical-address type on failure.

## Test Signals

Exercise init/cleanup, lazy init, zero/one/multi-page allocations, vmalloc-backed allocations, load/store/set across page boundaries, vmap cached and uncached paths, kmap fallback, mmap open/close reference counts, invalid pointers, oversized copy lengths, and MMU bind failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hmm/hmm.c -->
