# Research: subset-b-006138

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/migrate.c -->
# sources/distributed-fs/ceph-client/mm/migrate.c

## Purpose
Implements the core Linux folio/page migration engine for the Ceph client kernel tree. It supports memory compaction, memory hot-remove/offline, huge page migration, NUMA `move_pages(2)`, automatic NUMA balancing, memory tiering demotion/promotion, KSM/anonymous/file-backed folios, swapcache folios, and driver-owned "movable_ops" pages such as balloon/offline and zsmalloc pages. The file is the central coordinator that isolates source folios, installs migration entries into page tables, allocates destination folios through caller callbacks, moves address-space metadata and folio flags, restores mappings, updates VM accounting, and reports migration statistics.

## Important APIs, Types, and Functions
Primary exported APIs include `set_movable_ops()`, `putback_movable_pages()`, `isolate_folio_to_list()`, `remove_migration_ptes()`, `migration_entry_wait()`, `folio_migrate_mapping()`, `migrate_huge_page_move_mapping()`, `folio_migrate_flags()`, `migrate_folio()`, `buffer_migrate_folio()`, `buffer_migrate_folio_norefs()`, `filemap_migrate_folio()`, `migrate_pages()`, and `alloc_migration_target()`. NUMA-specific exports under configuration include `move_pages(2)`, `migrate_misplaced_folio_prepare()`, and `migrate_misplaced_folio()`.

Key local structures and helpers are `struct rmap_walk_arg`, which controls migration-entry restoration and optional zeropage remapping; `struct migrate_pages_stats`, which accumulates base-page and THP success/failure/split counts; the `PAGE_WAS_MAPPED` and `PAGE_WAS_MLOCKED` state bits packed into destination folio private storage during two-phase migration; and the `movable_operations` dispatch selected by `page_movable_ops()` for non-LRU driver pages.

## Control Flow
Generic migration is split into unmap and move phases. Callers build a list of isolated folios, then `migrate_pages()` first handles hugetlb folios through `migrate_hugetlbs()`, batches normal folios up to `NR_MAX_BATCHED_MIGRATION`, and chooses either async batching or sync retry fallback. `migrate_folio_unmap()` allocates and locks a destination folio, locks the source according to migration mode, waits for writeback only in full sync mode, pins the anon_vma when needed, installs migration PTEs through `try_to_migrate()`, and records old state in the destination folio. `migrate_folio_move()` extracts that state, calls `move_to_new_folio()`, requeues deferred-split folios, places the new folio on LRU before restoring PTEs, removes migration entries with `remove_migration_ptes()`, then unlocks and releases old and new references.

Address-space migration goes through `__folio_migrate_mapping()`. It freezes the source folio reference count at an expected value, removes large folios from deferred split queues, transfers `index`, `mapping`, swapcache/private state, dirty state, and radix/XArray or swapcache slots to the destination, then adjusts lruvec and zone counters if the folio changed zones. `folio_migrate_flags()` then copies referenced/uptodate/active/unevictable/workingset/checked/mappedtodisk/young/idle/readahead metadata, moves NUMA cpupid state with memory-tiering special handling, migrates KSM and memcg state, clears source private/swapcache bits, and wakes destination writeback waiters.

Mapping restoration walks reverse maps through `remove_migration_ptes()`. For each migration entry, `remove_migration_pte()` reconstructs a present PTE or device-private entry with young, dirty, soft-dirty, uffd-wp, write, and anon-exclusive semantics preserved. When `TTU_USE_SHARED_ZEROPAGE` is requested, zero-filled anonymous subpages can be remapped to the shared zeropage instead of the migrated folio. Fault handlers that encounter migration entries wait through `migration_entry_wait()`, `migration_entry_wait_huge()`, or `pmd_migration_entry_wait()`.

The NUMA syscall path starts in `kernel_move_pages()`, validates flags and permissions through ptrace, LSM, capabilities, and cpuset nodemasks, then either collects folios per target node in `do_pages_move()` or reports current nodes in `do_pages_stat()`. Automatic NUMA balancing uses `migrate_misplaced_folio_prepare()` to reject shared executable file pages, dirty file folios, and low-watermark target nodes, then `migrate_misplaced_folio()` performs async migration and records NUMA promotion events.

## State and Persistence Behavior
Persistent kernel-visible state changes include page-table migration entries, XArray/swapcache replacement, folio LRU membership, folio flags, memcg membership, KSM metadata, page owner migrate reason, zone/lruvec counters, `mm->locked_vm` side effects through restored mlocked mappings, VM event counters, and NUMA/memory-tiering statistics. Movable page registration stores global pointers for offline and zsmalloc movable operations and intentionally has no concurrent registration protocol beyond rejecting duplicate non-NULL registrations.

Most migration state is transient and protected by folio locks, page-table locks, i_pages or swap-cluster locks, rmap locks, and refcount freezing. Destination folio `private` is temporarily borrowed to carry old mapped/mlocked bits and an anon_vma pointer between unmap and move phases. Callers retain responsibility for putting back remaining folios with `putback_movable_pages()` when `migrate_pages()` returns nonzero.

## Dependencies and Integration Points
This file integrates with rmap (`try_to_migrate()`, `rmap_walk()`), page table helpers, swapcache, XArray page cache, memory cgroups, KSM, hugetlb, compaction, memory hotplug/offline, page owner, page idle, buffer heads, filesystem `address_space_operations->migrate_folio`, NUMA policy and cpusets, LSM `security_task_movememory()`, ptrace permission checks, and tracepoints under `trace/events/migrate.h`. It also uses `internal.h` and `swap.h` for MM-private interfaces.

## Risks and Edge Cases
High-risk areas are reference-count expectation mismatches, migration of large folios on deferred split queues, anon-exclusive preservation, dirty/writeback races, swapcache replacement, PMD-mapped THP migration, hugetlb shared mapping locks, LRU isolation accounting, and movable_ops pages whose ownership is controlled by external drivers. Error handling is intentionally nuanced: `-EAGAIN` leaves folios retryable, `-ENOMEM` can stop the batch after moving already-unmapped folios, and permanent failures move folios to return lists. Incorrect old-state packing in destination `private`, missing `remove_migration_ptes()`, or misplaced ref/unlock ordering can strand migration entries, leak anon_vma refs, or free pages still visible to page tables.

## Test Signals
Useful coverage includes memory compaction and hot-remove tests, hugetlb migration, THP migration with split fallback, file-backed folio migration with and without filesystem callbacks, buffer-head mappings using both buffer migration variants, swapcache migration, KSM anonymous pages, mlocked and unevictable pages, NUMA `move_pages()` permission and status behavior, automatic NUMA balancing under memory pressure, memory-tiering promotion/demotion counters, fault waits on migration entries, and tracepoint/vmstat validation for success, failure, and split counters. Fault injection for destination allocation failure, folio lock contention, writeback, pinned pages, and refcount mismatch is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/migrate_device.c -->
# sources/distributed-fs/ceph-client/mm/migrate_device.c

## Purpose
Implements HMM/device-memory migration between CPU system memory, device-private memory, and device-coherent memory. It provides the driver-facing `migrate_vma_*()` workflow for virtual-address-based migration and PFN-range helpers for moving device private pages back to normal memory when a driver needs to evict or release device memory.

## Important APIs, Types, and Functions
Exported APIs are `migrate_vma_setup()`, `migrate_vma_pages()`, `migrate_vma_finalize()`, `migrate_device_pages()`, `migrate_device_finalize()`, `migrate_device_range()`, `migrate_device_pfns()`, and `migrate_device_coherent_folio()`. The central caller-provided type is `struct migrate_vma`, whose `vma`, `start`, `end`, `src`, `dst`, `npages`, `cpages`, `flags`, `pgmap_owner`, and optional `fault_page` fields describe the migration operation.

Important local helpers include `migrate_vma_collect_pmd()` and `migrate_vma_collect_huge_pmd()` for walking CPU page tables, `migrate_device_unmap()` for LRU isolation and rmap unmapping, `__migrate_device_pages()` for moving `struct page` metadata, `migrate_vma_insert_page()` and `migrate_vma_insert_huge_pmd_page()` for populating anonymous holes, and `__migrate_device_finalize()` for restoring CPU page tables and unlocking pages.

## Control Flow
The virtual-address workflow starts with `migrate_vma_setup()`, which validates VMA constraints, page-aligned range bounds, source/destination arrays, and optional locked device-private fault pages. It clears the source array, starts an MMU notifier `MMU_NOTIFY_MIGRATE` invalidation, walks the range, and records one source PFN entry per base page or one compound entry for PMD-sized THP migration. Present system pages, device-private swap entries, device-coherent pages, zero pages, and anonymous holes are either selected for migration or skipped according to `MIGRATE_VMA_SELECT_*` flags and `pgmap_owner`.

Collection installs migration entries opportunistically while holding page-table locks when it can lock the backing folio. Large folios are either collected as compound PMD migrations when selected and aligned, or split before base-page collection. After collection, `migrate_vma_unmap()` isolates non-device folios from LRU, calls `try_to_migrate()` for remaining mappings, checks for pins with `migrate_vma_check_page()`, restores pinned pages immediately, and leaves successfully selected pages locked and unmapped for driver copying.

The driver allocates and locks destination pages, copies data, writes `MIGRATE_PFN_VALID` destination PFNs, then calls `migrate_vma_pages()`. `__migrate_device_pages()` handles anonymous hole population, optional compound splitting when source and destination granularity differ, rejects unsupported ZONE_DEVICE destination types, frees swapcache for anonymous migration to device memory where possible, calls `folio_migrate_mapping()`, and copies folio flags. `migrate_vma_finalize()` then adds non-device destination folios to LRU, removes migration PTEs to either destination or source, unlocks pages, and drops references.

The PFN workflows `migrate_device_range()` and `migrate_device_pfns()` lock device PFNs directly with `migrate_device_pfn_lock()`, mark compound groups, call `migrate_device_unmap()`, and let drivers use `migrate_device_pages()` and `migrate_device_finalize()` without a VMA walk. `migrate_device_coherent_folio()` is a single-folio helper that migrates a device-coherent folio back to normal memory by unmapping, allocating a base system folio, moving metadata, copying contents on success, and finalizing.

## State and Persistence Behavior
During setup, source PTEs are replaced by migration entries or device-private entries and MMU notifiers tell device drivers to invalidate secondary mappings. Source and destination arrays carry persistent-in-the-operation flags such as `MIGRATE_PFN_MIGRATE`, `MIGRATE_PFN_WRITE`, `MIGRATE_PFN_COMPOUND`, and encoded PFNs. Folios remain locked across driver copy and page-table update phases, so drivers can inspect success after `migrate_vma_pages()` but before finalization.

Successful migration transfers address-space metadata and folio flags through the generic migration helpers, updates CPU page tables to the new page or restores the old page, adjusts LRU state for non-device pages, and drops operation references. Failed or skipped entries have `MIGRATE_PFN_MIGRATE` cleared and are restored to their original mapping during finalization.

## Dependencies and Integration Points
This file depends on MMU notifiers, page walking, rmap migration entries, `memremap`/`dev_pagemap`, ZONE_DEVICE page types, THP split/PMD helpers, anon_vma preparation, memcg charging, LRU isolation, and the generic migration helpers in `migrate.c`. It is designed for GPU, accelerator, and heterogeneous-memory drivers that mirror CPU page tables and need to migrate anonymous memory to/from device-owned memory.

## Risks and Edge Cases
Risk concentrates around secondary MMU synchronization, driver ownership filtering by `pgmap_owner`, compound THP selection and fallback splitting, preserving write/dirty/young/soft-dirty/uffd-wp state in migration entries, handling anonymous holes without delivering userfaultfd faults, memcg charge failure after driver allocation, and pinned-page detection. Device-private memory migration back to system memory must not fail lightly because an unserviceable device fault can become `SIGBUS`; the setup comments explicitly warn drivers about this. Unsupported ZONE_DEVICE types, DAX/special/hugetlb VMAs, unaligned or out-of-VMA ranges, and unlocked fault pages are rejected.

## Test Signals
Useful signals include HMM selftests or GPU-driver tests that migrate anonymous pages to device-private memory and back, device-coherent folio eviction, range-based migration during driver unload, write-protected and uffd-wp mappings, zero-page and anonymous-hole population, pinned-page rejection, THP compound migration and split fallback, memcg charge failure, mmu-notifier ordering observed by a secondary page table, and fault-page paths where the fault folio remains locked by the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/migrate_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mincore.c -->
# sources/distributed-fs/ceph-client/mm/mincore.c

## Purpose
Implements the `mincore(2)` system call, which reports whether pages in the calling process's virtual address range are resident enough that a fault would not need I/O. It walks VMAs and page tables, checks page cache and swap cache state for unmapped file-backed ranges, handles hugetlb and transparent huge mappings, and applies the kernel's side-channel mitigation for page-cache residency visibility.

## Important APIs, Types, and Functions
The user-visible entry point is `SYSCALL_DEFINE3(mincore)`. Important helpers are `do_mincore()`, `mincore_pte_range()`, `mincore_unmapped_range()`, `__mincore_unmapped_range()`, `mincore_page()`, `mincore_swap()`, `mincore_hugetlb()`, and `can_do_mincore()`. The page walker is configured by `mincore_walk_ops` with PMD, PTE-hole, hugetlb, and read-lock behavior.

## Control Flow
The syscall untags and validates the start address, requires page alignment, checks the user range and result vector with `access_ok()`, allocates one temporary page of bytes, and processes at most `PAGE_SIZE` residency entries per loop. For each chunk it takes `mmap_read_lock()`, calls `do_mincore()`, releases the lock, and copies the bytes to userspace.

`do_mincore()` finds the VMA covering the current address and limits the chunk to the VMA end. If the VMA is not eligible for precise residency visibility, it fills the result with `1`s to avoid leaking file page-cache state. Otherwise `walk_page_range()` drives `mincore_pte_range()`, `mincore_unmapped_range()`, and `mincore_hugetlb()`. Present PTEs and PMD-mapped THPs report resident, swap entries are checked through `mincore_swap()`, and PTE holes or markers in file-backed mappings consult `mincore_page()` to query the page cache.

## State and Persistence Behavior
The syscall does not persist kernel state. It briefly allocates a temporary kernel page, walks page tables under the mmap read lock and page-table locks, may take swap device references for shmem swap lookups, and gets transient folio references from filemap or swapcache lookups. Results are intentionally a snapshot; residency can change immediately after locks are dropped.

## Dependencies and Integration Points
The implementation depends on pagewalk, pgtable helpers, hugetlb, swapcache, shmem, filemap XArray entries, VMA lookup, and usercopy helpers. The visibility policy integrates with inode ownership/capability checks and `file_permission(..., MAY_WRITE)` to avoid exposing page-cache residency for files the caller could not write.

## Risks and Edge Cases
Important edge cases include partially covered VMAs, invalid gaps returning `-ENOMEM`, huge pages whose subpages must all receive the same byte, shmem swapin error entries, migration/hwpoison markers, swap disabled builds, concurrent page-table changes that require `ACTION_AGAIN`, and user vector faults. The side-channel behavior is subtle: denied non-anonymous mappings are reported as resident rather than failing or revealing actual cache state.

## Test Signals
Tests should cover anonymous resident and nonresident pages, file-backed cached and uncached pages with allowed and denied permissions, tmpfs/shmem swapped pages, hugetlb mappings, THP mappings, holes across VMA boundaries, unaligned start returning `-EINVAL`, invalid address ranges returning `-ENOMEM`, bad result vectors returning `-EFAULT`, and repeated calls under concurrent reclaim/migration to validate snapshot rather than stability semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mincore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mlock.c -->
# sources/distributed-fs/ceph-client/mm/mlock.c

## Purpose
Implements memory locking and unlocking for process VMAs and System V/shared memory accounting. It provides `mlock(2)`, `mlock2(2)`, `munlock(2)`, `mlockall(2)`, `munlockall(2)`, folio-level unevictable LRU transitions, per-CPU batching for mlock/munlock operations, RLIMIT/CAP checks, and user accounting for `SHM_LOCK`.

## Important APIs, Types, and Functions
User-facing syscall entry points are `mlock`, `mlock2`, `munlock`, `mlockall`, and `munlockall`. Exported or externally used helpers include `can_do_mlock()`, `mlock_drain_local()`, `mlock_drain_remote()`, `need_mlock_drain()`, `mlock_folio()`, `mlock_new_folio()`, `munlock_folio()`, `user_shm_lock()`, and `user_shm_unlock()`. The file-local `struct mlock_fbatch` stores a local lock and `folio_batch`; low pointer bits `LRU_FOLIO` and `NEW_FOLIO` encode which batch action to apply.

## Control Flow
Folio-level locking is deferred through per-CPU batches. `mlock_folio()` sets `PG_mlocked`, charges `NR_MLOCK`, takes a reference, and queues the folio as an LRU mlock operation. `mlock_new_folio()` does the same for newly allocated folios not yet on LRU. `munlock_folio()` queues the folio for unlock without clearing `PG_mlocked`; `__munlock_folio()` handles `mlock_count`, stats, and unevictable rescue decisions under the lruvec lock. `mlock_folio_batch()` decodes queued pointer flags, relocks the correct lruvec, calls `__mlock_folio()`, `__mlock_new_folio()`, or `__munlock_folio()`, unlocks the final lruvec, and releases folio refs.

Range operations operate on VMAs under the mmap write lock. `do_mlock()` normalizes and page-aligns the requested range, checks `RLIMIT_MEMLOCK` and `CAP_IPC_LOCK`, subtracts already-locked pages when needed, applies `VM_LOCKED` or `VM_LOCKONFAULT` through `apply_vma_lock_flags()`, then populates the range with `__mm_populate()` for non-on-fault mlock semantics. `munlock()` clears lock flags through the same VMA path. `mlockall()` updates `mm->def_flags` for future mappings and optionally applies current VMA flags, then populates all current address space when `MCL_CURRENT` is used.

`mlock_fixup()` filters secretmem and unsupported/special VMAs, splits or merges VMAs via `vma_modify_flags()`, updates `mm->locked_vm`, and invokes `mlock_vma_pages_range()` when actual page state must change. The page walker `mlock_pte_range()` handles PMD THPs and PTE ranges, skips zone-device pages and zero PMDs, batches large-folio PTE runs, and uses `allow_mlock_munlock()` to avoid incorrectly mlocking partially mapped large folios.

## State and Persistence Behavior
Persistent state includes VMA `VM_LOCKED` and `VM_LOCKONFAULT` flags, `mm->def_flags`, `mm->locked_vm`, folio `PG_mlocked`, folio `PG_unevictable`, folio `mlock_count`, LRU list placement, `NR_MLOCK`, unevictable VM events, and per-user `UCOUNT_RLIMIT_MEMLOCK` references for shared memory locks. Per-CPU folio batches are transient but must be drained on local CPU, CPU offline, LRU cache disable, or when callers need mlock side effects visible.

## Dependencies and Integration Points
The file integrates with VMA modification/iteration, pagewalk, rmap-visible VMA flags, LRU and lruvec locking, memcg/lruvec accounting, hugetlb and THP helpers, secretmem, resource limits, capabilities, shared memory user accounting, and population/fault-in helpers. It also cooperates with migration and reclaim: mlocked folios become unevictable, and migration restoration drains local mlock state when restoring mappings into locked VMAs.

## Risks and Edge Cases
Risk centers on mismatches between VMA lock flags and folio unevictable state, double mlock counting during concurrent migration/reclaim, partially mapped large folios, `mlock_count` undercount/overcount, and correct RLIMIT accounting when requests overlap already locked ranges. The temporary use of `VM_IO` inside `mlock_vma_pages_range()` is a concurrency signal to rmap walkers and must not leak as a visible VMA state. Secretmem is intentionally not unlocked. Error translation for population follows POSIX expectations, converting some `get_user_pages()` errors.

## Test Signals
Useful tests include `mlock`, `mlock2(MLOCK_ONFAULT)`, `munlock`, `mlockall` with current/future/onfault combinations, `munlockall`, RLIMIT and `CAP_IPC_LOCK` boundary cases, overlapping locked ranges, secretmem handling, THP and large-folio partial mappings, CPU hotplug drain paths, LRU unevictable statistics, shared memory `SHM_LOCK` accounting, and migration/reclaim interactions where mlocked folios must remain unevictable after PTE restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mm_init.c -->
# sources/distributed-fs/ceph-client/mm/mm_init.c

## Purpose
Builds the kernel memory-management foundation during boot and memory hotplug setup. It initializes global memory bounds, zero page state, zones, nodes, memmaps, pageblocks, deferred struct-page initialization, ZONE_DEVICE memmaps, CMA pageblocks, large system hash tables, memory hardening/debug static keys, and late page allocator setup. It is the bridge from early `memblock` physical memory descriptions to fully initialized `pg_data_t`, `zone`, `struct page`, and allocator state.

## Important APIs, Types, and Functions
Global exported state includes `high_memory`, `zero_page_pfn`, `empty_zero_page`/`__zero_page` where applicable, and non-NUMA `max_mapnr`/`mem_map`. Important entry points include `mm_core_init_early()`, `mm_core_init()`, `page_alloc_init_late()`, `memmap_init_range()`, `memmap_init_zone_device()`, `init_currently_empty_zone()`, `memmap_alloc()`, `get_pfn_range_for_nid()`, `node_map_pfn_alignment()`, `deferred_grow_zone()`, `init_cma_reserved_pageblock()`, `init_cma_pageblock()`, `set_zone_contiguous()`, `pfn_range_intersects_zones()`, `alloc_large_system_hash()`, and `memblock_free_pages()`.

Key command-line/init controls are `mminit_loglevel`, `kernelcore=`, `movablecore=`, `kernelcore=mirror`, `hashdist=`, `init_on_alloc=`, `init_on_free=`, and `check_pages=`. Important internal state includes zone PFN boundary arrays, per-node `zone_movable_pfn[]`, required kernel/movable core page counts, `deferred_struct_pages`, `boot_nodestats`, and deferred init completion counters.

## Control Flow
Early boot calls `mm_core_init_early()`, which reserves hugetlb CMA/bootmem and invokes `free_area_init()`. `free_area_init()` asks the architecture for zone limits, initializes sparse memory metadata, computes possible zone PFN ranges, derives per-node ZONE_MOVABLE starts from `kernelcore`, `movablecore`, mirrored memory, or movable-node settings, prints memory ranges, initializes node IDs and pageblock order, allocates node data for offline nodes, and calls `free_area_init_node()` for each node.

Per-node initialization computes spanned and present pages for each zone using memblock holes and movable-zone adjustments, allocates flatmem memmaps when needed, sets deferred-init boundaries, initializes pgdat internals, initializes each populated zone's locks, PCPs, free lists, pageblock flags, and LRU-generation state, then later `memmap_init()` initializes every valid `struct page` for early memory ranges and reserved holes. `memmap_init_range()` handles early, hotplug, and ZONE_DEVICE contexts; it initializes `struct page` links, reserved/offline flags, pageblock migratetypes, and can defer high-zone page initialization after one section to parallel late boot.

`mm_core_init()` runs after core architecture preinit and before general slab use. It initializes the zero page PFN, zonelists, page allocator CPU hotplug, allocation tag sections, flatmem page extensions, memory debugging/hardening static keys, KFENCE metadata, KMSAN shadow, stack depot, KHO memory, releases memblock pages to the buddy allocator, calls weak `mem_init()`, and initializes slab caches. `page_alloc_init_late()` completes deferred struct-page initialization in per-node kernel threads, disables on-demand deferred init, prints memory information, initializes buffer heads, discards memblock metadata, shuffles free memory, marks contiguous zones, initializes page extensions when deferral was used, and registers page allocator sysctls.

## State and Persistence Behavior
This file establishes long-lived MM topology state: node and zone spans, present and managed page counts, zone names and locks, per-zone free areas and pageblock flags, global direct-map high bound, zero-page PFN, page-to-node/zone links in every initialized `struct page`, ZONE_DEVICE `pgmap` backpointers, CMA migratetypes and counters, page allocator hardening static keys, hash table allocations, and boot memory accounting totals. Deferred initialization temporarily leaves high-zone `struct page` ranges uninitialized and records the first deferred PFN in each pgdat until late boot or `deferred_grow_zone()` initializes and frees those pages.

Most data is boot-persistent, but several variables are `__initdata` or `__meminitdata` and disappear after init. `memblock` remains authoritative until `memblock_free_all()` and `memblock_discard()`; after that, buddy allocator and zone structures own free memory.

## Dependencies and Integration Points
The file depends on memblock, sparsemem/flatmem, NUMA node maps, architecture zone limits and zero-page hooks, page allocator internals, page isolation/pageblock flags, hotplug memory notifiers, padata multithreading, CMA, hugetlb boot reservations, KFENCE, KMSAN, page_ext, stack depot, KHO, vmstat, buffer heads, debug pagealloc/page poisoning, and sysfs `kernel/mm` kobject creation. It exports allocator and topology helpers used across the MM subsystem and architecture setup.

## Risks and Edge Cases
Risk is high because initialization order is strict. Zone PFN calculations must handle holes, memoryless nodes, mirrored memory, movablecore/kernelcore percentages, descending architecture zone PFNs, highmem cutoffs, and hotplug reuse. Deferred struct-page initialization must not leave uninitialized pages visible to the buddy allocator or page_ext users; early page freeing must skip deferred ranges. ZONE_DEVICE initialization has specialized refcount and compound-page rules. Hardening options interact: page poisoning takes precedence over init-on-alloc/free, KMSAN warns about auto-init settings, and debug pagealloc enables page checking. `alloc_large_system_hash()` must avoid excessive boot allocations while preserving power-of-two masks.

## Test Signals
Important signals include boot logs for zone ranges, movable zone starts, early memory node ranges, memory totals, and mem auto-init state; NUMA and memoryless-node boot tests; `kernelcore=`, `movablecore=`, percentage, `kernelcore=mirror`, and `movable_node` scenarios; deferred struct-page init with large memory and early allocations; memory hotplug on new and existing nodes; ZONE_DEVICE/HMM/DAX initialization; CMA reserved pageblock accounting; sparsemem and flatmem builds; highmem/descending-zone architectures; page poisoning, init-on-alloc/free, debug pagealloc, KMSAN, and check_pages combinations; and large hash allocation fallbacks to vmalloc or linear memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mm_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mm_slot.h -->
# sources/distributed-fs/ceph-client/mm/mm_slot.h

## Purpose
Provides a small shared helper abstraction for subsystems that keep per-`mm_struct` records in both a hash table and an ordered/list structure. It defines the common `struct mm_slot`, allocation/free wrappers, and hash lookup/insert macros used by MM features that need to associate metadata with an address space.

## Important APIs, Types, and Functions
`struct mm_slot` contains `hash` for a hash bucket, `mm_node` for a list, and `mm` pointing to the address space the slot describes. `mm_slot_entry()` wraps `container_of()` so embedding subsystems can recover their larger object. `mm_slot_alloc()` allocates zeroed cache objects with `kmem_cache_zalloc(GFP_KERNEL)` and returns `NULL` if cache initialization failed. `mm_slot_free()` frees objects through the same slab cache. `mm_slot_lookup()` and `mm_slot_insert()` are statement-expression macros over Linux hash-table helpers.

## Control Flow
There is no standalone runtime flow. Callers allocate an embedding object from a subsystem slab cache, initialize or embed `struct mm_slot`, insert it with `mm_slot_insert()`, later find it with `mm_slot_lookup()`, and free it with `mm_slot_free()`. Lookup hashes the `mm_struct *` value and linearly scans the selected bucket for pointer equality.

## State and Persistence Behavior
The header owns no global state. Persistent state lives in caller-owned hash tables, lists, and slab caches. `mm_slot_insert()` writes the slot's `mm` pointer before adding it to the supplied hash table. The macros perform no locking or lifetime management, so callers must protect hash/list access and ensure the referenced `mm_struct` remains valid for the slot lifetime.

## Dependencies and Integration Points
The header depends on `<linux/hashtable.h>` and `<linux/slab.h>`. It is a utility interface for MM subsystems such as KSM-style or scanner-style code that need efficient lookup from `mm_struct` to subsystem metadata while also iterating all slots through a list.

## Risks and Edge Cases
The main risks are caller-side: missing external locking, stale `mm` pointers after address-space teardown, inserting duplicate slots for one `mm`, freeing through the wrong cache, and relying on `mm_slot_alloc()` without handling a `NULL` cache or allocation failure. Because the hash key is the raw pointer cast to `unsigned long`, correctness assumes stable `mm_struct` addresses during slot lifetime.

## Test Signals
Compile coverage for embedding users is the primary signal. Runtime tests should exercise insertion, duplicate prevention at the caller layer, lookup miss and hit paths, teardown ordering during process exit, slab allocation failure handling, and lockdep coverage around whatever subsystem lock protects the hash table and list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mm_slot.h -->
