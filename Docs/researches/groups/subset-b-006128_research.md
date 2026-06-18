# Research: subset-b-006128

Grouped research for HugeTLB memory-management sources under `sources/distributed-fs/ceph-client/mm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb.c -->
# `sources/distributed-fs/ceph-client/mm/hugetlb.c`

## Purpose
`hugetlb.c` is the core generic HugeTLB implementation. It owns huge-page hstate registration, boot-time and runtime pool allocation, per-node free/active lists, persistent/surplus/reserved page accounting, hugetlbfs reservation maps, VMA lock coordination, page fault handling, PMD page-table sharing, userfaultfd fill paths, migration/isolation hooks, memory-hotplug dissolve/replace behavior, and public reporting helpers used by `/proc`, sysfs, sysctl, hugetlbfs, migration, memory failure, and architecture page-table code.

## Important APIs, Types, And Functions
- Global state: `hstates[]`, `hugetlb_max_hstate`, `default_hstate_idx`, `hugetlb_lock`, `hugetlb_bootmem_nodes`, `huge_boot_pages[]`, `hugetlb_fault_mutex_table`, and per-hstate counters in `struct hstate`.
- Subpool API: `hugepage_new_subpool()`, `hugepage_put_subpool()`, `hugepage_subpool_get_pages()`, and `hugepage_subpool_put_pages()` enforce hugetlbfs inode min/max quotas and translate local subpool accounting into global reservations.
- VMA lock API: `hugetlb_vma_lock_read/write()`, `hugetlb_vma_unlock_read/write()`, `hugetlb_vma_trylock_write()`, `hugetlb_vma_lock_alloc()`, and `hugetlb_vma_lock_free()` serialize faults, truncation, and PMD sharing for shared VMAs, while private reservation maps carry their own `rw_sema`.
- Reservation-map internals: `resv_map_alloc()`, `resv_map_release()`, `region_chg()`, `region_add()`, `region_abort()`, `region_del()`, `region_count()`, `vma_needs_reservation()`, `vma_commit_reservation()`, `vma_end_reservation()`, `vma_add_reservation()`, and `vma_del_reservation()` maintain ordered `file_region` ranges and preallocated region cache entries.
- Pool and folio management: `enqueue_hugetlb_folio()`, `dequeue_hugetlb_folio_*()`, `remove_hugetlb_folio()`, `add_hugetlb_folio()`, `free_huge_folio()`, `alloc_fresh_hugetlb_folio()`, `alloc_hugetlb_folio()`, `alloc_hugetlb_folio_nodemask()`, `alloc_hugetlb_folio_reserve()`, `set_max_huge_pages()`, and `__nr_hugepages_store_common()` are the main runtime allocation and resizing surface.
- Boot allocation: `hugetlb_add_hstate()`, `hugetlb_bootmem_alloc()`, `alloc_bootmem_huge_page()`, `gather_bootmem_prealloc()`, `hugetlb_init_hstates()`, `hugetlb_init()`, plus command-line parsers for `hugepages=`, `hugepagesz=`, `default_hugepagesz=`, and `hugepage_alloc_threads=`.
- Fault and page-table paths: `hugetlb_fault()`, `hugetlb_no_page()`, `hugetlb_wp()`, `copy_hugetlb_page_range()`, `move_hugetlb_page_tables()`, `__unmap_hugepage_range()`, `hugetlb_change_protection()`, `huge_pte_alloc()`, `huge_pte_offset()`, and `hugetlb_mask_last_page()`.
- PMD sharing: `want_pmd_share()`, `huge_pmd_share()`, `huge_pmd_unshare()`, `huge_pmd_unshare_flush()`, `adjust_range_if_pmd_sharing_possible()`, `hugetlb_unshare_pmds()`, and `hugetlb_unshare_all_pmds()`.
- Userfaultfd and migration hooks: `hugetlb_mfill_atomic_pte()`, `hugetlb_handle_userfault()`, `folio_isolate_hugetlb()`, `folio_putback_hugetlb()`, `move_hugetlb_state()`, `get_hwpoison_hugetlb_folio()`, and `get_huge_page_for_hwpoison()`.
- Reservation public API: `hugetlb_reserve_pages()` and `hugetlb_unreserve_pages()` connect hugetlbfs mmap/truncate/evict operations to global, subpool, and hugetlb-cgroup reservation accounting.

## Control Flow
Initialization begins with early parameter capture through `hugetlb_early_param()` wrappers. `hugetlb_bootmem_alloc()` sets bootmem nodes, initializes `huge_boot_pages[]`, parses deferred HugeTLB parameters, and allocates gigantic hstates through memblock or CMA. Later `hugetlb_init()` guarantees the default hstate exists, applies implicit default-size counts, allocates non-gigantic pools, gathers bootmem pages into real folios, reports hstates, registers sysfs/cgroup/sysctl interfaces, and initializes per-page fault mutexes.

Pool growth and shrinkage flow through `__nr_hugepages_store_common()` into `set_max_huge_pages()`. Growth first converts surplus pages back to persistent pages, then allocates fresh frozen folios across allowed nodes and bulk-optimizes vmemmap before enqueuing. Shrinkage frees enough unused persistent pages while preserving reservations, optionally moves excess persistent pages into surplus state, and uses `update_and_free_pages_bulk()` to restore vmemmap before returning memory to buddy/CMA.

Reservations are two-phase. `region_chg()` computes missing reservation ranges and preallocates file-region entries, then `region_add()` commits or `region_abort()` rolls back. Shared mappings store reservation ranges in the inode `resv_map`; private mappings allocate a per-VMA `resv_map` where range meaning is inverted: absent entries mean reserved and present entries mean consumed. `hugetlb_reserve_pages()` charges hugetlb cgroups, subpools, and global reserves before committing shared map entries; `hugetlb_unreserve_pages()` deletes ranges and releases excess reservation state.

Fault handling uses a hash mutex keyed by mapping and hugepage offset to avoid spurious allocation failure when multiple tasks instantiate the same page. `hugetlb_fault()` allocates or locates a huge PTE under the VMA lock, dispatches missing entries to `hugetlb_no_page()`, handles markers/migration/hwpoison, resolves userfaultfd write-protect, and calls `hugetlb_wp()` for COW or unshare. `hugetlb_no_page()` can allocate a new folio, add shared folios to page cache, install PTEs, and opportunistically COW on write faults. `hugetlb_wp()` either reuses exclusive anonymous folios, allocates and copies a new huge folio, or unmaps child private mappings when the original owner cannot COW because the pool is inadequate.

Unmap, remap, protection, and fork paths all respect huge PTE granularity and PMD sharing. `copy_hugetlb_page_range()` preserves markers and migration entries, write-protects COW mappings, duplicates rmap state, and may allocate a new child folio when anon rmap duplication is unsafe. `__unmap_hugepage_range()` clears PTEs, restores private reservations when needed, leaves userfaultfd markers, updates mm counts and rmap, and flushes shared-PMD unshares. `move_hugetlb_page_tables()` and `hugetlb_change_protection()` widen invalidation ranges when PMD sharing is possible.

## State And Persistence Behavior
Persistent state is kept in `struct hstate` counters and lists: total pages, free pages, reserved pages, surplus pages, per-node variants, max persistent pages, demotion order, next allocation/free nodes, and resize locks. Huge folios persist on `hugepage_freelists[nid]` when free or `hugepage_activelist` when allocated/migratable; flags such as hugetlb, freed, temporary, restore-reserve, CMA, migratable, and vmemmap-optimized encode lifecycle state.

Reservation state persists in inode or private VMA `struct resv_map` objects with ordered `file_region` lists, region-cache entries, `adds_in_progress`, cgroup uncharge metadata, and a `kref`. Private reservation ownership and unmapped-failure state are stored in low bits of `vm_private_data` (`HPAGE_RESV_OWNER`, `HPAGE_RESV_UNMAPPED`).

Accounting spans multiple systems: `h->resv_huge_pages`, subpool `used_hpages` and `rsv_hpages`, `inode->i_blocks`, `mm->hugetlb_usage`, lruvec `NR_HUGETLB`, memcg hugetlb charges, and hugetlb cgroup reservation/fault counters. Boot-only state in `hugetlb_params`, `default_hugepages_in_node`, `huge_boot_pages`, and `hstate_boot_nrinvalid` is consumed during init.

## Dependencies And Integration Points
The file depends on generic mm, mempolicy, cpuset, memblock, padata, rmap, mmu-notifier, TLB gather, page-owner/tagging, migration, memory hotplug, userfaultfd, cgroup hugetlb, memcg, hugetlbfs inode/subpool helpers, architecture huge PTE primitives, CMA/contig allocation, and hugetlb vmemmap optimization. It calls into `hugetlb_cma.c` for gigantic CMA allocation and `hugetlb_vmemmap` for HVO restore/optimize. It exports behavior to sysfs/sysctl, `/proc/meminfo`, node meminfo, hugetlbfs mmap and inode eviction, fork/mremap/mprotect/munmap, memory failure, and migration.

## Risks
- Lock ordering is delicate: `hugetlb_lock`, hstate `resize_lock`, VMA locks, `i_mmap_rwsem`, page-table locks, page locks, mmap locks, and fault mutexes are combined in many paths. PMD sharing and userfaultfd paths are especially sensitive.
- Reservation maps are intentionally nontrivial. Incorrect `region_chg()`/`region_add()`/`region_abort()` pairing can leak `adds_in_progress`, lose file-region cache entries, or corrupt global/subpool/cgroup reservation counts.
- Private mapping semantics are inverted relative to shared mappings; mistakes around `HPAGE_RESV_OWNER`, `HPAGE_RESV_UNMAPPED`, or restore-reserve flags can SIGBUS/SIGKILL users or overcommit huge pages.
- Vmemmap optimization can fail under memory pressure; error handling intentionally turns pages into surplus or retries freeing. Counters and flags must remain consistent across partial restore failures.
- CMA, gigantic pages, and runtime allocation differ by architecture and config. Code must tolerate unsupported runtime gigantic allocation, early CMA-only allocation, and invalid bootmem zone intersections.
- PMD sharing requires widened invalidation ranges and deferred `huge_pmd_unshare_flush()` before dropping mapping locks; missing flushes risk page-table reuse races with GUP-fast or hardware walkers.
- Fault handling deliberately drops and reacquires locks for allocation, userfaultfd, and COW; stale PTE checks are mandatory to avoid installing pages over racing migration/truncation/unmap.

## Test Signals
- Boot tests with combinations of `hugepages=`, node-specific `hugepages=N:M`, `hugepagesz=`, `default_hugepagesz=`, `hugepage_alloc_threads=`, and gigantic/CMA options should verify hstate counts, invalid page handling, and init logs.
- Runtime sysfs/sysctl resize tests should grow, shrink, signal-interrupt, and node-constrain pools while checking `/proc/meminfo`, per-node meminfo, sysfs counts, and no negative reserve/surplus counters.
- hugetlbfs mmap tests should cover shared/private, `MAP_NORESERVE`, truncate/hole punch, fork/COW, mremap reservation fixup, mprotect write-protect, munmap, and subpool min/max limits.
- cgroup tests should verify `hugetlb.*.current/max/rsvd.*`, cgroup charge rollback on allocation failure, migration, and reservation uncharge when regions are deleted or VMAs close.
- Stress tests should combine faults from multiple tasks on the same offset, userfaultfd missing/minor/WP/poison/copy/continue, page migration, memory hotplug dissolve/replace, HWPoison, PMD sharing/unsharing, and HVO enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cgroup.c -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_cgroup.c`

## Purpose
`hugetlb_cgroup.c` implements the hugetlb cgroup controller. It allocates per-cgroup hugetlb accounting state, charges and uncharges hugepage fault and reservation usage, reparents charged active pages when cgroups go offline, tracks NUMA usage, exposes cgroup v1 and v2 files for each hstate, and migrates cgroup metadata during hugepage migration.

## Important APIs, Types, And Functions
- Global controller state: `root_h_cgroup`, dynamically allocated `dfl_files`, and `legacy_files`.
- Counter helpers: `hugetlb_cgroup_counter_from_cgroup()`, `hugetlb_cgroup_counter_from_cgroup_rsvd()`, `hugetlb_cgroup_from_css()`, `hugetlb_cgroup_from_task()`, `parent_hugetlb_cgroup()`, and `hugetlb_cgroup_have_usage()`.
- Lifecycle: `hugetlb_cgroup_css_alloc()`, `hugetlb_cgroup_css_offline()`, `hugetlb_cgroup_css_free()`, `hugetlb_cgroup_init()`, and `hugetlb_cgroup_free()`.
- Charging API consumed by `hugetlb.c`: `hugetlb_cgroup_charge_cgroup()`, `hugetlb_cgroup_charge_cgroup_rsvd()`, `hugetlb_cgroup_commit_charge()`, `hugetlb_cgroup_commit_charge_rsvd()`, `hugetlb_cgroup_uncharge_folio()`, `hugetlb_cgroup_uncharge_folio_rsvd()`, `hugetlb_cgroup_uncharge_cgroup()`, `hugetlb_cgroup_uncharge_cgroup_rsvd()`, `hugetlb_cgroup_uncharge_counter()`, and `hugetlb_cgroup_uncharge_file_region()`.
- Event and file interfaces: `hugetlb_event()`, `hugetlb_cgroup_read_numa_stat()`, `hugetlb_cgroup_read_u64()`, `hugetlb_cgroup_read_u64_max()`, `hugetlb_cgroup_write()`, `hugetlb_cgroup_reset()`, `hugetlb_events_show()`, and `hugetlb_events_local_show()`.
- Cgroup file templates: `hugetlb_dfl_tmpl[]` for v2 (`max`, `rsvd.max`, `current`, `rsvd.current`, `events`, `events.local`, `numa_stat`) and `hugetlb_legacy_tmpl[]` for v1 (`limit_in_bytes`, `usage_in_bytes`, `max_usage_in_bytes`, `failcnt`, reservation variants, `numa_stat`).
- Initialization: `hugetlb_cgroup_file_init()` builds per-hstate cftypes and registers them with cgroup core. `hugetlb_cgrp_subsys` declares the controller callbacks.

## Control Flow
When a cgroup is created, `hugetlb_cgroup_css_alloc()` allocates a flexible `struct hugetlb_cgroup` sized for `nr_node_ids`, allocates per-node `hugetlb_cgroup_per_node` records, initializes page counters for every hstate, and records the root cgroup. In legacy mode it enables `failcnt` tracking. Limits are initialized to rounded-down `PAGE_COUNTER_MAX` values that align with each huge page size.

Fault and reservation charging starts in `__hugetlb_cgroup_charge_cgroup()`. The current task's hugetlb css is acquired under RCU with `css_tryget()`, then the proper fault or reservation `page_counter` is charged. On failure the function increments the `HUGETLB_MAX` event and drops the css reference. Fault charges release the css reference immediately after a successful charge because the charged folio will point at the cgroup. Reservation charges keep a css reference until the reservation region or counter is removed.

Commit functions run with `hugetlb_lock` held and attach the cgroup pointer to the folio, separately for real allocation and reservation charge. Non-reservation commits also increment per-node usage in `h_cg->nodeinfo[nid]->usage[idx]`. Uncharge functions clear the folio cgroup pointer, uncharge page counters, drop css references for reservations, and decrement per-node usage for real pages.

When a cgroup goes offline, `hugetlb_cgroup_css_offline()` repeatedly scans all hstate active lists under `hugetlb_lock` and calls `hugetlb_cgroup_move_parent()` for folios charged to the dying cgroup until no usage remains. Pages are moved to the parent or root counter without failure.

Cgroup file setup is generated per hstate. `hugetlb_cgroup_cfttypes_init()` formats file names with hugepage size prefixes, encodes hstate index and attribute in `cftype.private`, adjusts event file offsets for per-hstate arrays, and registers lockdep keys. The post-init step registers the generated cftypes for v1 and v2.

## State And Persistence Behavior
Each hugetlb cgroup owns two `page_counter` arrays per hstate: `hugepage[]` for instantiated pages and `rsvd_hugepage[]` for reservations. It also owns per-hstate event counters, event cgroup files, and per-node usage arrays. Usage is not persisted outside memory; it is reflected through cgroupfs files. Reservation cgroup references persist in `resv_map` or `file_region` metadata in `hugetlb.c` until the reserved range is deleted or the private VMA closes.

## Dependencies And Integration Points
The file depends on cgroup core, `page_counter`, NUMA node iteration, hugetlb folio metadata accessors, `hugetlb_lock`, hstate iteration, and cgroup file registration. It is called from `hugetlb.c` allocation, free, reservation, reservation-delete, cgroup-offline, and migration paths. Its `hugetlb_cgrp_subsys` object is consumed by kernel cgroup initialization.

## Risks
- Reservation css references must be exactly balanced. File regions can split and share source metadata, so `copy_hugetlb_cgroup_uncharge_info()` and per-region `css_get()` behavior in `hugetlb.c` are tightly coupled to these uncharge functions.
- Per-node usage is updated under `hugetlb_lock` and read with `READ_ONCE`; readers should expect approximate but consistent-enough values, especially for hierarchical NUMA stats that traverse descendant cgroups.
- Offline reparenting scans active lists until local usage drains. If folio cgroup tags or counters become inconsistent, the loop can spin or leave usage behind.
- cgroup v1/v2 file naming and `private` encoding must stay aligned with template order and hstate count. Incorrect offsets for event files can notify the wrong cgroup file.
- Limit writes round down to hugepage multiples; tests need to verify user-visible values because byte inputs can silently align down.

## Test Signals
- Create cgroup v1 and v2 hierarchies, set `max`/`limit_in_bytes` and `rsvd.max`/`rsvd.limit_in_bytes`, and verify faults fail with `events:max` or `failcnt` increments.
- Exercise reservation-only paths with mmap, truncate, VMA close, shared/private mappings, and region splits to confirm `rsvd.current` returns to zero.
- Offline a cgroup holding active huge pages and verify usage moves to the parent/root and no charged folios keep dangling css references.
- Verify `numa_stat` totals against per-node hugepage placement and hierarchical descendants.
- Run hugepage migration and confirm both fault and reservation cgroup tags move from old folio to new folio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cma.c -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_cma.c`

## Purpose
`hugetlb_cma.c` provides the HugeTLB-specific CMA backend used primarily for gigantic huge pages. It parses `hugetlb_cma=` and `hugetlb_cma_only=` boot parameters, reserves per-node or distributed CMA regions early in boot, allocates/free frozen compound folios from those regions, and exposes policy helpers used by the core hugetlb allocator.

## Important APIs, Types, And Functions
- Static state: `hugetlb_cma[MAX_NUMNODES]`, `hugetlb_cma_size_in_node[]`, `hugetlb_cma_only`, and `hugetlb_cma_size`.
- Runtime allocation: `hugetlb_cma_alloc_frozen_folio()` tries the requested node first, then allowed nodes unless `__GFP_THISNODE` is set; successful folios are tagged with `folio_set_hugetlb_cma()`.
- Runtime free: `hugetlb_cma_free_frozen_folio()` releases CMA-backed frozen folios with `cma_release_frozen()`.
- Boot allocation: `hugetlb_cma_alloc_bootmem()` reserves early CMA chunks for gigantic boot pages, can fall back across `hugetlb_bootmem_nodes`, and records `HUGE_BOOTMEM_CMA` and the `struct cma *` in `struct huge_bootmem_page`.
- Parameter parsing: `cmdline_parse_hugetlb_cma()` supports total-size syntax and node-specific `node:size[,node:size]` syntax; `cmdline_parse_hugetlb_cma_only()` parses a boolean.
- Reservation setup: `hugetlb_cma_reserve()` validates architecture support, minimum region size, node validity, and then calls `cma_declare_contiguous_multi()` for each selected node.
- Policy helpers: `hugetlb_cma_exclusive_alloc()`, `hugetlb_cma_total_size()`, `hugetlb_cma_validate_params()`, and `hugetlb_early_cma()`.
- Architecture hook: weak `arch_hugetlb_cma_order()` returns 0 unless an architecture provides the gigantic CMA alignment/order.

## Control Flow
`early_param("hugetlb_cma", ...)` parses requested CMA size before normal init. A single size is stored in `hugetlb_cma_size`; node-specific entries accumulate into both per-node and total sizes. `hugetlb_cma_only=` is parsed as a boolean and later invalidated if no CMA size was requested.

During early memory setup, `hugetlb_cma_reserve()` returns immediately if no size was requested or the architecture does not provide a CMA order. It warns if the order is not truly gigantic, builds the bootmem node mask, drops invalid node-specific requests, validates each region is at least one huge CMA allocation unit, computes a per-node size for non-specific requests, and declares named CMA areas such as `hugetlb0`. If all declarations fail, `hugetlb_cma_size` is reset to zero so later allocation paths know CMA is unavailable.

At hugetlb boot allocation time, `hugetlb_early_cma()` returns true for gigantic hstates when the architecture lacks regular huge bootmem allocation and `hugetlb_cma_only` is active. `hugetlb_cma_alloc_bootmem()` then reserves from the node's CMA area, optionally falling back to another bootmem node, and annotates the bootmem record so later conversion initializes CMA pageblocks and frees through the CMA path.

At runtime, `hugetlb_cma_alloc_frozen_folio()` only participates if `hugetlb_cma_size` is nonzero. It allocates a frozen compound page from the requested node's CMA area, then falls back across the supplied nodemask when allowed. `hugetlb.c` tries this path for gigantic allocations before falling back to contiguous allocation unless `hugetlb_cma_only` forbids fallback.

## State And Persistence Behavior
CMA regions are declared during boot and persist for the life of the kernel in `hugetlb_cma[]`. `hugetlb_cma_size` doubles as both requested-size accounting and a runtime availability flag. CMA-backed boot pages carry `HUGE_BOOTMEM_CMA` and a CMA pointer until gathered by `hugetlb.c`; runtime folios carry the `hugetlb_cma` folio flag so `free_huge_folio()` returns them to CMA instead of the buddy allocator.

## Dependencies And Integration Points
This file depends on CMA allocation APIs (`cma_declare_contiguous_multi()`, `cma_alloc_frozen_compound()`, `cma_release_frozen()`, `cma_reserve_early()`), memblock/boot node discovery through `hugetlb_bootmem_nodes`, architecture setup hooks, and core HugeTLB hstate helpers. `hugetlb.c` consumes its allocation, free, size, exclusivity, parameter validation, and early-CMA predicates. `hugetlb_internal.h` and `hugetlb_cma.h` provide the declarations and fallback stubs.

## Risks
- `hugetlb_cma_only` changes allocation semantics by preventing fallback to `alloc_contig_frozen_pages()` for gigantic pages; incorrect validation could leave systems unable to allocate huge pages.
- Node-specific parsing mutates total size as invalid nodes are discovered; tests should verify mixed valid/invalid node lists do not overstate available CMA.
- The architecture-provided CMA order is critical. If too small or zero, reservations are rejected or warned because gigantic huge page assumptions break.
- Runtime allocation fallback across `nodemask` must respect `__GFP_THISNODE`; violating this would break node-specific pool semantics.
- Early CMA boot records must be marked so later bootmem conversion initializes CMA pageblocks and later frees use CMA release.

## Test Signals
- Boot with total and node-specific `hugetlb_cma=` values and verify logs show expected per-node reservations and invalid-node warnings.
- Boot with `hugetlb_cma_only=true` with and without a valid CMA size and verify `hugetlb_cma_validate_params()` disables exclusivity when no CMA exists.
- Allocate and free gigantic huge pages and confirm CMA-backed folios carry the CMA flag and are released through `cma_release_frozen()`.
- Test `__GFP_THISNODE` and nodemask-constrained allocation for node-local behavior.
- On architectures without `arch_hugetlb_cma_order()`, verify the warning and zero effective CMA availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cma.h -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_cma.h`

## Purpose
`hugetlb_cma.h` is the internal interface between core HugeTLB code and the optional CMA backend. It declares the real CMA helpers when `CONFIG_CMA` is enabled and provides no-op or false/NULL/zero inline stubs when CMA is disabled, allowing `hugetlb.c` to call the same API regardless of configuration.

## Important APIs, Types, And Functions
- Allocation/free declarations under `CONFIG_CMA`: `hugetlb_cma_alloc_frozen_folio()`, `hugetlb_cma_free_frozen_folio()`, and `hugetlb_cma_alloc_bootmem()`.
- Policy/query declarations: `hugetlb_cma_exclusive_alloc()`, `hugetlb_cma_total_size()`, `hugetlb_cma_validate_params()`, and `hugetlb_early_cma()`.
- Non-CMA stubs return safe defaults: allocation functions return `NULL`, `hugetlb_cma_exclusive_alloc()` and `hugetlb_early_cma()` return `false`, `hugetlb_cma_total_size()` returns `0`, and free/validate functions do nothing.

## Control Flow
The header itself has no dynamic control flow. Preprocessor selection determines whether callers link to `hugetlb_cma.c` or compile inline fallback behavior. In non-CMA builds, `hugetlb.c` naturally falls back to non-CMA allocation paths because the CMA allocation helper returns `NULL` and the exclusive-allocation predicate is false.

## State And Persistence Behavior
The header defines no state. It controls visibility of state owned by `hugetlb_cma.c` when CMA is enabled and makes that state appear absent when CMA is disabled.

## Dependencies And Integration Points
The API uses `struct folio`, `struct hstate`, `struct huge_bootmem_page`, `gfp_t`, and `nodemask_t` from core mm/HugeTLB headers. It is included by `hugetlb.c` and `hugetlb_cma.c`.

## Risks
- Stub behavior must stay semantically aligned with `hugetlb.c` expectations. A non-CMA build relies on `NULL` allocation and `false` exclusivity to preserve fallback behavior.
- Any new CMA helper added in `hugetlb_cma.c` should also get a non-CMA stub here, otherwise configuration-specific build failures or `#ifdef` leakage will occur.
- The include guard uses `_LINUX_HUGETLB_CMA_H`; conflicting names would cause missing prototypes in internal mm builds.

## Test Signals
- Build both `CONFIG_CMA=y` and `CONFIG_CMA=n` kernels.
- In non-CMA builds, verify gigantic allocation either uses architecture-supported non-CMA paths or fails cleanly without unresolved symbols.
- In CMA builds, verify callers link to real implementations and boot parameter validation is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_cma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_internal.h -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_internal.h`

## Purpose
`hugetlb_internal.h` centralizes private HugeTLB declarations and small helpers shared by the HugeTLB core, sysfs, sysctl, and CMA-adjacent code. It avoids exporting these details through public headers while keeping hstate node iteration, gigantic-page gating, pool mutation, demotion, resize, and init hooks available across HugeTLB translation units.

## Important APIs, Types, And Functions
- `hstate_is_gigantic_no_runtime()` returns true for gigantic hstates when runtime gigantic-page support is unavailable.
- Node selection helpers: `next_node_allowed()`, `get_valid_node_allowed()`, `hstate_next_node_to_alloc()`, and `hstate_next_node_to_free()`.
- Iteration macros: `for_each_node_mask_to_alloc()` and `for_each_node_mask_to_free()` implement bounded round-robin traversal over allowed nodes.
- Core declarations exported from `hugetlb.c`: `remove_hugetlb_folio()`, `add_hugetlb_folio()`, `init_new_hugetlb_folio()`, `prep_and_add_allocated_folios()`, `demote_pool_huge_page()`, and `__nr_hugepages_store_common()`.
- Init declarations: `hugetlb_sysfs_init()` and conditional `hugetlb_sysctl_init()`.

## Control Flow
The inline node helpers normalize potentially stale `next_nid_to_alloc` or `next_nid_to_free` values against a caller-provided nodemask. Allocation returns the current valid node and advances the stored next-node pointer. Free selection uses `h->next_nid_to_free` similarly. The macros wrap these helpers with a `nodes_weight()` countdown so callers visit each allowed node at most once per operation.

`hstate_is_gigantic_no_runtime()` is used by sysfs/sysctl and core resize/free paths to reject operations that cannot work on gigantic pages without runtime support while still allowing boot-time accounting and reporting.

## State And Persistence Behavior
The header mutates hstate round-robin cursors via inline helpers: allocation updates an integer passed by pointer and free updates `h->next_nid_to_free`. It defines no independent persistent state.

## Dependencies And Integration Points
It depends on `linux/hugetlb.h` for `struct hstate` and hstate helpers, and `linux/hugetlb_cgroup.h` for cgroup types used by HugeTLB internals. It is included by `hugetlb.c`, `hugetlb_sysfs.c`, and `hugetlb_sysctl.c`.

## Risks
- The node iteration helpers assume non-empty allowed masks; they use `VM_BUG_ON(nid >= MAX_NUMNODES)` after `next_node_in()`. Callers must validate masks.
- The allocation/free macros evaluate helper calls inside loop conditions; callers must pass stable nodemask pointers and writable next-node storage.
- Changing `hstate_is_gigantic_no_runtime()` semantics affects sysfs/sysctl resize rejection, demotion, and freeing behavior.
- Declarations here are private but cross-file; prototype drift from `hugetlb.c` will produce build failures or worse if types remain compatible but semantics change.

## Test Signals
- Runtime resize and demotion tests with restricted nodemasks should show round-robin distribution and no out-of-mask allocation/free.
- Build configurations with and without `CONFIG_SYSCTL` should verify `hugetlb_sysctl_init()` resolves to a real function or inline no-op.
- Gigantic hstate tests on architectures with and without runtime support should verify resize/demotion rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_sysctl.c -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_sysctl.c`

## Purpose
`hugetlb_sysctl.c` registers HugeTLB controls under `/proc/sys/vm` when `CONFIG_SYSCTL` is enabled. It provides sysctl handlers for the default hstate's persistent hugepage count, mempolicy-aware count, shared-memory group, overcommit count, and optional movable gigantic page behavior.

## Important APIs, Types, And Functions
- Global setting: `int movable_gigantic_pages`, exposed when `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION` is enabled.
- `proc_hugetlb_doulongvec_minmax()` safely duplicates a `ctl_table` and redirects `.data` to a stack temporary before calling `proc_doulongvec_minmax()`.
- `hugetlb_sysctl_handler_common()` reads/writes `default_hstate.max_huge_pages` through `__nr_hugepages_store_common()`, optionally honoring task mempolicy.
- `hugetlb_sysctl_handler()` implements `nr_hugepages`.
- `hugetlb_mempolicy_sysctl_handler()` implements `nr_hugepages_mempolicy` under `CONFIG_NUMA`.
- `hugetlb_overcommit_handler()` reads/writes `default_hstate.nr_overcommit_huge_pages` and rejects writes to gigantic hstates without runtime support.
- `hugetlb_table[]` defines the `/proc/sys/vm` entries.
- `hugetlb_sysctl_init()` registers the table under `vm`.

## Control Flow
For `nr_hugepages` and `nr_hugepages_mempolicy`, the handler snapshots the default hstate max count into `tmp`, lets the generic sysctl parser read or update `tmp`, and on write calls `__nr_hugepages_store_common()` with `NUMA_NO_NODE`. The mempolicy variant passes `obey_mempolicy=true`.

For `nr_overcommit_hugepages`, the handler rejects writes when the default hstate is gigantic and runtime allocation/free is unsupported, parses into a temporary, and commits `h->nr_overcommit_huge_pages` under `hugetlb_lock`.

## State And Persistence Behavior
Sysctl writes mutate in-kernel HugeTLB state only. `nr_hugepages` changes persistent pool size through the same core resize path used by sysfs. `nr_overcommit_hugepages` changes the default hstate's surplus allocation ceiling. `hugetlb_shm_group` writes to `sysctl_hugetlb_shm_group`. These settings persist until changed or rebooted; the file does not itself store state on disk.

## Dependencies And Integration Points
The file depends on sysctl core, `default_hstate`, `hugepages_supported()`, `hugetlb_lock`, `hstate_is_gigantic_no_runtime()`, `__nr_hugepages_store_common()`, and `sysctl_hugetlb_shm_group`. It is initialized from `hugetlb_init()` through `hugetlb_sysctl_init()` declared in `hugetlb_internal.h`.

## Risks
- The temporary-table wrapper avoids races with generic sysctl parsing; bypassing it and pointing directly at live counters would expose partially parsed writes or races with HugeTLB resize.
- Only the default hstate is exposed through these sysctls; multi-size HugeTLB management belongs in sysfs.
- Overcommit writes are protected by `hugetlb_lock` but no resize mutex; this is acceptable for a scalar limit but must stay consistent with surplus allocation checks.
- Gigantic hstates without runtime support must reject overcommit and resize writes to avoid impossible allocations.

## Test Signals
- Read and write `/proc/sys/vm/nr_hugepages` and compare with `/proc/meminfo` and sysfs default hstate counts.
- On NUMA systems, write `nr_hugepages_mempolicy` under an mbind/cpuset policy and verify node placement constraints.
- Write `nr_overcommit_hugepages` while faulting `MAP_NORESERVE` mappings to verify surplus allocation caps.
- Build with `CONFIG_SYSCTL=n` and verify the inline no-op path from the internal header.
- Build with `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION=y` and verify `movable_gigantic_pages` registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_sysfs.c -->
# `sources/distributed-fs/ceph-client/mm/hugetlb_sysfs.c`

## Purpose
`hugetlb_sysfs.c` creates HugeTLB sysfs interfaces under the global `mm/hugepages` kobject and, on NUMA builds, per-node `node*/hugepages` kobjects. It exposes per-hstate pool sizing, free/reserved/surplus counts, overcommit, mempolicy-aware resizing, and demotion controls.

## Important APIs, Types, And Functions
- Global kobjects: `hugepages_kobj` and `hstate_kobjs[HUGE_MAX_HSTATE]`.
- Kobject lookup: `kobj_to_hstate()` and `kobj_to_node_hstate()` map sysfs objects back to an hstate and optional NUMA node.
- Pool attributes: `nr_hugepages_show/store`, `nr_hugepages_mempolicy_show/store`, `nr_overcommit_hugepages_show/store`, `free_hugepages_show`, `resv_hugepages_show`, and `surplus_hugepages_show`.
- Demotion attributes: `demote_store`, `demote_size_show`, and `demote_size_store`.
- Attribute groups: `hstate_attr_group`, `hstate_demote_attr_group`, and `per_node_hstate_attr_group`.
- Registration helpers: `hugetlb_sysfs_add_hstate()`, `hugetlb_sysfs_init()`, `hugetlb_register_node()`, `hugetlb_unregister_node()`, and `hugetlb_register_all_nodes()`.
- NUMA state: `hugetlb_sysfs_initialized` and `node_hstates[MAX_NUMNODES]`.

## Control Flow
`hugetlb_sysfs_init()` creates the global `hugepages` kobject under `mm_kobj`, then registers one child per hstate using `hugetlb_sysfs_add_hstate()`. Each hstate gets the standard attribute group, and hstates with `demote_order` also get demotion attributes. On NUMA builds, initialization marks sysfs ready and registers hugepage kobjects for all online nodes.

Writes to `nr_hugepages` and `nr_hugepages_mempolicy` parse a decimal count, resolve the target hstate and optional node from the kobject, and call `__nr_hugepages_store_common()` with `obey_mempolicy` false or true. Per-node kobjects pass the node id so the core resize path constrains allocation/free to that node.

`nr_overcommit_hugepages_store()` parses a scalar and updates the hstate overcommit limit under `hugetlb_lock`, rejecting gigantic hstates without runtime support. Count show methods read either global hstate counters or per-node arrays depending on the kobject.

`demote_store()` parses the requested number of huge pages to demote, builds a node mask for a node-specific kobject or all memory nodes for a global kobject, then holds the source hstate `resize_lock` and `hugetlb_lock` while repeatedly calling `demote_pool_huge_page()`. It only demotes free pages beyond reservations. `demote_size_store()` validates that the requested target hugepage size exists, is at least `HUGETLB_PAGE_ORDER`, and is smaller than the source hstate before updating `h->demote_order` under the resize lock.

NUMA node registration creates `node->dev.kobj/hugepages` and per-hstate children with a smaller attribute group. Unregistration removes demote and standard groups, drops kobject references, and clears per-node pointers.

## State And Persistence Behavior
The sysfs files expose live `struct hstate` state and per-node hstate counters. Writes mutate `h->max_huge_pages`, per-node pool counts through core resize, `h->nr_overcommit_huge_pages`, and `h->demote_order`. Kobject pointers persist in global and per-node arrays until unregister/init cleanup. No sysfs value is stored independently of HugeTLB core state.

## Dependencies And Integration Points
This file depends on sysfs/kobject infrastructure, NUMA node devices, `mm_kobj`, hstate iteration, `__nr_hugepages_store_common()`, `demote_pool_huge_page()`, `size_to_hstate()`, `hugetlb_lock`, hstate resize locks, and page-isolation/page-owner headers used by demotion dependencies. It is initialized from `hugetlb_init()` and responds to node hotplug registration callbacks.

## Risks
- Kobject-to-hstate lookup must remain correct; failing to find a kobject calls `BUG()` in the node lookup path.
- Demotion changes two hstates and locks source then destination by size-order convention in the core demotion path. Incorrect lock ordering could deadlock with resize.
- `demote_store()` subtracts reserved pages from free pages before demotion; underflow or stale counts would allow demoting pages needed for reservations.
- Per-node registration can partially fail and must unwind with `hugetlb_unregister_node()` to avoid dangling sysfs entries.
- Global and node-specific attributes have different attribute sets; adding a new attribute requires deciding whether it is valid per-node and updating both groups intentionally.

## Test Signals
- Verify `/sys/kernel/mm/hugepages/hugepages-*/` files exist for each hstate and show counts matching `/proc/meminfo` for the default hstate.
- Write global and per-node `nr_hugepages`, including invalid values and interrupted allocations, and verify counts and error returns.
- On NUMA builds, online/offline node devices and verify per-node hugepage sysfs directories register and unregister cleanly.
- Exercise `demote_size` and `demote` with valid smaller hstates, invalid sizes, reserved pages, poisoned/free pages, and node-specific demotion.
- Write `nr_overcommit_hugepages` on gigantic hstates with and without runtime support and verify rejection/acceptance behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hugetlb_sysfs.c -->
