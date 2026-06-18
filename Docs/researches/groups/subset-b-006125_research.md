# subset-b-006125 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/dmapool.c -->
# sources/distributed-fs/ceph-client/mm/dmapool.c

## Purpose
`dmapool.c` implements the kernel DMA pool allocator for small coherent DMA objects. It allocates coherent DMA pages with `dma_alloc_coherent()`, splits each page into fixed-size aligned blocks, and hands those blocks to device drivers that need many small DMA-safe descriptors or control structures. It also exposes per-device pool diagnostics through a `pools` sysfs attribute and provides devres-managed wrappers.

## Important APIs, types, and functions
The core internal types are `struct dma_pool`, `struct dma_page`, and `struct dma_block`. `struct dma_pool` owns the per-pool block size, allocation size, boundary limit, NUMA node, free-block head, page list, active/block/page counters, device pointer, spinlock, and registration list node under `dev->dma_pools`. `struct dma_page` records each coherent allocation's CPU virtual address and DMA address. Free blocks are stored in-band as `struct dma_block` nodes.

The exported API is `dma_pool_create_node()`, `dma_pool_destroy()`, `dma_pool_alloc()`, `dma_pool_free()`, `dmam_pool_create()`, and `dmam_pool_destroy()`. `dma_pool_create_node()` validates power-of-two alignment and boundary constraints, rounds object size, allocates the pool, links it into `dev->dma_pools`, and creates `dev_attr_pools` when the first pool appears. `dma_pool_alloc()` pops an available block or temporarily drops the pool spinlock to allocate and initialize a new DMA page. `dma_pool_free()` validates and pushes a block back. The managed wrappers allocate a devres slot and destroy the pool on device teardown.

## Control flow
Pool creation normalizes input first: zero alignment becomes one, non-power-of-two alignment or boundary is rejected, tiny objects are raised to `sizeof(struct dma_block)`, and each object is aligned. The page allocation size is at least `PAGE_SIZE`, and the usable boundary is clamped to the allocation size. Registration is serialized by `pools_reg_lock` and list mutation by `pools_lock` so sysfs file creation/removal cannot race with the first or last pool on a device.

Allocation enters `pool->lock`, pops `pool->next_block`, and increments `nr_active`. If the free list is empty it drops the spinlock, allocates a `struct dma_page` and coherent DMA memory, reacquires the spinlock, calls `pool_initialise_page()`, and then pops a block. `pool_initialise_page()` walks offsets through the coherent page, skips offsets whose object would cross the configured boundary, chains valid blocks, appends the chain to the global free list, links the page to `page_list`, and updates counters. Freeing runs `pool_block_err()` first, then stores the DMA address in the block, links it at the free-list head, and decrements `nr_active`.

## State and persistence
State is entirely in kernel memory and device lifetime structures. Pool pages persist until `dma_pool_destroy()` or devres release. `nr_blocks`, `nr_active`, and `nr_pages` are maintained for diagnostics and leak detection. `dma_pool_destroy()` removes the pool from the device list and removes the `pools` sysfs file when the device has no pools left. If `nr_active` is nonzero, it logs the pool as busy and deliberately avoids freeing coherent pages to avoid releasing DMA memory still in use.

With `CONFIG_SLUB_DEBUG_ON`, `DMAPOOL_DEBUG` poisons freed and allocated blocks, checks for corruption, verifies the DMA address belongs to a pool page, and detects double-free by scanning the free list. Without debug, free optionally zeroes blocks when `init_on_free` is enabled; allocation optionally zeroes blocks when requested by allocation policy.

## Dependencies and integration points
This file integrates with the DMA mapping API (`dma_alloc_coherent()`, `dma_free_coherent()`), the device model (`struct device`, sysfs attributes, `devres`), NUMA slab allocation, list/spinlock/mutex primitives, memory initialization hardening hooks (`want_init_on_alloc/free()`), poison constants, and exported symbols consumed by device drivers. It relies on `dev->dma_pools` being initialized by device core code.

## Risks and test signals
Important risks are boundary arithmetic, stale DMA/virtual address pairs on free, double-free, and incorrect lifetime handling when a driver destroys a busy pool. The allocator stores free-list metadata inside freed DMA objects, so use-after-free by a device or driver can corrupt allocator state. The page initialization path assumes at least one valid block fits after validation. Registration must keep sysfs creation and removal balanced across concurrent create/destroy calls.

Useful test signals include `dmapool_test.c`, driver probe/remove cycles using `dmam_pool_create()`, sysfs `poolinfo` counter sanity, SLUB debug poison reports, DMA API debug warnings, boundary-sensitive devices, and tests that destroy pools only after all active blocks are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/dmapool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/dmapool_test.c -->
# sources/distributed-fs/ceph-client/mm/dmapool_test.c

## Purpose
`dmapool_test.c` is a loadable timing and smoke-test module for the DMA pool allocator. It creates a synthetic device, builds pools with representative object sizes and alignments, repeatedly allocates and frees many blocks, and prints elapsed microseconds for each parameter set.

## Important APIs, types, and functions
`struct dma_pool_pair` stores one CPU pointer and DMA handle returned by `dma_pool_alloc()`. `struct dmapool_parms` describes a pool size, alignment, and boundary. `pool_parms[]` covers sizes from 16 bytes through 4096 bytes plus a nontrivial `{ size = 68, align = 32, boundary = 4096 }` case.

`nr_blocks()` scales the test block count by object size and clamps it between 1024 and 8192. `dmapool_test_alloc()` allocates all requested blocks, frees them, and unwinds partially successful allocations on failure. `dmapool_test_block()` allocates the pair array, creates a `dma_pool`, runs `NR_TESTS` allocation/free loops, yields with `cond_resched()` when needed, prints timing, and destroys the pool. `dmapool_checks()` is the module init routine that registers the fake device, configures DMA ops and a 64-bit coherent mask, and runs all parameter sets.

## Control flow
On module load, `dmapool_checks()` names and registers `test_dev`, assigns a release callback, clears DMA ops, installs `dma_mask`, and calls `dma_set_mask_and_coherent()`. It then iterates over `pool_parms[]`. Each iteration creates a pool, runs 100 full allocate/free passes over the chosen number of blocks, prints one line of timing, and tears the pool down. If any allocation, registration, or mask setup fails, the function jumps through cleanup labels to delete and put the device.

## State and persistence
The module uses file-scope `pool`, `test_dev`, and `dma_mask`. All test allocations are temporary and should be freed before each parameter case returns. There is no persistent state beyond printk output. `dmapool_exit()` is empty because all work is performed synchronously at module initialization.

## Dependencies and integration points
The test depends on the DMA mapping layer, device core registration, `dma_pool_create()/alloc/free/destroy()`, kernel timing via `ktime_get()` and `ktime_us_delta()`, scheduler rescheduling, and module init/exit infrastructure. It uses `kzalloc_objs()` for the pair array and `DMA_BIT_MASK(64)` to make the synthetic device broadly DMA-capable.

## Risks and test signals
The module is a timing smoke test, not a correctness proof. It does not validate returned alignment, boundary crossing, data poisoning, sysfs counters, or DMA API debug state. The synthetic device setup is minimal and may not model IOMMU-heavy real devices. A useful pass signal is successful module load producing timing lines for all parameter sets without allocation failure or DMA mask setup failure. Failures in this test point toward allocator regressions in page splitting, high-volume allocation/free loops, or fake-device DMA setup assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/dmapool_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/early_ioremap.c -->
# sources/distributed-fs/ceph-client/mm/early_ioremap.c

## Purpose
`early_ioremap.c` provides generic early-boot temporary mapping helpers for architectures that need to access physical I/O or memory before the normal `ioremap()` and `vmalloc` infrastructure is ready. It maps physical ranges through fixed-address boot-time slots and also supplies simple no-MMU identity mappings.

## Important APIs, types, and functions
The MMU path exports `early_ioremap_setup()`, `early_ioremap_reset()`, `early_ioremap()`, `early_memremap()`, `early_memremap_ro()`, optional `early_memremap_prot()`, `copy_from_early_mem()`, `early_iounmap()`, and `early_memunmap()`. The weak `early_memremap_pgprot_adjust()` lets architectures adjust protections. The central helper is `__early_ioremap()`, which reserves a slot from `prev_map[]`, page-aligns the physical range, installs fixed mappings with `__early_set_fixmap()` or `__late_set_fixmap()`, and returns the virtual address plus original offset.

## Control flow
`early_ioremap_setup()` initializes `slot_virt[]` from `FIX_BTMAP_BEGIN` and the per-slot fixed-map stride. `__early_ioremap()` finds a free slot, rejects zero or wrapping ranges, records the caller-visible size in `prev_size[]`, page-aligns the physical address and size, rejects mappings larger than `NR_FIX_BTMAPS`, installs one fixed mapping per page, and records the returned pointer in `prev_map[]`. `early_iounmap()` finds the matching slot by exact returned address, checks the size matches, computes the page count from the virtual offset and original size, clears the fixed mappings, and releases the slot.

`copy_from_early_mem()` copies an arbitrary physical range by repeatedly mapping chunks no larger than the fixed-map capacity, copying out of the mapped window, and unmapping. `check_early_ioremap_leak()` runs as a late initcall and warns if any slot remains mapped.

## State and persistence
The MMU implementation has `__initdata` state only: `early_ioremap_debug`, `after_paging_init`, `prev_map[]`, `prev_size[]`, and `slot_virt[]`. Mappings are temporary boot-time state and should be unmapped before late init. After `early_ioremap_reset()`, architectures that support late use must provide `__late_set_fixmap()` and `__late_clear_fixmap()`; otherwise the weak defaults call `BUG()`.

## Dependencies and integration points
The file depends on architecture fixmap definitions (`FIX_BTMAP_BEGIN`, `NR_FIX_BTMAPS`, `FIX_BTMAPS_SLOTS`, page protection constants), early fixmap functions, initcall ordering, `system_state`, and optional architecture protection overrides. It is used by early platform, firmware, memory discovery, and boot code that needs temporary physical access before full mapping services exist.

## Risks and test signals
Risks include leaking slots, mismatched unmap sizes, mapping ranges larger than the fixed-map window, physical address wraparound, and using late mappings on an architecture that did not implement late fixmap operations. Since unmap lookup is by exact returned pointer, callers must preserve the pointer and size. Test signals include booting with `early_ioremap_debug`, absence of late leak warnings, successful early firmware/table copies, and architecture boot tests that exercise both pre- and post-`paging_init()` use if supported. The no-MMU path should remain a simple identity mapping with no slot state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/early_ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/execmem.c -->
# sources/distributed-fs/ceph-client/mm/execmem.c

## Purpose
`execmem.c` implements the executable-memory allocator used for module text and other kernel executable ranges. It abstracts architecture-provided executable memory ranges, falls back to vmalloc space when no architecture setup is supplied, supports KASAN module shadow allocation, and optionally maintains a read-only-executable cache that can be temporarily made writable for text updates.

## Important APIs, types, and functions
Global state is `execmem_info`, a `struct execmem_info` containing per-`enum execmem_type` ranges, and `default_execmem_info`. `execmem_alloc()` allocates page-aligned memory for a type. `execmem_alloc_rw()` allocates and then forces it writable/non-executable for patching. `execmem_free()` frees through the ROX cache when possible, otherwise `vfree()`. `execmem_is_rox()` reports whether a type uses the ROX cache. `execmem_vmap()` reserves module-data virtual space.

The optional `CONFIG_ARCH_HAS_EXECMEM_ROX` cache uses `struct execmem_cache` with a mutex, `busy_areas` and `free_areas` maple trees, and a pending-free counter. Helpers include `execmem_cache_alloc_locked()`, `execmem_cache_populate_alloc()`, `__execmem_cache_free()`, delayed `execmem_cache_free_slow()`, and `execmem_cache_clean()`. Permission helpers are `execmem_force_rw()`, `execmem_restore_rox()`, and `execmem_set_direct_map_valid()`.

## Control flow
Initialization calls weak `execmem_arch_setup()`. If it returns `NULL`, the default range spans `VMALLOC_START` to `VMALLOC_END`, uses `PAGE_KERNEL_EXEC`, and has alignment 1. `execmem_validate()` requires the default range to have nonzero alignment, start, end, and page protection, and strips unsupported `EXECMEM_ROX_CACHE` flags when the architecture lacks ROX cache support. `execmem_init_missing()` copies the default range into missing type-specific ranges, except module data uses `PAGE_KERNEL`.

`execmem_alloc()` aligns size, selects the requested range, and either uses `execmem_cache_alloc()` for ROX-cache ranges or `execmem_vmalloc()` directly. The vmalloc path tries the primary range then a fallback range, applies KASAN shadow allocation if requested, and returns a tag-reset pointer. The ROX cache first tries to carve a suitable span from `free_areas`. If none exists, it allocates a PMD-sized or exact vmalloc block, fills it with trapping instructions, marks it ROX, adds the whole block to `free_areas`, and carves out the requested allocation atomically under the mutex.

Freeing a cached allocation finds its `busy_areas` entry. Fast free makes the range writable/NX, fills trapping instructions, restores ROX permissions, merges it into `free_areas`, removes it from `busy_areas`, and schedules cleanup. If fast free cannot allocate maple-tree metadata with `__GFP_NORETRY`, it marks the busy entry with `PENDING_FREE_MASK` and schedules delayed work. Cleanup returns PMD-aligned free ranges to the direct map and `vfree()`s them.

## State and persistence
`execmem_info` becomes read-only after init. Cached memory persists in the maple-tree free list after individual frees so later executable allocations can reuse it without repeated vmalloc/direct-map churn. Busy entries persist until `execmem_free()`. Pending-free state is encoded in the low bit range made available by page alignment. Workqueue items perform asynchronous retry and cleanup.

## Dependencies and integration points
The allocator depends on vmalloc internals, maple trees, memory permission APIs (`set_memory_nx/rw/rox`, `set_direct_map_valid_noflush()`), KASAN module shadow support, architecture TLB/cache behavior, module loader ranges, and text-patching helpers such as `execmem_fill_trapping_insns()`. Architecture code can override `execmem_arch_setup()` and choose late initialization through `CONFIG_ARCH_WANTS_EXECMEM_LATE`.

## Risks and test signals
Key risks are permission transitions that briefly expose writable executable memory, direct-map alias validity, maple-tree range merge/split bugs, delayed-free starvation, and incorrect architecture range definitions. `within_range()` range checks and fallback handling are security-sensitive because executable memory must remain inside intended regions. Test signals include module load/unload under KASAN, BPF/kprobe/ftrace/text-patching users, ROX permission tests, memory hotplug/direct-map checks, and fault injection around maple-tree allocation during free. Warnings from `execmem_validate()` indicate module loading may fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/execmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/fadvise.c -->
# sources/distributed-fs/ceph-client/mm/fadvise.c

## Purpose
`fadvise.c` implements generic and VFS-level handling for `posix_fadvise()` style advice. It lets callers tune read-ahead behavior, prefetch expected pages, mark no-reuse access, or discard clean cached pages over a byte range without changing file contents.

## Important APIs, types, and functions
`generic_fadvise()` is the main implementation and is exported for filesystem use. `vfs_fadvise()` dispatches to `file->f_op->fadvise` when provided, otherwise calls the generic implementation. `ksys_fadvise64_64()` resolves an fd and calls `vfs_fadvise()`. Syscall wrappers are conditionally compiled for native `fadvise64_64`, optional `fadvise64`, and compat `fadvise64_64`.

## Control flow
The generic path rejects FIFOs with `-ESPIPE`, rejects negative offsets/lengths or missing mappings with `-EINVAL`, and ignores valid advice for DAX or noop backing devices. It computes an inclusive `endbyte`, treating `len == 0` or overflow as "to end of addressable range".

For `POSIX_FADV_NORMAL`, it resets readahead pages to the backing device default and clears random/no-reuse mode bits. `POSIX_FADV_RANDOM` sets `FMODE_RANDOM`; `POSIX_FADV_SEQUENTIAL` doubles `ra_pages` and clears random mode. `POSIX_FADV_WILLNEED` computes page indexes and calls `force_page_cache_readahead()`. `POSIX_FADV_NOREUSE` sets `FMODE_NOREUSE`. `POSIX_FADV_DONTNEED` first starts writeback for the range, then invalidates only full pages: it rounds the start up, handles the inclusive end page carefully so partial tail pages are preserved unless page-aligned or EOF, drains local LRU additions, tries `mapping_try_invalidate()`, and if failures remain drains all CPU LRU caches and retries with `invalidate_mapping_pages()`.

## State and persistence
Persistent effects are limited to `file->f_ra.ra_pages` and `file->f_mode` advice bits under `file->f_lock`. `WILLNEED` and `DONTNEED` affect page-cache residency but not file data. The operation does not store advice in the inode or on disk.

## Dependencies and integration points
The file integrates with fd lookup, VFS file operations, backing-device readahead settings, DAX detection, page-cache readahead, writeback, LRU drain logic, page-cache invalidation, and syscall compatibility glue. Filesystems can override behavior through `f_op->fadvise`.

## Risks and test signals
Range arithmetic and partial-page handling are the main correctness risks, especially around `len == 0`, overflow, EOF, and unsigned `pgoff_t` underflow. `DONTNEED` must avoid discarding dirty data, hence the flush and retry behavior. Useful tests include syscall ABI tests for native and compat argument packing, FIFO `-ESPIPE`, invalid-advice `-EINVAL`, DAX/noop backing no-op behavior, readahead mode observation, and cache residency checks before and after `WILLNEED` or `DONTNEED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/fadvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/fail_page_alloc.c -->
# sources/distributed-fs/ceph-client/mm/fail_page_alloc.c

## Purpose
`fail_page_alloc.c` implements page allocator fault injection. It decides when page allocations should fail based on global fault-injection policy, allocation order, and GFP flag filters, allowing kernel error paths to be exercised deliberately.

## Important APIs, types, and functions
The file-scope `fail_page_alloc` object contains `struct fault_attr attr`, `ignore_gfp_highmem`, `ignore_gfp_reclaim`, and `min_order`. Defaults ignore highmem allocations, ignore direct-reclaim allocations, and inject only for order 1 or higher. `setup_fail_page_alloc()` parses the `fail_page_alloc=` boot parameter. `should_fail_alloc_page()` is the exported decision point and is marked with `ALLOW_ERROR_INJECTION(..., TRUE)`. With fault-injection debugfs enabled, `fail_page_alloc_debugfs()` creates tunables under `fail_page_alloc`.

## Control flow
`should_fail_alloc_page()` returns false when the allocation order is below `min_order`, `__GFP_NOFAIL` is set, the highmem filter matches, or the direct-reclaim filter matches. It translates `__GFP_NOWARN` into `FAULT_NOWARN`, then calls `should_fail_ex()` with a size weight of `1 << order`. The debugfs init path creates the base fault-attribute directory and adds booleans for reclaim/highmem filters plus a `min-order` u32 knob.

## State and persistence
State lives in the global fault attributes and debugfs-exposed filter fields. Boot parameters initialize the fault policy early; debugfs updates adjust it at runtime. No per-allocation state is persisted.

## Dependencies and integration points
This code depends on `linux/fault-inject.h`, debugfs, error-injection infrastructure, and the page allocator's call site for `should_fail_alloc_page()`. It reflects allocator semantics by respecting `__GFP_NOFAIL` and optionally avoiding highmem or reclaimable contexts.

## Risks and test signals
Misconfigured injection can make broad kernel paths fail, so default filters are conservative. The size weight must stay consistent with order semantics, and `__GFP_NOFAIL` must never be failed. Useful signals include booting with `fail_page_alloc=` parameters, modifying debugfs knobs, observing expected allocation failures without warnings when `__GFP_NOWARN` is present, and running MM error-path or fstest workloads under injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/fail_page_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/failslab.c -->
# sources/distributed-fs/ceph-client/mm/failslab.c

## Purpose
`failslab.c` implements slab allocator fault injection. It lets tests force selected `kmem_cache` allocations to fail so slab-user error handling can be validated.

## Important APIs, types, and functions
The global `failslab` object holds `struct fault_attr attr`, `ignore_gfp_reclaim`, and `cache_filter`. `should_failslab()` is the allocator-facing decision function and returns `-ENOMEM` or 0; it is enabled for errno-style error injection. `setup_failslab()` parses `failslab=` boot options. `failslab_debugfs_init()` creates debugfs controls for the generic fault attributes plus `ignore-gfp-wait` and `cache-filter`.

## Control flow
`should_failslab()` immediately skips the bootstrap `kmem_cache`, `__GFP_NOFAIL` allocations, direct-reclaim allocations when the filter is enabled, and caches not marked `SLAB_FAILSLAB` when `cache_filter` is true. It maps `__GFP_NOWARN` to `FAULT_NOWARN` and calls `should_fail_ex()` using `s->object_size` as the size argument. A true fault-injection decision becomes `-ENOMEM`.

## State and persistence
All policy state is global and runtime mutable through debugfs when configured. The injection decision does not persist per-cache or per-object state. `cache_filter` allows tests to restrict failures to caches explicitly opted in by `SLAB_FAILSLAB`.

## Dependencies and integration points
This file depends on slab internals (`struct kmem_cache`, `kmem_cache`, `SLAB_FAILSLAB`), common fault-injection policy, boot parameter parsing, debugfs, and error injection. It is called from slab allocation paths before an object is returned to callers.

## Risks and test signals
Faulting bootstrap, nofail, or reclaim-sensitive allocations could destabilize the system, so those paths are guarded. The main test signals are boot parameter parsing, debugfs control visibility, expected `-ENOMEM` from targeted cache allocations, absence of allocation warnings under `__GFP_NOWARN`, and cache-filter behavior that only fails `SLAB_FAILSLAB` caches when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/failslab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/filemap.c -->
# sources/distributed-fs/ceph-client/mm/filemap.c

## Purpose
`filemap.c` is the core generic page-cache implementation for normal file data. It manages insertion, lookup, removal, writeback waiting, buffered reads and writes, direct-I/O cache invalidation, file-backed mmap faults, fault-around mapping, page-cache wait queues, `SEEK_HOLE`/`SEEK_DATA` helpers, and the `cachestat` syscall when enabled. Filesystems and VFS code rely on it for the common buffered I/O and mmap behavior.

## Important APIs, types, and functions
The file is built around `struct address_space`, xarray `mapping->i_pages`, `struct folio`, `struct folio_batch`, `struct file_ra_state`, `struct writeback_control`, `struct kiocb`, and `struct vm_fault`. Important exported functions include page-cache mutation (`filemap_add_folio()`, `__filemap_add_folio()`, `filemap_remove_folio()`, `delete_from_page_cache_batch()`, `replace_page_cache_folio()`), lookup and batching (`filemap_get_entry()`, `__filemap_get_folio_mpol()`, `filemap_get_folios*()`, `find_get_entries()`, `find_lock_entries()`), writeback/error handling (`filemap_fdatawrite*()`, `filemap_flush*()`, `filemap_fdatawait*()`, `filemap_write_and_wait_range()`, `file_check_and_advance_wb_err()`), waits and folio completion (`folio_unlock()`, `folio_end_read()`, `folio_end_writeback()`, `folio_wait_bit*()`, `__folio_lock_or_retry()`), buffered I/O (`filemap_read()`, `generic_file_read_iter()`, `generic_perform_write()`, `generic_file_write_iter()`), mmap (`filemap_fault()`, `filemap_map_pages()`, `generic_file_mmap()`), and direct-write helpers (`generic_file_direct_write()`, `kiocb_invalidate_pages()`).

## Control flow
Page-cache insertion charges memcg, locks the folio, inserts it into `mapping->i_pages` with the correct order, handles conflicts with shadow entries and larger entries, updates `mapping->nrpages` and VM counters, records workingset refaults, and adds the folio to LRU. Removal runs the inverse path: it requires locked folios, unaccounts VM state, clears the xarray slot or stores a shadow, clears mapping, updates shrinker/LRU state, calls filesystem `free_folio`, and drops page-cache references.

Writeback helpers build `writeback_control`, call `do_writepages()`, then wait on folios tagged `PAGECACHE_TAG_WRITEBACK`. Mapping-wide legacy error bits `AS_EIO`/`AS_ENOSPC` and modern `errseq_t wb_err` are both handled. File-scoped error reporting advances `file->f_wb_err` under `file->f_lock`.

Buffered reads call `filemap_get_pages()` to gather contiguous uptodate folios, trigger synchronous or asynchronous readahead, create and fill missing folios under the invalidate lock, and then copy folio data into the destination iterator while honoring `i_size`. `generic_file_read_iter()` runs direct I/O first when requested, then falls back to buffered reads for remaining data when allowed. Splice uses the same page-cache population path but inserts page-cache pipe buffers.

Buffered writes use `generic_file_write_iter()` to lock the inode, run generic write checks, remove privileges, update times, then either perform direct I/O or call `generic_perform_write()`. The buffered write loop uses filesystem `write_begin`/`write_end`, copies from the iterator atomically to avoid recursive page-fault deadlocks, handles short copies by reducing chunk size or faulting in user pages, updates `ki_pos`, and lets the caller perform sync handling.

The mmap fault path first checks EOF for SIGBUS, tries to find the folio, performs async or sync mmap readahead, creates a folio if needed, locks it while possibly dropping the fault lock, validates truncation races, reads non-uptodate folios synchronously, rechecks `i_size`, and returns a locked page for the fault core. Fault-around (`filemap_map_pages()`) scans uptodate unlocked folios under RCU, locks them, maps order-0 or large folio ranges through PTEs or PMDs where legal, updates RSS counters, and adjusts mmap readahead miss accounting.

## State and persistence
Persistent runtime state includes the page-cache xarray, folio flags (`locked`, `uptodate`, `dirty`, `writeback`, `readahead`, `dropbehind`, `workingset`, `private_2`), xarray marks, `mapping->nrpages`, VM/memcg statistics, per-file readahead state, writeback error cursors, and hashed wait queues initialized by `pagecache_init()`. No state is on-disk by itself, but dirty folios represent data that must be written by filesystem address-space operations.

Locking state is central: the file documents ordering across inode locks, invalidate locks, mmap locks, page-table locks, xarray locks, writeback locks, and LRU locks. The invalidate lock prevents new page-cache folios from being instantiated during truncate/hole-punch/direct-I/O invalidation. RCU lookup plus speculative folio references are used to avoid global locking while staying safe against concurrent removal.

## Dependencies and integration points
`filemap.c` is a nexus for the VFS, filesystem `address_space_operations`, readahead, writeback, memcg, LRU/workingset, xarray, DAX/shmem/hugetlb distinctions, swap/shadow entries, page-table helpers, pipe/splice, security/permission checks for cachestat, sysctl registration, PSI/delay accounting, and tracepoints (`trace/events/filemap.h`). Ceph and other distributed filesystems integrate by supplying `read_folio`, `readahead`, `write_begin`, `write_end`, `direct_IO`, `release_folio`, and writeback operations that these generic paths call.

## Risks and test signals
The highest risks are races with truncation, hole punching, reclaim, writeback completion, mmap faults, direct I/O, and large-folio xarray entries. Incorrect reference handling can lead to use-after-free; incorrect locking can deadlock; incorrect `i_size` checks can expose zero-filled data past EOF or miss SIGBUS; failed invalidation after direct I/O can cause stale page-cache data, for which the code emits a ratelimited critical warning and records `-EIO`. Large folio order handling must preserve alignment, range bounds, and page-table limits.

Useful test signals include generic filesystem buffered read/write tests, mmap fault and fault-around tests, direct I/O plus buffered collision tests, truncate/hole-punch races, large-folio and THP page-cache tests, writeback error reporting via fsync, `SEEK_HOLE`/`SEEK_DATA`, `splice`, `cachestat`, lockdep, KCSAN/KASAN, xfstests across local and network filesystems, and tracepoints for page-cache add/delete/fault/map activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/filemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/folio-compat.c -->
# sources/distributed-fs/ceph-client/mm/folio-compat.c

## Purpose
`folio-compat.c` provides out-of-line compatibility wrappers for older `struct page` APIs while the kernel transitions callers to folio-native interfaces. It keeps legacy exported symbols available without forcing large inline wrappers into every caller.

## Important APIs, types, and functions
The file exports page-based wrappers for common folio operations: `unlock_page()`, `end_page_writeback()`, `wait_on_page_writeback()`, `mark_page_accessed()`, `set_page_writeback()`, `set_page_dirty()`, `set_page_dirty_lock()`, `clear_page_dirty_for_io()`, `redirty_page_for_writepage()`, `add_to_page_cache_lru()`, and `pagecache_get_page()`. Each wrapper converts `struct page *` to the containing folio with `page_folio()` and delegates to the folio or filemap implementation.

## Control flow
Most functions are single-step adapters: convert page to folio, call the folio helper, and return its result if any. `add_to_page_cache_lru()` delegates to `filemap_add_folio()`. `pagecache_get_page()` calls `__filemap_get_folio()` with caller-provided `fgp_flags` and `gfp`; if lookup returns an error pointer it returns `NULL`, otherwise it returns the page within the folio corresponding to the requested index with `folio_file_page()`.

## State and persistence
This file owns no state. It mutates page-cache, dirty, writeback, and LRU state indirectly through the folio APIs it wraps. Symbol exports preserve ABI/API continuity for in-tree and module callers still using page names.

## Dependencies and integration points
The wrappers depend on `pagemap`, migration/rmap/swap headers, writeback control, and the generic filemap folio APIs. They integrate legacy page API users with the folio-first MM implementation, including filesystem writeback, migration, dirty accounting, and page-cache insertion/lookup.

## Risks and test signals
The main risk is semantic drift between legacy page functions and folio-native behavior, especially for large folios where a page pointer may refer to a subpage. `pagecache_get_page()` must return the correct subpage for an index inside a folio. Useful signals are successful builds of legacy callers, module symbol resolution, page-cache/dirty/writeback tests that still use page APIs, and large-folio tests ensuring wrappers preserve expected page-level results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/folio-compat.c -->
