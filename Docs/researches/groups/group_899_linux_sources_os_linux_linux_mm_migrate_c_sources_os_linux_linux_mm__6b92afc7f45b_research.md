# Group Research: group_899_linux_sources_os_linux_linux_mm_migrate_c_sources_os_linux_linux_mm__6b92afc7f45b

Scope: `Docs/research_subset_a.md`

This grouped report covers Linux MM files centered on page migration, device memory migration, residency reporting, memory locking, boot-time memory initialization, and the small `mm_slot` helper. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/migrate.c -->
# File Research: sources/os/linux/linux/mm/migrate.c

## Role

`migrate.c` is the core Linux folio/page migration implementation. It supplies common migration primitives used by compaction, memory hotplug/offlining, NUMA policy and balancing, memory failure handling, hugetlb migration, filesystem/page-cache migration callbacks, and userspace `move_pages(2)`.

## Main Responsibilities

- Registers and dispatches `movable_operations` for special movable pages such as offline balloon pages and zsmalloc pages.
- Isolates pages/folios from LRU, hugetlb lists, or movable-ops owners, and returns them via `putback_movable_pages()`.
- Converts mapped PTEs/PMDs to migration entries, waits on migration entries, and restores mappings with `remove_migration_ptes()`.
- Moves folio metadata and content from source to destination folios, including address-space xarray entries, swap cache state, dirty/writeback/accounting state, memcg ownership, KSM metadata, NUMA cpupid metadata, and page owner data.
- Implements batched and retrying migration loops through `migrate_pages()`.
- Implements `move_pages(2)` when `CONFIG_NUMA_MIGRATION` is enabled.
- Implements NUMA balancing migration helpers when `CONFIG_NUMA_BALANCING` is enabled.

## Key Entry Points

- `set_movable_ops()`: installs per-page-type movable callbacks for `PGTY_offline` and `PGTY_zsmalloc`.
- `isolate_movable_ops_page()`: pins, locks, callback-isolates, and marks a movable-ops page as isolated.
- `putback_movable_pages()`: generic cleanup for isolated LRU, hugetlb, and movable-ops pages.
- `remove_migration_ptes()`: walks reverse mappings and replaces migration entries with either the migrated destination page or the original source page.
- `migration_entry_wait()`, `migration_entry_wait_huge()`, `pmd_migration_entry_wait()`: fault-side wait helpers for PTE/hugetlb/PMD migration entries.
- `folio_migrate_mapping()`: atomically replaces a folio in its mapping or swap cache after refcount freezing.
- `folio_migrate_flags()`: transfers ancillary state after mapping replacement.
- `migrate_folio()`, `filemap_migrate_folio()`, `buffer_migrate_folio()`, `buffer_migrate_folio_norefs()`: exported migration callbacks for generic folios, page cache, and buffer-head users.
- `migrate_pages()`: public high-level migrator for lists of isolated folios.
- `alloc_migration_target()`: default destination allocation helper controlled by `struct migration_target_control`.
- `SYSCALL_DEFINE6(move_pages, ...)`: userspace NUMA page move/status syscall.
- `migrate_misplaced_folio_prepare()` and `migrate_misplaced_folio()`: NUMA fault migration helpers.

## Migration Pipeline

The ordinary non-hugetlb path is split into unmap and move phases:

1. `migrate_folio_unmap()` allocates a destination folio, locks source and destination, waits for writeback only when migration mode permits, obtains an `anon_vma` reference when needed, and installs migration PTEs via `try_to_migrate()`.
2. It records transient state in the destination folio private field: whether the source was mapped, whether it was mlocked, and the borrowed `anon_vma`.
3. `migrate_folio_move()` extracts that state, removes the destination from the temporary list, calls `move_to_new_folio()`, requeues deferred split state when needed, puts the destination on LRU, restores PTEs to destination, unlocks both folios, and drops migration references.
4. Failure paths call `migrate_folio_undo_src()` and `migrate_folio_undo_dst()` to restore migration PTEs, unlock folios, release destination allocation, and move failed folios to the caller’s return list unless retrying.

`migrate_pages_batch()` performs the same logic in batches for `MIGRATE_ASYNC`, first collecting unmapped folios and destination folios, then flushing TLBs once via `try_to_unmap_flush()`, then moving the batch. Synchronous migration first tries the async batch path and then falls back to one-by-one migration for failures.

## Mapping and Accounting Details

`__folio_migrate_mapping()` is the central atomic replacement routine. It freezes the source folio refcount at the expected value, unqueues deferred split state, copies index/mapping/swapcache/private state, moves dirty state, replaces xarray or swap-cache entries, unfreezes the source with the cache reference removed, and updates zone/lruvec counters when source and destination zones differ.

`folio_migrate_flags()` copies state that is not handled by mapping replacement: referenced, uptodate, active/unevictable, workingset, checked, mapped-to-disk, dirty fallback, young/idle, ref metadata, NUMA cpupid, KSM, swapcache clearing, private clearing, writeback waiter wakeup, readahead, owner metadata, allocation tags, and memcg migration.

## Special Page Classes

- Movable-ops pages are not ordinary LRU pages. Their owner callback handles isolate, putback, and migrate. The migration core still temporarily treats them as folios and locks/refcounts them.
- Hugetlb migration uses `unmap_and_move_huge_page()` with hugetlb-specific locking, rmap handling, and `move_hugetlb_state()`.
- THP/large folios may be migrated as large folios, split when migration is unsupported or allocation fails, or counted specially in migration statistics.
- Device-private pages can be restored through migration-entry handling in `remove_migration_pte()`, but device-specific collection/migration lives in `migrate_device.c`.

## Userspace and NUMA Interfaces

With `CONFIG_NUMA_MIGRATION`, `move_pages(2)` resolves user addresses to folios, validates target nodes against cpuset and memory-node availability, enforces `MPOL_MF_MOVE_ALL` privilege, isolates eligible folios, migrates by target node batches, and writes per-page status back to userspace.

With `CONFIG_NUMA_BALANCING`, misplaced folio migration avoids dirty file folios, shared executable mappings, and target nodes below watermarks. Tiering mode can wake kswapd and tracks promotion success in lruvec stats.

## Concurrency and Failure Model

This file is heavily built around refcount freezing, folio locks, rmap locks, page-table locks, xarray/swap-cluster locks, mmap/rmap coordination, and TLB flush batching. Retryable failures generally use `-EAGAIN`; permanent failures move folios to return lists; low-memory allocation failure can short-circuit the batch with `-ENOMEM`. The caller must put back remaining isolated folios when `migrate_pages()` reports nonzero/negative results.

## Filesystem Relevance

Filesystem address spaces participate through `address_space_operations::migrate_folio`. If a filesystem does not provide a callback, `fallback_migrate_folio()` refuses dirty folios and requires private data release before using generic migration. Buffer-head filesystems can use `buffer_migrate_folio()` when buffer references are controlled by the folio lock, or `buffer_migrate_folio_norefs()` when direct buffer-head references must be checked.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/migrate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/migrate_device.c -->
# File Research: sources/os/linux/linux/mm/migrate_device.c

## Role

`migrate_device.c` implements HMM/ZONE_DEVICE migration between CPU-addressable system memory and device private/coherent memory. It exposes the `migrate_vma_*` API for drivers that migrate a virtual address range, plus PFN-range helpers for migrating device memory back to normal memory without walking a VMA.

## Main Responsibilities

- Walk CPU page tables for a VMA range and collect source PFNs into `migrate->src`.
- Replace CPU PTEs/PMDs with migration entries while pages are locked and pinned.
- Support anonymous holes so drivers can populate device memory for previously unallocated anonymous addresses.
- Support device-private and device-coherent page selection by `pgmap_owner`.
- Coordinate invalidation through MMU notifiers before and after page table collection/insertion.
- Move struct-page metadata from source to destination pages with the generic migration helpers in `migrate.c`.
- Finalize migration by restoring CPU mappings to the destination or source pages and releasing locks/references.

## Key Entry Points

- `migrate_vma_setup()`: validates `struct migrate_vma`, clears arrays, walks page tables, collects candidates, and unmaps migratable pages.
- `migrate_vma_pages()`: migrates source struct-page metadata to destination pages supplied by the driver.
- `migrate_vma_finalize()`: restores CPU page tables and unlocks/puts source and destination folios.
- `migrate_device_pages()`: metadata migration for pre-collected device PFN arrays.
- `migrate_device_finalize()`: finalization for `migrate_device_pages()`.
- `migrate_device_range()`: prepares a contiguous device PFN range for migration to system memory.
- `migrate_device_pfns()`: prepares a non-contiguous pre-populated device PFN array.
- `migrate_device_coherent_folio()`: migrates a single device-coherent folio back to normal memory.

## VMA Range Collection

`migrate_vma_collect()` wraps the page-table walk in `MMU_NOTIFY_MIGRATE` invalidation. The walk callbacks record one source entry per page-sized slot. `migrate_vma_collect_hole()` marks anonymous holes as migratable and optionally marks PMD-sized compound holes. `migrate_vma_collect_pmd()` handles ordinary PTEs, device-private swap entries, device-coherent pages, zero pages, and large folio splitting. It installs migration entries immediately when it can lock the folio, preserving write, young, dirty, soft-dirty, uffd-wp, and anon-exclusive state.

For PMD-mapped THPs, `migrate_vma_collect_huge_pmd()` can collect and replace the whole PMD with a migration entry when `MIGRATE_VMA_SELECT_COMPOUND` is requested and alignment permits. Otherwise it falls back to splitting.

## Unmap and Pin Checks

`migrate_device_unmap()` isolates non-device folios from the LRU, uses `try_to_migrate()` for still-mapped folios, and rejects pages that remain mapped or appear pinned. `migrate_vma_check_page()` applies a refcount-vs-mapcount heuristic similar to generic migration but accounts for the caller’s extra reference and ZONE_DEVICE extra references. Rejected pages have migration entries restored and are unlocked/put.

## Metadata Migration

`__migrate_device_pages()` iterates `src_pfns` and `dst_pfns`:

- If the source is a hole and destination is valid, it inserts a new anonymous page or device-private entry through `migrate_vma_insert_page()`.
- If compound source/destination support mismatches, it either splits an unmapped source folio or cancels migration.
- It only allows migration to device private/coherent memory for anonymous memory; swap cache may be freed first with `folio_free_swap()`.
- It rejects unsupported ZONE_DEVICE destination types.
- It uses `folio_migrate_mapping()` and `folio_migrate_flags()` for the actual metadata move.

The driver remains responsible for allocating destination pages, copying contents, marking destination entries valid, and ensuring copy completion before finalization.

## Page Table Insertion

`migrate_vma_insert_page()` mirrors anonymous fault insertion logic for device or normal destination pages. It allocates page tables, prepares anon-vma, charges memcg, marks the folio uptodate, builds either a device-private swap PTE or normal PTE, handles zero-page replacement, checks stable address space and userfaultfd-missing state, adds anonymous rmap, optionally adds the folio to LRU, and installs the PTE.

When THP migration is enabled, `migrate_vma_insert_huge_pmd_page()` performs analogous PMD insertion, including memcg charge, pgtable deposit, huge PMD entry construction, rmap setup, zero PMD replacement, and THP fault accounting.

## Finalization

`__migrate_device_finalize()` walks all entries and chooses destination if migration succeeded, otherwise source. Non-device destinations are added back to LRU. It calls `remove_migration_ptes()` to restore CPU mappings and releases locks/references, preserving a supplied fault folio lock when required.

## Concurrency and Driver Contract

The API assumes the caller holds `mmap_lock` appropriately via the VMA context and that destination pages are locked. MMU notifier invalidation tells devices that CPU mappings are being migrated; `pgmap_owner` lets a driver avoid invalidating its own pages unnecessarily. Migration is best-effort except device-to-system fault recovery paths, where failure can propagate to severe userspace faults if the driver cannot bring device-private memory back.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/migrate_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mincore.c -->
# File Research: sources/os/linux/linux/mm/mincore.c

## Role

`mincore.c` implements the `mincore(2)` system call, reporting whether pages in a process virtual address range are resident enough that access would not require page-in I/O at the time of inspection.

## Main Responsibilities

- Validate user arguments for alignment, address range access, and output vector access.
- Walk VMAs page-table-by-page-table and fill a byte vector with residency bits.
- Check page cache residency for unmapped file-backed ranges.
- Handle shmem swap-cache entries, regular swap entries, migration entries, hwpoison-like non-swap entries, THPs, and hugetlb mappings.
- Restrict file-backed page-cache disclosure to avoid side-channel leakage.

## Key Entry Points

- `SYSCALL_DEFINE3(mincore, ...)`: syscall wrapper, temporary page-sized vector allocation, chunked walk/copy loop.
- `do_mincore()`: resolves the VMA, applies `can_do_mincore()`, and walks the requested subrange.
- `mincore_pte_range()`: PMD/PTE walker for normal mappings.
- `mincore_unmapped_range()` and `__mincore_unmapped_range()`: page-cache lookup for unmapped file-backed areas or zero fill for anonymous gaps.
- `mincore_hugetlb()`: hugepage-specific walker.
- `mincore_page()`: page-cache/xarray residency lookup.
- `mincore_swap()`: swap-cache residency lookup.

## Residency Semantics

Present PTEs and PMD-mapped THPs are reported resident. PTE holes in file VMAs are checked against the backing mapping at the corresponding file offset; holes in anonymous VMAs are reported not resident. Page-cache entries are resident only if they refer to an uptodate folio. Xarray value entries in shmem mappings are interpreted as swap entries and checked via swap cache.

Non-swap special entries in page tables, such as migration or hwpoison entries, are treated as resident for non-shmem PTE checks. Hugetlb mappings are reported resident unless the huge PTE is none or a marker.

## Security Gate

`can_do_mincore()` allows anonymous VMAs and file mappings whose inode owner/capability check or write permission check would permit page-cache disclosure. For disallowed non-anonymous file-backed mappings, `do_mincore()` fills the result range with resident bits rather than exposing real cache state.

## Concurrency

The syscall holds `mmap_read_lock()` per chunk and the page-table walker uses `PGWALK_RDLOCK`. PTE reads happen under page-table locks. Shmem swap lookups grab the swap device around `swap_cache_get_folio()` because the mapping lookup is lockless.

## Error Handling

Invalid alignment returns `-EINVAL`; invalid address range access returns `-ENOMEM`; invalid output vector access returns `-EFAULT`; temporary buffer allocation failure returns `-EAGAIN`; missing VMAs during the walk return `-ENOMEM`. Results may become stale immediately after return unless the caller has locked memory.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mincore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mlock.c -->
# File Research: sources/os/linux/linux/mm/mlock.c

## Role

`mlock.c` implements memory locking and unlocking: `mlock(2)`, `mlock2(2)`, `munlock(2)`, `mlockall(2)`, `munlockall(2)`, folio-level mlock/munlock helpers, and System V shared-memory lock accounting. Its job is to keep selected user pages unevictable while respecting resource limits and capability checks.

## Main Responsibilities

- Enforce `RLIMIT_MEMLOCK` and `CAP_IPC_LOCK`.
- Maintain `VM_LOCKED` and `VM_LOCKONFAULT` VMA flags.
- Walk existing mappings to mark or unmark resident folios.
- Move folios between evictable and unevictable LRU state with approximate `mlock_count` tracking.
- Batch LRU operations per CPU to reduce lock churn.
- Account locked pages in `mm->locked_vm`, `NR_MLOCK`, unevictable VM events, and user shared-memory ucounts.

## Key Entry Points

- `can_do_mlock()`: shared permission check.
- `mlock_folio()`: mark an existing LRU folio mlocked and enqueue it for unevictable handling.
- `mlock_new_folio()`: mark a newly allocated folio mlocked before it enters LRU.
- `munlock_folio()`: enqueue folio unlock processing.
- `mlock_drain_local()`, `mlock_drain_remote()`, `need_mlock_drain()`: drain per-CPU mlock batches.
- `SYSCALL_DEFINE2(mlock, ...)`, `SYSCALL_DEFINE3(mlock2, ...)`, `SYSCALL_DEFINE2(munlock, ...)`: range locking syscalls.
- `SYSCALL_DEFINE1(mlockall, ...)`, `SYSCALL_DEFINE0(munlockall)`: process-wide locking syscalls.
- `user_shm_lock()` and `user_shm_unlock()`: shared-memory lock accounting against `ucounts`.

## Folio Batch Design

`struct mlock_fbatch` stores a per-CPU `folio_batch` protected by a local lock. Low pointer bits distinguish three queued operations: mlock an existing LRU folio, mlock a new non-LRU folio, or munlock. `mlock_folio_batch()` decodes each entry, relocks the appropriate lruvec, performs LRU state changes, unlocks once at the end, and drops folio references.

This batching is important because mlock state can be updated from fault, migration, and syscall paths while avoiding excessive LRU lock traffic.

## LRU and Unevictable Logic

`__mlock_folio()` clears the LRU bit, relocks the folio’s lruvec, and moves non-evictable folios to unevictable state. If the folio is already unevictable and still mlocked, it increments `mlock_count`. `__munlock_folio()` decrements `mlock_count`, clears `PG_mlocked` when appropriate, updates `NR_MLOCK`, and rescues folios back to evictable LRU when `folio_evictable()` becomes true.

The code intentionally treats `mlock_count` as approximate in some races; reclaim can correct stranded unevictable folios.

## VMA Flag Transitions

`apply_vma_lock_flags()` iterates a target address range, verifies contiguous VMA coverage, computes new lock flags, and calls `mlock_fixup()` for each VMA segment. `mlock_fixup()` filters unsupported VMAs, performs VMA split/merge flag modifications, updates `mm->locked_vm`, and calls `mlock_vma_pages_range()` unless the range was already locked.

`mlock_vma_pages_range()` temporarily combines `VM_LOCKED` with `VM_IO` in the new flags to signal rmap walkers and avoid double-counting during concurrent migration/reclaim interactions, then walks PTEs with `PGWALK_WRLOCK_VERIFY`.

## Syscall Semantics

`do_mlock()` aligns the range, checks permissions, adjusts for already locked pages when testing limits, applies VMA flags under `mmap_write_lock`, then populates pages with `__mm_populate()` unless `MLOCK_ONFAULT` deferred locking was requested. `mlockall()` updates `mm->def_flags` for future mappings and optionally applies flags to current VMAs; `munlockall()` clears process-wide lock flags.

## Special Cases

Secretmem VMAs cannot be unlocked through this path. Zone-device pages and huge zero PMDs are skipped by the page walker. Large folios are only mlocked when the mapped range fully covers the folio; munlock is allowed on partially mapped large folios so later reclaim/splitting can recover pages no longer protected by `VM_LOCKED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mm_init.c -->
# File Research: sources/os/linux/linux/mm/mm_init.c

## Role

`mm_init.c` coordinates early and late MM subsystem initialization. It verifies memory-init layout, parses memory-zone boot parameters, constructs zones/nodes, initializes `struct page` arrays, supports deferred struct-page initialization, initializes ZONE_DEVICE metadata, configures debug/hardening static keys, reports memory layout, and runs the main allocator/MM bootstrap sequence.

## Main Responsibilities

- Define global memory symbols such as `high_memory`, `zero_page_pfn`, and non-NUMA `mem_map`/`max_mapnr`.
- Create `/sys/kernel/mm`.
- Parse `kernelcore=`, `movablecore=`, `mminit_loglevel=`, `hashdist=`, `init_on_alloc=`, `init_on_free=`, and `check_pages=`.
- Determine zone PFN bounds, movable-zone placement, absent pages, and per-node totals.
- Initialize pgdat, zone internals, free lists, pageblock migratetypes, and flatmem memmaps.
- Initialize unavailable ranges as reserved pages so holes have safe `struct page` state.
- Initialize ZONE_DEVICE pages and compound device-page metadata.
- Defer initialization of high memory ranges when configured, then complete it in parallel later.
- Allocate large system hash tables during boot.
- Enable memory debugging/hardening static branches.
- Run `mm_core_init_early()`, `mm_core_init()`, and `page_alloc_init_late()` bootstrap phases.

## Zone and Node Initialization

`free_area_init()` obtains architecture zone limits, initializes sparsemem, computes possible zone ranges, finds per-node ZONE_MOVABLE start PFNs, prints early memory ranges, initializes node IDs and pageblock order, then calls `free_area_init_node()` for each node. `free_area_init_node()` computes a node PFN range, calculates zone totals, allocates flatmem node maps when needed, configures deferred ranges, initializes zone internals, and initializes LRU-generation pgdat state.

`find_zone_movable_pfns_for_nodes()` is the main policy routine for ZONE_MOVABLE placement. It handles `movable_node`, `kernelcore=mirror`, percentage and absolute `kernelcore`/`movablecore`, even distribution of kernelcore across usable nodes, and MAX_ORDER alignment.

`calculate_node_totalpages()` computes spanned and present pages per zone using `zone_spanned_pages_in_node()` and `zone_absent_pages_in_node()`, with special mirrored-memory handling where mirrored/unmirrored pages are treated as absent from the opposite zone.

## Struct Page Initialization

`__init_single_page()` zeroes and initializes a `struct page`, sets zone/node/pfn links, initializes refcount/mapcount/cpupid/KASAN tag/list state, and optionally sets direct virtual address metadata. `memmap_init_range()` initializes a PFN range for early boot, hotplug, or ZONE_DEVICE contexts, sets offline/reserved state where appropriate, initializes pageblock migratetype, and supports vmem altmap reservations.

`memmap_init()` walks memblock ranges by node and zone, initializes valid memory ranges, and explicitly initializes holes/trailing sections via `init_unavailable_range()` as reserved pages. This prevents later `struct page` users from observing uninitialized metadata for PFNs inside memmap coverage but outside actual RAM.

## Deferred Initialization

When `CONFIG_DEFERRED_STRUCT_PAGE_INIT` is enabled, high-zone struct-page initialization can stop after an initial section. `defer_init()` records `pgdat->first_deferred_pfn`; `deferred_grow_zone()` can initialize/free section-sized chunks on demand during early allocation; `page_alloc_init_late()` starts per-node `deferred_init_memmap` kernel threads and waits for completion. Deferred chunks initialize pages and free them to the buddy allocator, using larger naturally aligned frees when possible.

## ZONE_DEVICE Support

`memmap_init_zone_device()` initializes device memory pages after hotplug section activation. It handles altmap offsets, pgmap back-pointers, reserved state, pageblock migratetype, device-specific refcount initialization, and compound-page metadata when `pgmap->vmemmap_shift` groups PFNs. Supported pgmap types include FS DAX, private, coherent, PCI P2PDMA, and generic device memory.

## Boot Phases

- `mm_core_init_early()` reserves hugetlb CMA/bootmem and initializes zones via `free_area_init()`.
- `mm_core_init()` performs architecture preinit, zero-page setup, zonelist construction, CPU hotplug allocator setup, allocation tags, page-ext flatmem setup, debugging/hardening setup, KFENCE metadata allocation, meminit reporting, KMSAN setup, stack depot setup, KHO memory init, memblock release to buddy, slab initialization, kmemleak/page-table/vmalloc/debug-object setup, espfix/PTI, runtime KMSAN, MM cache init, and executable memory init.
- `page_alloc_init_late()` completes deferred page init, initializes buffer heads, discards memblock metadata, shuffles free memory, marks contiguous zones, initializes page extensions if deferred, and installs page-allocation sysctls.

## Debugging and Hardening

`mem_debugging_and_hardening_init()` coordinates page poisoning, debug pagealloc, guard pages, init-on-alloc, init-on-free, and page sanity checking static branches. Page poisoning takes precedence over heap auto-initialization. `report_meminit()` reports stack and heap initialization state; `mem_init_print_info()` prints available/reserved/CMA/highmem and kernel section sizes after accounting stabilizes.

## Utility Exports

`get_pfn_range_for_nid()`, `absent_pages_in_range()`, `node_map_pfn_alignment()`, `set_zone_contiguous()`, `pfn_range_intersects_zones()`, `memmap_alloc()`, `alloc_large_system_hash()`, and `memblock_free_pages()` are reusable helpers for architecture, hotplug, allocator, and subsystem initialization code.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mm_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mm_slot.h -->
# File Research: sources/os/linux/linux/mm/mm_slot.h

## Role

`mm_slot.h` defines a tiny reusable helper abstraction for subsystems that need to associate per-`mm_struct` state with both a hash table and a list.

## Main Contents

- `struct mm_slot`: contains a hash node, a list node, and the `struct mm_struct *mm` key.
- `mm_slot_entry(ptr, type, member)`: container helper for embedding `struct mm_slot` inside a larger subsystem-specific object.
- `mm_slot_alloc()`: allocates zeroed slot objects from a supplied `kmem_cache`, returning `NULL` if cache initialization failed.
- `mm_slot_free()`: frees an object to the supplied cache.
- `mm_slot_lookup()`: macro that searches a hash table bucket keyed by the `mm_struct` pointer value.
- `mm_slot_insert()`: macro that stores the `mm` key and adds the slot to the hash table.

## Design Notes

The header deliberately does not own locking. Callers must serialize hash/list access according to their subsystem rules. It also does not manage mm lifetime; users must hold appropriate references or otherwise guarantee that pointer-keyed lookup remains valid.

## Filesystem/MM Relevance

The helper is useful for MM subsystems such as KSM-style scanners that track process address spaces in a global list while also needing fast lookup by `mm_struct`. It keeps the common allocation, lookup, and insertion pattern local without imposing policy.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mm_slot.h -->