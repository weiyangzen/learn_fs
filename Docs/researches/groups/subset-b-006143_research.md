# Research: subset-b-006143

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu.c -->
# sources/distributed-fs/ceph-client/mm/percpu.c

## Purpose
`percpu.c` implements the generic Linux dynamic percpu allocator. In this source tree it is generic MM infrastructure that Ceph-client code may depend on indirectly through kernel facilities that allocate per-CPU counters, work state, caches, and subsystem data. It manages the static first percpu region created during boot, optional reserved percpu space for module percpu variables, and dynamically allocated percpu chunks used after normal allocation services are available.

The allocator represents a percpu allocation as the same byte offset in every CPU unit of a chunk. Chunks are divided into units, one unit per possible CPU, and units can be grouped by NUMA locality. The allocator backs units lazily, maintains chunk free-space bitmaps and block metadata hints, optionally accounts allocations to memory cgroups and allocation profiling, and runs asynchronous balance work to keep enough populated pages for atomic allocations while reclaiming idle populated pages and excess empty chunks.

## Important APIs, Types, and Functions
The primary exported runtime APIs are `pcpu_alloc_noprof()` and `free_percpu()`. `pcpu_alloc_noprof()` validates size and alignment, chooses reserved or normal chunks, handles atomic versus sleepable allocation policy, charges memcg/profiling hooks, populates backing pages when necessary, zeroes every CPU copy, returns a `void __percpu *`, and emits percpu tracepoints. `free_percpu()` translates a percpu pointer back to a chunk, frees the bitmap area, releases memcg/profiling state, and schedules balancing when chunks become empty or reclaimable.

Boot/setup APIs include `pcpu_alloc_alloc_info()`, `pcpu_free_alloc_info()`, `pcpu_setup_first_chunk()`, `pcpu_embed_first_chunk()`, `pcpu_page_first_chunk()`, generic `setup_per_cpu_areas()` variants, and the `percpu_alloc=` early parameter parser. Address helpers include `__addr_to_pcpu_ptr()`, `__pcpu_ptr_to_addr()`, `pcpu_chunk_addr_search()`, `__is_kernel_percpu_address()`, `is_kernel_percpu_address()`, `per_cpu_ptr_to_phys()`, and `pcpu_nr_pages()`.

Key state objects are `struct pcpu_chunk`, `struct pcpu_block_md`, and `struct pcpu_alloc_info`, with definitions coming from `percpu-internal.h` and public percpu headers. Important global state includes `pcpu_first_chunk`, `pcpu_reserved_chunk`, `pcpu_base_addr`, `pcpu_unit_map`, `pcpu_unit_offsets`, chunk list slot indices, `pcpu_chunk_lists`, `pcpu_lock`, `pcpu_alloc_mutex`, `pcpu_nr_empty_pop_pages`, `pcpu_nr_populated`, and the deferred `pcpu_balance_work`.

The allocation bitmap helpers are central: `pcpu_find_block_fit()`, `pcpu_find_zero_area()`, `pcpu_alloc_area()`, and `pcpu_free_area()` operate on allocation and boundary maps; `pcpu_block_update_hint_alloc()`, `pcpu_block_update_hint_free()`, `pcpu_chunk_refresh_hint()`, and `pcpu_block_refresh_hint()` maintain fast-path metadata. Chunk population is delegated to the included backend file, either `percpu-km.c` or `percpu-vm.c`, through `pcpu_populate_chunk()`, `pcpu_depopulate_chunk()`, `pcpu_post_unmap_tlb_flush()`, `pcpu_create_chunk()`, `pcpu_destroy_chunk()`, `pcpu_addr_to_page()`, and `pcpu_verify_alloc_info()`.

## Control Flow
At boot, architecture or generic setup code builds a `pcpu_alloc_info`, allocates or maps the first chunk, copies static percpu data into each unit, and calls `pcpu_setup_first_chunk()`. That function validates the layout, records CPU-to-unit mappings, computes unit and chunk sizing, creates chunk slot lists, splits the first chunk into static, optional reserved, and dynamic regions, initializes `pcpu_first_chunk` and `pcpu_reserved_chunk`, and records the base address. SMP setups can select embedded first chunk allocation or page-remapped first chunk allocation; UP setup creates a single identity-mapped dynamic unit.

Runtime allocation starts by normalizing GFP flags, rounding size/alignment to `PCPU_MIN_ALLOC_SIZE`, checking allocation limits, and optionally precharging the current object cgroup. Sleepable allocations take `pcpu_alloc_mutex`; all chunk metadata operations are protected by `pcpu_lock`. Reserved allocations search only the reserved chunk. Normal allocations scan chunk slots from the requested size class to the free slot, using block metadata hints before scanning the bitmap. If no existing chunk fits and the request can sleep, a new chunk is created and the scan restarts. Once an area is reserved, sleepable allocations populate any missing backing pages outside the spinlock, update populated-page bookkeeping after each successful range, zero the per-CPU copies, and install accounting metadata.

Freeing reverses the address translation, uses the boundary bitmap to recover allocation size, clears the allocation bitmap, updates hints and counters, removes accounting, and either schedules balance work for excess free chunks or isolates chunks whose empty populated pages should be reclaimed. The balance worker runs under `pcpu_alloc_mutex` and `pcpu_lock`, frees excess fully free chunks, depopulates isolated empty pages, replenishes populated free pages for future atomic allocations, and then tries to free chunks that became fully depopulated. Balance work is enabled only after `subsys_initcall(percpu_enable_async)`, because early boot lacks workqueue/slab support.

## State and Persistence Behavior
The file persists only in-memory kernel allocator state. It has no on-disk persistence. Durable state consists of global percpu topology tables, chunk lists, chunk allocation bitmaps, chunk boundary bitmaps, metadata-block hints, populated-page bitmaps, object-cgroup pointers in optional `obj_exts`, allocation profiling tags, and page-to-chunk reverse mappings via `page->private`. The first chunk is immutable in population terms and is special because it contains static percpu variables. Dynamic chunks can be created, populated, depopulated, sidelined, reintegrated, or destroyed.

Memcg-aware allocations are selected by `__GFP_ACCOUNT`. Non-root memcg allocations charge the full percpu object size before allocation, store an object cgroup pointer in the chunk extension after success, update `MEMCG_PERCPU_B`, and uncharge on free or allocation failure. Allocation profiling stores per-object allocation tags when configured. `pcpu_nr_pages()` exposes populated backing pages multiplied by the unit count, excluding metadata.

## Dependencies and Integration Points
This allocator depends on memblock for early allocation, slab/vmalloc for metadata, workqueues for background balancing, CPU topology and NUMA distance callbacks for first-chunk layout, vmalloc or kmapping backends, tracepoints in `trace/events/percpu.h`, kmemleak, memcg, allocation profiling, cache/TLB flush primitives, and architecture-provided percpu address translation hooks.

It integrates with the rest of the kernel through `alloc_percpu()`-style APIs that eventually call `pcpu_alloc_noprof()`, module static percpu reservations, memory reporting, and architecture setup. For Ceph-client relevance, this is a foundational allocator for per-CPU kernel data used by filesystems, networking, workqueues, memory management, and tracing rather than a Ceph-specific component.

## Risks and Edge Cases
Correctness depends on bitmap/hint consistency. A wrong boundary bit can corrupt free-size recovery; stale contig hints can cause failed allocations or excessive scanning; and populated-page counters must match actual backend page state. Atomic allocations can only use already populated backing pages, so failure history drives background population. Large atomic allocations are explicitly unreliable.

Concurrency risks are concentrated around `pcpu_lock` versus `pcpu_alloc_mutex`, temporary lock dropping during population/depopulation, chunk isolation during reclaim, and pointer-to-chunk lookup through page metadata. Boot setup uses `BUG()`/panic paths for impossible topology or layout errors. The first chunk can be embedded in the linear map or vmalloc-mapped, making physical translation and address-range tests architecture-sensitive. Memcg/profiling extension allocation must be available for charged allocations; if not, precharges are undone.

## Test Signals
Useful signals include boot on SMP, UP, NUMA, embedded first chunk, and page first chunk configurations; module percpu allocation from the reserved region; allocation/free stress with many sizes and alignments; atomic allocation under low populated-page conditions; chunk depopulation/reintegration under idle workloads; `percpu_alloc=` early parameter coverage; memcg charged percpu allocation and uncharge accounting; allocation profiling deltas; kmemleak behavior; `per_cpu_ptr_to_phys()` on embedded and vmalloc-backed chunks; tracepoint coverage for allocation, free, and chunk creation; and lockdep/KASAN/KCSAN coverage for concurrent allocation/free/reclaim paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/percpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pgalloc-track.h -->
# sources/distributed-fs/ceph-client/mm/pgalloc-track.h

## Purpose
`pgalloc-track.h` provides small inline wrappers around page-table allocation helpers that also record which upper-level page-table entries were modified. It is used by walkers or mapping code that need to allocate missing page-table levels and later know whether PGD, P4D, PUD, or PMD entries changed.

## Important APIs, Types, and Functions
The header defines `p4d_alloc_track()`, `pud_alloc_track()`, `pmd_alloc_track()`, and the `pte_alloc_kernel_track()` macro. The functions accept an `mm_struct`, the parent page-table pointer, an address, and a `pgtbl_mod_mask *`. When a missing parent entry is allocated by `__p4d_alloc()`, `__pud_alloc()`, or `__pmd_alloc()`, the wrapper ORs the corresponding `PGTBL_*_MODIFIED` bit into the supplied mask before returning the normal child pointer.

`pte_alloc_kernel_track()` performs the same role for kernel PTE tables: when the PMD is none and `__pte_alloc_kernel()` succeeds, it sets `PGTBL_PMD_MODIFIED`; then it returns `pte_offset_kernel()`. The upper-level helpers are present only under `CONFIG_MMU`; the kernel-PTE macro is defined unconditionally by the header.

## Control Flow
Each helper is a straight-line allocate-if-missing wrapper. It checks whether the parent entry is none, calls the underlying allocator, returns `NULL` on allocation failure, records the modification bit on success, and returns the child table offset for the requested address. No table is allocated and no mask bit is set when the parent entry is already present.

## State and Persistence Behavior
The header owns no state. Persistent effects are the page-table pages installed by the underlying allocation helpers and the caller-owned modification mask. The mask is transient but important to callers that defer cache/TLB synchronization, accounting, or validation until after page-table walking.

## Dependencies and Integration Points
The wrapper depends on core MM page-table types and allocation routines declared by Linux MM headers. It integrates with page-table modification paths that need source-level visibility into which levels changed, commonly code that maps kernel or user ranges through generic page-table walking helpers.

## Risks and Edge Cases
The main risk is mask accuracy. Callers may skip required follow-up work if a wrapper allocates a table but fails to set the right bit. The `pte_alloc_kernel_track()` macro is compact and relies on side effects in a conditional expression, so maintenance changes must preserve short-circuit behavior: failed allocation must return `NULL`, successful allocation must set `PGTBL_PMD_MODIFIED`, and existing PMDs must not set the mask. The helper assumes the caller supplies a valid mask pointer.

## Test Signals
Compile coverage under folded and unfolded page-table configurations is the primary signal. Runtime validation should exercise mapping code that allocates every page-table level from empty parents, verifies the returned child pointers are usable, checks modification-mask bits, and confirms no bits are set when walking already-populated tables. Allocation-failure injection should verify `NULL` return without bogus mask updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pgalloc-track.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pgtable-generic.c -->
# sources/distributed-fs/ceph-client/mm/pgtable-generic.c

## Purpose
`pgtable-generic.c` supplies generic implementations of page-table helpers declared by `linux/pgtable.h` when an architecture does not override them. It covers bad-entry clearing, access/young/dirty permission updates, transparent-hugepage page-table helpers, safe PTE mapping and locking under RCU, deferred PTE freeing, and optional asynchronous freeing of kernel page-table pages.

## Important APIs, Types, and Functions
Bad-entry handlers include `pgd_clear_bad()`, `p4d_clear_bad()`, `pud_clear_bad()`, and `pmd_clear_bad()`, each reporting an architecture error and clearing the entry. Generic access helpers include `ptep_set_access_flags()`, `ptep_clear_flush_young()`, and `ptep_clear_flush()`. THP helpers include `pmdp_set_access_flags()`, `pmdp_clear_flush_young()`, `pmdp_huge_clear_flush()`, optional `pudp_huge_clear_flush()`, `pgtable_trans_huge_deposit()`, `pgtable_trans_huge_withdraw()`, `pmdp_invalidate()`, `pmdp_invalidate_ad()`, `pmdp_collapse_flush()`, and `pte_free_defer()`.

PTE mapping helpers are `__pte_offset_map()`, `pte_offset_map_ro_nolock()`, `pte_offset_map_rw_nolock()`, and `pte_offset_map_lock()`. They provide the generic concurrency protocol for safely looking up PTE tables while another thread might remove a table, replace it with a THP PMD, or free it after RCU grace. Optional `pagetable_free_kernel()` queues kernel page-table descriptors to a work item when `CONFIG_ASYNC_KERNEL_PGTABLE_FREE` is enabled.

## Control Flow
Bad-entry handlers are invoked by page-table walk macros when an entry is neither none nor valid; they log through architecture-specific `*_ERROR()` hooks and clear the entry to stop further misuse. Access-flag helpers compare old and new entries, install more-permissive entries when changed, and flush enough TLB state for spurious faults or young-bit clearing.

THP helpers operate on PMD/PUD-sized ranges and enforce hugepage alignment with `VM_BUG_ON()`. Deposit/withdraw maintains a FIFO list of preallocated PTE tables hanging off a huge PMD so THP split/collapse code can swap between huge PMD and PTE-table representations. Invalidation helpers establish invalid PMDs and flush huge PMD ranges; collapse flushing clears PTE-table PMDs and flushes the full range because PTE mappings are being collapsed into a huge PMD.

The PTE lookup path starts `rcu_read_lock()`, obtains a lockless PMD value, rejects none, non-present, THP, or bad PMDs, and maps the PTE page. Some configurations disable interrupts around split high/low PMD reads so a successful map cannot be based on mismatched halves. `pte_offset_map_lock()` then takes the page-table lock associated with the captured PMD value and rechecks that the PMD is still the same; on mismatch it unlocks, unmaps, and retries.

## State and Persistence Behavior
The file persists no independent state except the optional `kernel_pgtable_work` queue/list. Its operations mutate page-table entries, THP deposit lists, and deferred-free RCU/workqueue state. PTE mapping helpers deliberately hold RCU read-side state until callers unmap, ensuring disconnected page-table pages remain valid while inspected. Asynchronous kernel page-table freeing persists a list of `ptdesc` objects until the worker invalidates IOMMU SVA KVA mappings and frees them.

## Dependencies and Integration Points
The implementation depends on architecture page-table accessors and flush primitives, MMU/TLB APIs, THP configuration, RCU, IOMMU SVA invalidation, and page-table allocation/free helpers. It is integrated across fault handling, mprotect, reclaim, rmap, THP split/collapse, GUP, page walkers, and kernel page-table teardown. Architectures can override many functions with `__HAVE_ARCH_*` macros, making this file the fallback contract.

## Risks and Edge Cases
The highest-risk area is concurrent PTE-table lookup while page tables are removed or replaced by huge mappings. Callers must obey the documented distinction between read-only nolock lookup, writable nolock lookup requiring later stability checks, and locked lookup. THP helpers require exact hugepage alignment and correct TLB flush granularity. Deposit/withdraw list corruption would break THP split/collapse. Deferred freeing requires RCU or worker ordering to prevent use-after-free by lockless walkers. Async kernel page-table free must invalidate IOMMU KVA range before freeing page tables.

## Test Signals
Signals include architecture builds with and without each `__HAVE_ARCH_*` override; THP split, collapse, mprotect, young-bit aging, and fault tests; lockless GUP racing with THP collapse/split and page-table teardown; bad-entry injection or debug assertions; RCU KASAN/KCSAN coverage around `pte_offset_map*`; kernel page-table free with `CONFIG_ASYNC_KERNEL_PGTABLE_FREE`; and IOMMU SVA tests that validate stale KVA translations are invalidated before async free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/pgtable-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/process_vm_access.c -->
# sources/distributed-fs/ceph-client/mm/process_vm_access.c

## Purpose
`process_vm_access.c` implements the `process_vm_readv(2)` and `process_vm_writev(2)` system calls. These calls copy bytes directly between the calling process and another process address space using local and remote iovec arrays, avoiding an intermediate pipe or ptrace data loop. The code is generic process-memory access infrastructure, not filesystem-specific.

## Important APIs, Types, and Functions
The syscall entry points are `SYSCALL_DEFINE6(process_vm_readv, ...)` and `SYSCALL_DEFINE6(process_vm_writev, ...)`, both delegating to `process_vm_rw()`. `process_vm_rw()` imports the local iovec into an `iov_iter`, imports the remote iovec array, validates that flags are zero, and calls `process_vm_rw_core()`.

`process_vm_rw_core()` resolves the target task by PID, performs ptrace-style permission checks through `mm_access(task, PTRACE_MODE_ATTACH_REALCREDS)`, sizes a temporary `struct page *` array, and iterates each remote vector. `process_vm_rw_single_vec()` pins remote pages with `pin_user_pages_remote()`, copies each batch through `process_vm_rw_pages()`, unpins pages, and dirties them for writes with `unpin_user_pages_dirty_lock()`. `process_vm_rw_pages()` performs the actual page-to-iterator or iterator-to-page copy with `copy_page_to_iter()` and `copy_page_from_iter()`.

## Control Flow
The syscall path first rejects nonzero flags with `-EINVAL`. The local iovec is imported as `ITER_DEST` for reads from the target process and `ITER_SOURCE` for writes to the target process. Empty local iterators short-circuit successfully. The remote iovec is copied from userspace, with compat handling when needed.

Core execution computes the largest number of remote pages needed by any remote iovec. It uses a stack page-pointer array for small batches and kmallocs at most two pages of pointer storage for larger requests. After task lookup and permission checks, each remote iovec is processed until the local iterator is exhausted or an error occurs. For each remote range, the code computes the starting page, offset, and number of pages; pins pages in bounded batches under the remote mmap read lock; copies bytes page by page; advances address and offsets; and unpins. If any bytes were copied before an error, the syscall returns the partial byte count rather than the error.

## State and Persistence Behavior
The code has no persistent state. It temporarily pins remote pages, maps local iovec state in an `iov_iter`, holds task and mm references, and optionally dirties remote pages on writes. Writes persist only as normal modifications to the remote process memory and its backing pages; file-backed shared mappings may later participate in normal dirty/writeback behavior through generic MM mechanisms. All temporary page pins and references are released before returning.

## Dependencies and Integration Points
Dependencies include the syscall layer, iovec import helpers, `iov_iter`, task lookup/refcounting, ptrace permission checks, `mm_access()`, remote GUP (`pin_user_pages_remote()`), highmem-safe page copy helpers, and dirty unpin helpers. The integration point for filesystems is indirect: if the target memory is a writable shared file mapping, dirtying and later writeback are handled by generic MM and the underlying filesystem.

## Risks and Edge Cases
The main externally visible semantics are partial transfer and error mapping. A short copy due to a later bad remote address returns the bytes copied so far. Permission failures from `mm_access()` map `-EACCES` to `-EPERM`. Remote pages can disappear between vector validation and pinning, producing `-EFAULT`. The temporary page-pointer array is deliberately bounded for reliability. Write mode must pass `FOLL_WRITE` and dirty pages on unpin; failing to dirty would lose writes to file-backed mappings. Holding and releasing the remote mmap lock follows `pin_user_pages_remote()`'s `locked` protocol.

## Test Signals
Useful tests include same-process and cross-process read/write, invalid flags, invalid local and remote iovecs, zero-length vectors, permission-denied targets, exited target tasks, remote unmapped pages mid-vector, partial transfers over multiple iovecs, writes to private anonymous memory, writes to shared file mappings with dirty propagation, large vectors that force kmalloc pointer storage, compat syscall coverage, and stress with concurrent unmap/mprotect in the target process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/process_vm_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ptdump.c -->
# sources/distributed-fs/ceph-client/mm/ptdump.c

## Purpose
`ptdump.c` implements the generic page-table walking glue used by architecture page-table dump facilities and the W+X mapping checker. It walks configured address ranges, reports each mapped or hole entry to callbacks stored in `struct ptdump_state`, includes KASAN shadow shortcuts, and creates a debugfs file that reports whether writable-executable mappings were found.

## Important APIs, Types, and Functions
The main exported function is `ptdump_walk_pgd(struct ptdump_state *st, struct mm_struct *mm, pgd_t *pgd)`. It uses a local `mm_walk_ops` table containing `ptdump_pgd_entry()`, `ptdump_p4d_entry()`, `ptdump_pud_entry()`, `ptdump_pmd_entry()`, `ptdump_pte_entry()`, and `ptdump_hole()`. Each page-table-level callback reads the entry, optionally updates effective protection state, reports leaf mappings through the matching `st->note_page_*` callback, and tells the walker to continue past leaf ranges.

When KASAN generic or software tag mode is enabled, `note_kasan_page_table()` recognizes page-table branches that point to early KASAN shadow tables and reports a synthetic PTE directly instead of walking the repeated shadow page tables. Debugfs integration is `check_wx_show()`, `DEFINE_SHOW_ATTRIBUTE(check_wx)`, and `ptdump_debugfs_init()`, which creates `/sys/kernel/debug/check_wx_pages`.

## Control Flow
`ptdump_walk_pgd()` takes the memory hotplug read side with `get_online_mems()`, write-locks the target mm mmap lock, iterates each `ptdump_range`, and calls `walk_page_range_debug()` with the supplied root PGD and private state. The walk callbacks translate table entries into `ptdump_state` notifications. Hole callbacks synthesize zero entries at the level where the hole is discovered. After all ranges, the function unlocks, drops the memory-hotplug guard, and calls `note_page_flush()` to emit the final accumulated range.

The debugfs show path runs `ptdump_check_wx()` and prints `SUCCESS` or `FAILED`, making the page-table dump infrastructure an executable security test surface as well as a diagnostic view.

## State and Persistence Behavior
This file owns no long-lived data beyond the registered debugfs file. Walk state is held in caller-provided `struct ptdump_state`, including range arrays, effective-protection callbacks, and note callbacks. The page tables are inspected but not modified. Locking around memory hotplug and the mmap write lock keeps walked page tables stable enough for debug traversal.

## Dependencies and Integration Points
The file depends on generic pagewalk APIs, debugfs, `linux/ptdump.h`, KASAN symbols, and architecture-provided page-table leaf and accessor predicates. It integrates with architecture ptdump implementations that define how to format ranges and derive effective permissions, and with kernel W+X validation through `ptdump_check_wx()`.

## Risks and Edge Cases
The KASAN optimization must recognize only the canonical early shadow tables; a false match would hide real mappings, while a miss can make debug walking very slow on large address spaces. Leaf detection must be correct at every folded/unfolded page-table level. Holding the mmap write lock during debug walks can be intrusive, especially on large page tables. The debugfs `SUCCESS`/`FAILED` output depends on architecture-specific `ptdump_check_wx()` correctness.

## Test Signals
Signals include boot with `CONFIG_DEBUG_WX`, reading `check_wx_pages`, architecture `kernel_page_tables` style debugfs output, KASAN-enabled page-table dumps that complete quickly, folded and five-level page-table builds, hugepage/leaf mapping formatting, hole reporting, and intentional W+X test mappings in debug kernels that flip the check result to failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/ptdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/readahead.c -->
# sources/distributed-fs/ceph-client/mm/readahead.c

## Purpose
`readahead.c` implements address-space-level file readahead for the Linux page cache. It predicts sequential access, preallocates locked cache folios, dispatches reads to filesystem `address_space_operations`, supports large folio readahead, exposes the `readahead(2)` syscall via `fadvise`, and lets filesystems expand readahead windows. For a distributed filesystem client such as Ceph, this generic code is the front-end that decides which file-cache folios should be fetched before userspace explicitly demands them.

## Important APIs, Types, and Functions
Public APIs include `file_ra_state_init()`, `page_cache_ra_unbounded()`, `force_page_cache_ra()`, `page_cache_ra_order()`, `page_cache_sync_ra()`, `page_cache_async_ra()`, `ksys_readahead()`, `SYSCALL_DEFINE3(readahead, ...)`, optional compat `readahead`, and `readahead_expand()`. Core local helpers are `read_pages()`, `ractl_alloc_folio()`, `do_page_cache_ra()`, `get_init_ra_size()`, `get_next_ra_size()`, `ra_alloc_folio()`, and `ractl_max_pages()`.

Important data structures are `struct file_ra_state`, which tracks the last readahead window (`start`, `size`, `async_size`, `ra_pages`, `prev_pos`, and folio order), `struct readahead_control`, which carries mapping/file/index/count/workingset/dropbehind state into filesystem callbacks, `struct address_space`, and folios in the mapping XArray.

## Control Flow
`file_ra_state_init()` seeds a file's maximum readahead pages from the backing device and sets `prev_pos` to `-1`. Readahead dispatch always prepares folios first and then calls `read_pages()`. `read_pages()` starts a block plug, enters PSI memstall accounting if any folio came from the workingset, invokes `a_ops->readahead()` when available, removes and unlocks any folios the filesystem did not consume, or falls back to `a_ops->read_folio()` one folio at a time.

`page_cache_ra_unbounded()` is the low-level unchecked path. Under the mapping invalidate lock, it aligns the start index to the mapping's minimum folio order, calculates which folio should carry the readahead flag, allocates folios with `readahead_gfp_mask()`, inserts them into the page cache, skips already-present folios by flushing the current batch, and finally submits the batch. `do_page_cache_ra()` bounds this by file size and acquires `mapping->invalidate_lock` around the unbounded path. `force_page_cache_ra()` is the simple path for random-mode files or disabled/congested readahead: it caps the request by readahead or optimal IO size and chunks reads into 2 MiB units.

`page_cache_sync_ra()` handles cache misses. It either forces a minimal read when readahead is disabled/congested, detects start-of-file, oversized, and sequential misses from `prev_pos`, or looks backward in the page cache to infer prior sequential history. It sets a new window and calls `page_cache_ra_order()`. `page_cache_async_ra()` handles a hit on a folio marked `PG_readahead`: it clears the marker, verifies the hit matches expected pipeline position or reconstructs state from the next cache miss, grows the window, increases preferred folio order, aligns the end, and dispatches. `page_cache_ra_order()` attempts large-folio allocation according to mapping capabilities and falls back to normal readahead if an insertion or allocation gap is hit.

The syscall path validates an fd is readable, has a mapping and address-space ops, refers to a regular or block file, and is not anonymous, then delegates to `vfs_fadvise(..., POSIX_FADV_WILLNEED)`. `readahead_expand()` lets a filesystem expand a prepared request before and after the current window by adding locked folios until it hits an existing page or allocation failure.

## State and Persistence Behavior
Persistent state lives in per-file `file_ra_state`, page-cache folios, and folio flags. Readahead can set `PG_readahead` on the async trigger folio and optional dropbehind state on newly allocated folios. It mutates the mapping XArray by adding locked folios and later relies on filesystem callbacks to unlock or remove them. It does not persist data to disk and ignores I/O errors at the readahead submission level; if a folio is not uptodate later, the synchronous read path retries with `read_folio()` and handles the error.

## Dependencies and Integration Points
Dependencies include the page cache, XArray, folios, backing-device readahead and IO-size parameters, block plugging, PSI memstall tracking, blk-cgroup congestion, file/inode mode checks, `vfs_fadvise()`, DAX configuration headers, and tracepoints in `trace/events/readahead.h`. Filesystems integrate through `mapping->a_ops->readahead()` and `read_folio()`, and may call `readahead_expand()` inside their own readahead implementation. Ceph-like distributed filesystems are expected to translate these folio batches into network object reads and unlock/remove folios according to success or temporary congestion.

## Risks and Edge Cases
Readahead intentionally tolerates partial failure. Filesystem `->readahead()` may ignore async-tail folios; VFS cleanup removes leftovers. Incorrect filesystem behavior, such as leaving failed folios locked or cached but not uptodate, can stall readers or degrade into inefficient per-folio reads. The window heuristic can be misled by interleaved readers or coincidental adjacent random reads. Large-folio readahead must align to mapping minimum and maximum orders and avoid EOF overrun. Readahead disabled or blk-cgroup congested paths still issue minimal synchronous readahead for demand satisfaction. The syscall returns `-EINVAL` for unsupported file types/mappings rather than silently doing nothing.

## Test Signals
Useful tests include sequential reads from start-of-file with growing windows, interleaved sequential readers, random reads with `FMODE_RANDOM`, blk-cgroup congestion, disabled readahead, files smaller than requested windows, EOF boundary reads, large-folio capable mappings, DAX or mappings without readahead support, filesystem `->readahead()` that consumes none/some/all folios, `read_folio()` fallback, `readahead_expand()` before/after windows, syscall validation for regular/block/anonymous files, compat syscall coverage, readahead tracepoints, and Ceph-client mmap/read workloads where remote fetch batching matches page-cache windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/rmap.c -->
# sources/distributed-fs/ceph-client/mm/rmap.c

## Purpose
`rmap.c` implements Linux reverse mapping: the ability to find virtual mappings from a physical folio or page. It maintains anonymous VMA linkage, mapcounts and mapped-page accounting, referenced/dirty/write-protect queries, unmapping for reclaim, migration-entry installation, device-exclusive page conversion, and generic reverse-map walks for anonymous and file-backed folios. For filesystem clients, the file-backed rmap path is essential for cleaning shared mappings, write-protecting mapped ranges, reclaiming page-cache folios, and invalidating mappings during truncation or migration.

## Important APIs, Types, and Functions
Anon-vma lifecycle APIs include `__anon_vma_prepare()`, `anon_vma_clone()`, `anon_vma_fork()`, `unlink_anon_vmas()`, `anon_vma_init()`, `folio_get_anon_vma()`, `folio_lock_anon_vma_read()`, and `__put_anon_vma()`. Important private structures are `struct anon_vma`, `struct anon_vma_chain`, anon-vma interval trees, and slab caches `anon_vma_cachep` and `anon_vma_chain_cachep`.

Referenced and cleaning APIs include `page_address_in_vma()`, `mm_find_pmd()`, `folio_referenced()`, `folio_mkclean()`, `mapping_wrprotect_range()`, and `pfn_mkclean_range()`. Rmap accounting APIs include `folio_add_anon_rmap_ptes()`, `folio_add_anon_rmap_pmd()`, `folio_add_new_anon_rmap()`, `folio_add_file_rmap_ptes()`, `folio_add_file_rmap_pmd()`, `folio_add_file_rmap_pud()`, `folio_remove_rmap_ptes()`, `folio_remove_rmap_pmd()`, `folio_remove_rmap_pud()`, and hugetlb anon-rmap helpers.

Unmap and migration APIs include `try_to_unmap()`, `try_to_migrate()`, optional TLB batch helpers `try_to_unmap_flush()`, `try_to_unmap_flush_dirty()`, `flush_tlb_batched_pending()`, and device-private `make_device_exclusive()`. The generic traversal entry points are `rmap_walk()` and `rmap_walk_locked()`, dispatching to KSM, anon, or file walkers.

## Control Flow
Anon-vma preparation attaches a VMA to an existing mergeable anon_vma or allocates a new root, then inserts an `anon_vma_chain` into both the VMA list and anon-vma interval tree under the required mmap, anon-vma, and page-table locks. Fork first clones the parent's anon-vma chains so parent mappings remain discoverable, then either reuses an inactive anon_vma in the hierarchy or creates a new child anon_vma where future COW pages will be indexed. Unlink removes a VMA from all anon-vma trees, updates active and child counts, and frees empty anon_vmas outside the write lock.

Referenced/cleaning flow walks every mapping of a folio. `folio_referenced()` locks or tries to lock the folio, walks reverse mappings, clears young/accessed state in PTEs or PMDs, integrates with MGLRU look-around, restores missed mlock state, and can bail out on anon-vma lock contention. `folio_mkclean()` and `mapping_wrprotect_range()` use page-table walks plus MMU notifier ranges to clear dirty/writeable bits for shared mappings and return the number of cleaned entries.

Rmap add/remove flow updates per-page mapcounts, large-folio mapcounts, whole-folio mapped counters, PMD/PUD mapped accounting, mlock state, and anon-exclusive flags. New anonymous folios set `folio->mapping` to the relevant anon_vma with the anon flag in one store and set `folio->index` from the VMA linear index. File rmap additions update file-mapped counters but do not attach anon metadata.

`try_to_unmap()` walks all mappings of a locked folio and clears PTEs/hugetlb entries. It respects mlock unless told to ignore it, handles PMD splitting, optional batched TLB flushing, dirty-bit capture, userfaultfd write-protect marker preservation, hwpoison entries, MADV_FREE discard, anonymous swap entry installation, swap exclusivity sharing, file RSS accounting, rmap removal, and reference drops. `try_to_migrate()` is similar but replaces mappings with migration entries that preserve writable, young, dirty, soft-dirty, uffd-wp, and anon-exclusive state. File and anon reverse walks use interval trees under `mapping->i_mmap_rwsem` or anon-vma root locks.

## State and Persistence Behavior
Persistent kernel memory state includes VMA anon-vma chains, anon-vma interval trees, page/folio mapping pointers and indices, per-page and per-folio mapcounts, `PageAnonExclusive`, large-folio mapcount metadata, mapped-page node/memcg counters, LRU/munlock state, dirty and referenced state, swap entries in PTEs, migration entries, hwpoison markers, and batched TLB flush generation counters. No data is stored on disk here, but write-protect and dirty-clean operations strongly affect when file-backed folios are considered clean enough for writeback, reclaim, migration, or truncation.

For file-backed mappings, the durable-data integration is indirect: rmap can mark folios dirty when unmapping writable PTEs, clear PTE dirty/write bits before writeback, and remove user mappings so later accesses fault through filesystem handlers. A distributed filesystem client relies on these transitions to prevent stale writable mappings and to coordinate cache invalidation with generic MM.

## Dependencies and Integration Points
The file depends on VMA interval trees, anon-vma locking, KSM, memcg, MMU notifiers, migration, hugetlb, THP, page-idle, userfaultfd, swap, mlock, page table walkers, TLB/cache flush primitives, MGLRU, device-private memory, and filesystem `address_space->i_mmap` trees. File-backed integration is through `struct address_space`, `mapping->i_mmap`, dirty/write-protect paths, and rmap walks used by reclaim, writeback, migration, truncation, and memory failure.

## Risks and Edge Cases
Lock ordering is critical and documented at the top of the file. Regressions can deadlock across inode, mmap, invalidate, folio, i_mmap, anon_vma, page-table, swap, and LRU locks. Anon-vma lifetime is RCU-sensitive because lockless readers can observe `folio->mapping` while anon_vmas are freed and reused. Large folio mapcount math must handle PTE-mapped partial folios, PMD/PUD whole mappings, deferred splitting, and `CONFIG_NO_PAGE_MAPCOUNT`. TLB batching must flush dirty writable translations before writeback or freeing to avoid lost writes or data leakage. Userfaultfd markers, soft-dirty bits, anon-exclusive bits, device-private/exclusive entries, hwpoison, hugetlb PMD sharing, and temporary exec stacks all require special handling.

## Test Signals
Validation should include fork/COW and anon-vma reuse tests, VMA split/merge/remap/fork operations, KSM mappings, folio referenced/idle aging, MGLRU, mlock reclaim, shared-file `folio_mkclean()` before writeback, `mapping_wrprotect_range()` for PFN mappings, reclaim `try_to_unmap()` with swap and MADV_FREE, migration with THP split and migration entries, hugetlb hwpoison/migration paths, device-exclusive conversion and CPU fault restore, userfaultfd write-protect preservation, soft-dirty preservation, memcg mapped counters, lockdep under concurrent truncate/reclaim/fault/writeback, and filesystem mmap workloads on Ceph-like clients racing remote invalidation with local shared writable mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/rodata_test.c -->
# sources/distributed-fs/ceph-client/mm/rodata_test.c

## Purpose
`rodata_test.c` is a small functional test for kernel read-only data protection. It verifies that a `static const` variable in `.rodata` can be read, cannot be modified through a nofault kernel write helper, remains unchanged after the attempted write, and that the `.rodata` section boundaries are page-aligned.

## Important APIs, Types, and Functions
The file defines `TEST_VALUE`, a `static const int rodata_test_data`, and one function, `rodata_test()`. It uses `READ_ONCE()` to verify the value, `copy_to_kernel_nofault()` to attempt a write that should fault/fail cleanly, `PAGE_ALIGNED()` to check `__start_rodata` and `__end_rodata`, and `pr_err()`/`pr_info()` for result reporting.

## Control Flow
`rodata_test()` runs four checks in sequence. First it verifies the initial constant value. Second it attempts to write zero into the const object and treats a successful copy as failure because `.rodata` should be read-only. Third it reads the object again to ensure it was not changed. Fourth it checks start and end rodata section alignment. The function returns early on any failure and logs success only after all checks pass.

## State and Persistence Behavior
The intended behavior is no state mutation. The attempted write is expected to fail without changing `rodata_test_data`. The only persistent effect is kernel log output. A failed protection setup could corrupt the test variable, and the first and third checks are designed to catch that corruption.

## Dependencies and Integration Points
The file depends on rodata test declarations, uaccess nofault copying, MM page alignment macros, and architecture section symbols from `asm/sections.h`. It integrates with architecture or core init code that calls `rodata_test()` after read-only permissions are applied to kernel text/rodata mappings.

## Risks and Edge Cases
The test is meaningful only after page permissions for rodata have been finalized. If called too early, it can falsely report writable rodata. `copy_to_kernel_nofault()` must fail safely without panicking on a protected kernel address. Section boundary checks assume the architecture exposes accurate `__start_rodata` and `__end_rodata` symbols and requires page-aligned rodata protection.

## Test Signals
The expected signal is one `all tests were successful` log line during boot/test execution. Failure logs identify initial data corruption, writable rodata, post-write corruption, or unaligned rodata boundaries. Architecture bring-up and debug kernels should run this alongside W+X and strict kernel RWX tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/rodata_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/secretmem.c -->
# sources/distributed-fs/ceph-client/mm/secretmem.c

## Purpose
`secretmem.c` implements the `memfd_secret(2)` backing filesystem and file operations. Secret memory creates anonymous file descriptors whose mappings allocate pages removed from the kernel direct map, locked into memory, excluded from core dumps, unevictable, non-migratable, and zeroed/restored to the direct map when freed. It is generic security-sensitive MM infrastructure, not Ceph-specific.

## Important APIs, Types, and Functions
The syscall entry is `SYSCALL_DEFINE1(memfd_secret, unsigned int, flags)`. Public helper `secretmem_active()` reports whether any secretmem users exist, and `vma_is_secretmem()` identifies VMAs using `secretmem_vm_ops`. Fault handling is in `secretmem_fault()`. File and mapping hooks include `secretmem_release()`, `secretmem_mmap_prepare()`, `secretmem_fops`, `secretmem_aops`, `secretmem_migrate_folio()`, `secretmem_free_folio()`, `secretmem_setattr()`, and `secretmem_iops`.

Filesystem setup is handled by `secretmem_init_fs_context()`, `secretmem_fs`, and `secretmem_init()`, which mounts a pseudo filesystem into `secretmem_mnt`. `secretmem_file_create()` creates the secure anonymous inode and pseudo file. Important globals are `secretmem_enable`, a read-only module parameter, `secretmem_users`, and `secretmem_mnt`.

## Control Flow
At init, `secretmem_init()` checks the enable flag and `can_set_direct_map()`, then mounts the pseudo filesystem. The syscall rejects unsupported systems with `-ENOSYS`, rejects unknown flags, checks the user counter, and returns an fd from `secretmem_file_create()` with optional `O_CLOEXEC`. File creation allocates a secure anonymous inode, creates a pseudo file with secretmem fops, sets high-user GFP mask and unevictable mapping state, installs inode and address-space ops, marks the inode as regular with size zero, and increments `secretmem_users`.

Mapping requires shared semantics. `secretmem_mmap_prepare()` rejects mappings that are not shared/may-share, sets `VM_LOCKED` and `VM_DONTDUMP`, checks `mlock_future_ok()`, and installs the fault ops. On a page fault, `secretmem_fault()` rejects offsets beyond file size, takes the mapping invalidate lock shared, looks for an existing locked folio, or allocates a zeroed order-0 folio. New folios are removed from the direct map with `set_direct_map_invalid_noflush()`, marked uptodate, inserted into the filemap, and followed by a kernel TLB flush for the folio address. The fault returns the locked file page.

When a secretmem folio is freed, `secretmem_free_folio()` restores the default direct-map permissions and zeroes the folio contents. Migration is refused with `-EBUSY`. Truncation via setattr is allowed only while the inode size is zero; resizing a non-empty secretmem file returns `-EINVAL` under the invalidate lock. File release decrements the active user count.

## State and Persistence Behavior
State is in memory only. Secretmem files are pseudo files with page-cache folios, but the folios are unevictable and not backed by disk. The important persistence contract is negative: data should not remain accessible through the kernel direct map, should not be migrated or swapped, should not be dumped, and should be zeroed before being returned to normal memory. The user count lets other code observe whether secretmem is active.

## Dependencies and Integration Points
Dependencies include memfd/syscall infrastructure, pseudo filesystems, secure anonymous inode creation, page cache and filemap locks, `set_direct_map_invalid_noflush()`/`set_direct_map_default_noflush()`, TLB flushing, mlock accounting, unevictable mapping state, and simple inode setattr. It integrates with VMA setup through `.mmap_prepare`, with fault handling through `vm_operations_struct`, and with generic reclaim/migration through address-space operations that make secretmem dirty handling a no-op and migration impossible.

## Risks and Edge Cases
Security depends on direct-map manipulation succeeding and being paired on free. Failure after invalidating the direct map but before inserting into the filemap must restore default mapping. Existing folios found by `filemap_lock_folio()` are reused; racing insertion handles `-EEXIST` by retrying. The mapping must be shared and mlock limits must be enforced, otherwise users could create secret memory outside the intended accounting model. Size handling is restrictive: faults beyond `i_size` fail, and resizing after size is nonzero is rejected. Architectures without direct-map control disable the syscall.

## Test Signals
Tests should cover syscall disabled by module parameter or missing direct-map support, invalid flags, `O_CLOEXEC`, mmap mode rejection for private mappings, mlock-limit failure, ftruncate/setattr behavior before and after sizing, first fault allocation and repeated fault reuse, direct-map access prevention where testable, folio zeroing on free, migration refusal, core-dump exclusion, unevictable accounting, user count changes through open/release, and stress with concurrent faults and truncation/invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/secretmem.c -->
