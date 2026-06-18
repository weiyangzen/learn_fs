# Group Research: group_889_linux_sources_os_linux_linux_mm_hugetlb_c_sources_os_linux_linux_mm__7a8711afc7b8

Scope: `Docs/research_subset_a.md`

Files researched:

- `sources/os/linux/linux/mm/hugetlb.c`
- `sources/os/linux/linux/mm/hugetlb_cgroup.c`
- `sources/os/linux/linux/mm/hugetlb_cma.c`
- `sources/os/linux/linux/mm/hugetlb_cma.h`
- `sources/os/linux/linux/mm/hugetlb_internal.h`
- `sources/os/linux/linux/mm/hugetlb_sysctl.c`
- `sources/os/linux/linux/mm/hugetlb_sysfs.c`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb.c -->
# File Research: sources/os/linux/linux/mm/hugetlb.c

## Purpose

`hugetlb.c` is the core Linux HugeTLB implementation. It manages huge page hstates, reservations, subpools, allocation and freeing, page-table installation and teardown, faults, copy-on-write, migration/isolation, PMD page-table sharing, boot-time huge page setup, runtime pool resizing, and accounting hooks used by hugetlbfs, SysV shared memory, memory hotplug, userfaultfd, cgroups, memcg, NUMA policy, and MMU notifier users.

## Major Responsibilities

- Maintain global hstate state in `hstates[]`, including per-node free lists, active lists, persistent page counts, surplus counts, reservation counts, demotion targets, and resize locks.
- Implement hugetlbfs reservation maps (`struct resv_map` and `struct file_region`) for shared and private mappings, including placeholder/cache handling for non-sleeping reservation updates.
- Enforce subpool limits/minimums through `hugepage_subpool_get_pages()` and `hugepage_subpool_put_pages()`.
- Allocate, free, enqueue, dequeue, dissolve, replace, demote, isolate, and migrate hugetlb folios.
- Coordinate with HugeTLB Vmemmap Optimization (HVO), including deferred freeing when vmemmap restoration cannot use sleeping allocation context.
- Handle boot-time huge page command-line parsing, memblock/gigantic-page allocation, parallel buddy allocation, hstate initialization, and final reporting.
- Implement HugeTLB VM operations, page-table copying/moving/unmapping, protection changes, userfaultfd population, and fault handling.
- Support PMD page-table sharing for compatible shared hugetlb mappings and explicit unsharing before truncation, zap, mremap, or split-sensitive operations.
- Export memory information, total huge page count, and sysfs/sysctl-facing pool resize helpers.

## Reservation and Subpool Model

The file uses two reservation layers. The global hstate has `resv_huge_pages`, while hugetlbfs inodes may have a `hugepage_subpool` with optional maximum and minimum reservation constraints. `hugepage_new_subpool()` pre-charges minimum reservations, `hugepage_put_subpool()` releases the subpool when its references and usage drop to zero, and the get/put helpers return the amount by which global reservations must be adjusted.

Reservation maps are ordered lists of `file_region` ranges. Shared mappings record offsets that have reservations; private mappings invert the meaning and record consumed reservations. The main helpers are:

- `region_chg()`: counts missing reservation ranges and preallocates file-region descriptors.
- `region_add()`: commits a prior change and coalesces adjacent regions with matching cgroup uncharge metadata.
- `region_abort()`: cancels a pending `region_chg()`.
- `region_del()`: removes, trims, or splits reservation regions and uncharges reservation cgroups.
- `region_count()`: counts reserved overlap for close/unmap accounting.

Private VMA reservation ownership is encoded in low bits of `vm_private_data` with `HPAGE_RESV_OWNER` and `HPAGE_RESV_UNMAPPED`. `hugetlb_dup_vma_private()`, `clear_vma_resv_huge_pages()`, and `fixup_hugetlb_reservations()` handle fork and mremap cases where reservation ownership must not be inherited blindly.

## VMA Locks and Fault Serialization

HugeTLB has an extra VMA-level lock abstraction. Shared mappings allocate a `struct hugetlb_vma_lock` in `vm_private_data`; private mappings use the reservation map's `rw_sema` when the VMA owns the map. Read/write lock helpers synchronize page faults, truncation, PMD sharing, zap, and VMA split/unshare paths.

Faults on the same logical file page are also serialized through `hugetlb_fault_mutex_table`, hashed by mapping and huge-page offset. This avoids spurious allocation failures when multiple CPUs race to instantiate the same huge page.

## Allocation and Freeing

Free persistent huge pages live on per-node `h->hugepage_freelists`; allocated pages live on `h->hugepage_activelist`. `enqueue_hugetlb_folio()` moves a frozen folio to a free list and updates free counters. `dequeue_hugetlb_folio_*()` selects free pages according to NUMA policy, cpuset constraints, long-term pin suitability, hardware poison state, and page isolation state.

Fresh folios come from either the buddy allocator or gigantic-page contiguous allocation/CMA paths:

- `alloc_buddy_frozen_folio()` wraps `__alloc_frozen_pages()` and tracks per-node no-retry state for bulk pool growth.
- `alloc_gigantic_frozen_folio()` tries HugeTLB CMA first and then `alloc_contig_frozen_pages()` unless CMA-only allocation is configured.
- `alloc_fresh_hugetlb_folio()` initializes the folio and applies HVO.
- `alloc_surplus_hugetlb_folio()` grows the surplus pool within `nr_overcommit_huge_pages`.
- `alloc_hugetlb_folio()` is the fault-time allocator that combines reservation map state, subpool accounting, hugetlb cgroup reservation/usage charges, hstate free-list dequeue, surplus allocation fallback, memcg charging, rmap/stat setup, and reservation commit/rollback.

Freeing flows through `free_huge_folio()`, which restores reservations when needed, uncharges hugetlb cgroups and memcg, updates `NR_HUGETLB`, returns non-surplus pages to free lists, and frees temporary/surplus pages back to the lower allocator. HVO-aware freeing uses `hugetlb_vmemmap_restore_folio()` or bulk restoration before clearing the hugetlb flag and releasing pages. Atomic contexts can defer freeing through `hpage_freelist` and `free_hpage_work`.

## Pool Resizing, Surplus Pages, and Demotion

`set_max_huge_pages()` is the runtime pool resizing engine used by sysfs and sysctl. It serializes with `h->resize_lock`, flushes deferred free work, converts surplus pages back to persistent pages when growing, allocates fresh pool pages in node-rotating order, frees excess free pages when shrinking, and marks still-in-use excess pages as surplus.

Reservation growth uses `gather_surplus_pages()` to temporarily allocate surplus pages so reservations can succeed, then commits or rolls them back. `return_unused_surplus_pages()` releases unused reservation-backed surplus pages.

Demotion lets free huge pages in a larger hstate be split into smaller hstate pages. `demote_pool_huge_page()` selects free source folios, `demote_free_hugetlb_folios()` restores source vmemmap, splits page owner/allocation tags and compound metadata, preserves CMA state, initializes child hugetlb folios, and adds them to the destination hstate. Hstate initialization selects a default `demote_order` when a smaller hstate exists and runtime/CMA constraints allow it.

## Boot-Time Setup

HugeTLB command-line handling is staged: early parameters are copied into an init buffer by `hugetlb_add_param()` and consumed later by `hugetlb_parse_params()` after valid huge page sizes are known. Supported parameters include `hugepages=`, `hugepagesz=`, `default_hugepagesz=`, and `hugepage_alloc_threads=`.

Gigantic pages are allocated early through memblock or HugeTLB CMA and placed in `huge_boot_pages` until `gather_bootmem_prealloc()` converts them into normal hugetlb folios after memmap setup. Non-gigantic boot pages are allocated from the buddy allocator, potentially in parallel through padata. Boot initialization also validates zone boundaries, initializes tail vmemmap pages when HVO did not pre-optimize, sets pageblock migratetypes, updates managed page counts, and registers sysfs, cgroup files, sysctl handlers, and the fault mutex table.

## Page Tables and VM Operations

`hugetlb_vm_ops` supplies open/close, split validation, pagesize reporting, and a BUG fault method because normal VM faults must be routed to `hugetlb_fault()`. VMA open/close manage reservation map references and shared VMA locks; close releases unused private reservations and subpool/global reservation accounting.

Page-table helpers include:

- `make_huge_pte()` and writable variants for architecture-adjusted huge PTE creation.
- `copy_hugetlb_page_range()` for fork, including COW write-protection, rmap duplication, migration/hwpoison/marker entries, userfaultfd write-protect preservation, and early COW when anon rmap duplication fails.
- `move_hugetlb_page_tables()` for mremap-style relocation with MMU notifier and TLB gather sequencing.
- `__unmap_hugepage_range()` and `unmap_hugepage_range()` for zap/truncate/unmap, including PMD unsharing, dirtying, rmap removal, UFFD-WP marker preservation, reservation restoration for private anonymous pages, and TLB batching.
- `hugetlb_change_protection()` for mprotect/userfaultfd write-protect changes over present PTEs, migration entries, hwpoison entries, and markers.

## Fault Handling

`hugetlb_fault()` handles all HugeTLB faults. It hashes and takes the per-page fault mutex, takes the VMA lock, allocates/looks up the huge PTE, and dispatches to:

- `hugetlb_no_page()` for missing PTEs, page-cache lookup, userfaultfd missing/minor events, fresh allocation, page-cache insertion, anonymous rmap setup, and optional immediate write fault handling.
- `hugetlb_wp()` for write-protect/COW/unshare faults, including shared mapping write enable, exclusive anonymous page reuse, private-owner COW reservation bypass, child unmapping on owner COW failure, anon preparation, folio copy, MMU notifier invalidation, and reservation rollback.
- migration-entry wait and hwpoison error handling for non-present entries.
- userfaultfd write-protect resolution before COW.

The fault path is careful about lock dropping. Userfaultfd handling drops the VMA lock and fault mutex because it can drop `mmap_lock`. COW allocation drops the page-table lock around allocation/copying, then revalidates the PTE before installation.

## Userfaultfd Population

Under `CONFIG_USERFAULTFD`, `hugetlb_mfill_atomic_pte()` supports UFFDIO_COPY, UFFDIO_CONTINUE, UFFDIO_POISON, and write-protect population. It can allocate the final reservation-consuming folio, fall back to a temporary folio for copying outside `mmap_lock`, insert shared pages into the hugetlbfs page cache, install poison or write-protect markers, reject existing mappings, handle hwpoison, and update rmap/mm counters and migratability state.

## PMD Sharing

When `CONFIG_HUGETLB_PMD_PAGE_TABLE_SHARING` is enabled, compatible shared VMAs can share PMD page-table pages for PMD-sized huge pages. `want_pmd_share()` checks VMA shareability, VMA lock presence, userfaultfd restrictions, and PUD alignment. `huge_pmd_share()` searches the file mapping's interval tree for a compatible VMA and installs a shared PMD table while holding `i_mmap_rwsem`.

Unsharing uses `huge_pmd_unshare()` / `__huge_pmd_unshare()` to clear the PUD entry, decrement PMD accounting, and hand the shared page table to TLB gather. `huge_pmd_unshare_flush()` synchronizes walkers before `i_mmap_rwsem` is dropped. `adjust_range_if_pmd_sharing_possible()` widens invalidation ranges to PUD boundaries when needed.

## Migration, Memory Hotplug, and Poison

The file provides free-page dissolving and allocated-page isolation:

- `dissolve_free_hugetlb_folio()` and `dissolve_free_hugetlb_folios()` remove free huge pages from the pool for memory hotplug.
- `replace_free_hugepage_folios()` replaces free huge pages in a PFN range.
- `isolate_or_dissolve_huge_folio()` either isolates an in-use folio or allocates a replacement and dissolves a free folio.
- `folio_isolate_hugetlb()` and `folio_putback_hugetlb()` manage migration isolation references and active-list membership.
- `move_hugetlb_state()` transfers cgroup state, owner migration reason, temporary/surplus node state, and migratability after migration.
- `get_hwpoison_hugetlb_folio()` safely obtains references for hwpoison/unpoison handling.

## Integration Points and Invariants

This file is central to HugeTLB correctness. Important invariants include holding `hugetlb_lock` for hstate counters/lists and cgroup folio pointer updates, using reservation-map `region_chg`/`region_add`/`region_abort` as a transaction, preserving VMA locks around shared PMD page-table walks, restoring HVO vmemmap before freeing pages to the buddy allocator, and carefully pairing hugetlb cgroup reservation references with file-region or resv-map lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cgroup.c -->
# File Research: sources/os/linux/linux/mm/hugetlb_cgroup.c

## Purpose

`hugetlb_cgroup.c` implements the HugeTLB cgroup controller. It tracks and limits HugeTLB usage per hstate for both fault-time page consumption and reservation-time commitments, exposes cgroup v1/v2 control files, records per-node usage for NUMA reporting, emits limit events, reparents charged pages on cgroup offline, and migrates cgroup ownership during HugeTLB folio migration.

## Major Responsibilities

- Allocate and initialize `struct hugetlb_cgroup` CSS objects with per-hstate usage and reservation `page_counter`s.
- Maintain separate counters for actual huge page usage (`hugepage[]`) and reserved huge page commitments (`rsvd_hugepage[]`).
- Charge, commit, uncharge, and migrate HugeTLB cgroup state for folios and reservation maps.
- Provide cgroup v2 files such as `<size>.max`, `<size>.current`, `<size>.rsvd.max`, `<size>.rsvd.current`, `<size>.events`, `<size>.events.local`, and `<size>.numa_stat`.
- Provide legacy cgroup v1 files such as `<size>.limit_in_bytes`, usage, max usage, failcnt, reservation equivalents, and numa stats.
- Track per-node usage in `h_cgroup->nodeinfo[nid]->usage[idx]` for NUMA stat output.
- Reparent charged active huge pages to the parent cgroup when a hugetlb cgroup goes offline.

## Cgroup Lifetime

`hugetlb_cgroup_css_alloc()` allocates a flex-array `hugetlb_cgroup`, allocates per-node `hugetlb_cgroup_per_node` structures, assigns the root cgroup, and initializes all counters through `hugetlb_cgroup_init()`. Each hstate gets usage and reserved counters with parent linkage. Legacy mode enables failcnt tracking. Limits are rounded down to huge-page multiples.

`hugetlb_cgroup_css_offline()` repeatedly scans every hstate active list under `hugetlb_lock` and calls `hugetlb_cgroup_move_parent()` until the cgroup has no usage. Actual charged folios are moved to the parent, or to the root cgroup if there is no parent. Reservation charges are not reparented because reservations hold their own CSS references.

## Charge and Uncharge Flow

The charge path uses `__hugetlb_cgroup_charge_cgroup()`. It obtains the current task's hugetlb cgroup under RCU, pins the CSS, and attempts a `page_counter_try_charge()` against either the usage or reserved counter. Limit failures increment the `HUGETLB_MAX` event. Non-reservation charges immediately drop the CSS reference because the folio pointer does not own a CSS reference; reservation charges keep it until reservation uncharge.

Commit helpers require `hugetlb_lock`:

- `hugetlb_cgroup_commit_charge()` records actual usage ownership on a folio and increments per-node usage.
- `hugetlb_cgroup_commit_charge_rsvd()` records reservation ownership on a folio.

Uncharge helpers clear folio cgroup pointers, uncharge the matching page counter, drop reserved CSS references when needed, and decrement per-node usage for actual charges. Reservation-only uncharge can also happen from a whole `resv_map`, a `file_region`, or a charged cgroup pointer when an allocation/reservation path aborts.

## User Interface

The file dynamically builds cftype arrays once hstates are known. `hugetlb_cgroup_cfttypes_init()` prefixes each template file with a formatted huge page size such as `2MB` or `1GB`, encodes the hstate index and resource attribute in `cftype.private`, adjusts event file offsets per hstate, and registers lockdep keys.

For cgroup v2, limits use `max` syntax and output `max` when the counter limit is the rounded page-counter maximum. For legacy cgroups, limits use `-1`, max/fail counters can be reset by writing, and failcnt tracking is enabled. All byte values are rounded down to the hstate page size before being stored as page-counter units.

`hugetlb_cgroup_read_numa_stat()` prints non-hierarchical node usage in legacy mode and hierarchical node totals by walking descendant CSS objects. `hugetlb_event()` increments local and hierarchical event counters and notifies cgroup files.

## Migration and Integration

`hugetlb_cgroup_migrate()` moves both actual and reserved cgroup pointers from an old folio to a new folio while holding `hugetlb_lock`, then moves the new folio onto the hstate active list. It is used by HugeTLB migration state transfer in `hugetlb.c`.

The file depends on `hugetlb_lock` to serialize folio cgroup pointer updates, active-list scans during cgroup offline, and migration against cgroup removal. It is tightly coupled with `hugetlb.c` reservation-map code through `resv_map`, `file_region`, and cgroup reservation uncharge metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cma.c -->
# File Research: sources/os/linux/linux/mm/hugetlb_cma.c

## Purpose

`hugetlb_cma.c` implements HugeTLB integration with CMA reserved memory. It lets gigantic HugeTLB pages be allocated from per-node CMA areas, supports early boot reservation for CMA-only gigantic pages, parses HugeTLB CMA command-line options, and exposes policy helpers used by the main HugeTLB allocator.

## Major Responsibilities

- Store per-node HugeTLB CMA areas in `hugetlb_cma[]`.
- Parse `hugetlb_cma=` as either a global size or a comma-separated per-node `node:size` list.
- Parse `hugetlb_cma_only=` to force gigantic HugeTLB allocation to use the CMA reservation path.
- Reserve per-node CMA areas during early boot via `hugetlb_cma_reserve()`.
- Allocate and free frozen compound folios from HugeTLB CMA for runtime gigantic-page allocation.
- Provide early bootmem allocation from CMA for hstates that must use CMA before normal runtime allocation is available.
- Validate that CMA-only mode is disabled if no HugeTLB CMA area was configured.

## Allocation and Freeing

`hugetlb_cma_alloc_frozen_folio()` returns a frozen compound folio from a node-local CMA area when available. If allocation is not constrained by `__GFP_THISNODE`, it can fall back across the provided nodemask. Successful allocation marks the folio with `folio_set_hugetlb_cma()` so later freeing returns it to CMA.

`hugetlb_cma_free_frozen_folio()` releases a frozen folio back to its node's CMA area with `cma_release_frozen()`. The main HugeTLB free path calls this when the folio carries the HugeTLB CMA flag.

`hugetlb_cma_alloc_bootmem()` reserves a huge page from a node's CMA area during early boot, optionally falling back to other `hugetlb_bootmem_nodes` when exact-node allocation is not required. It tags the returned `huge_bootmem_page` with `HUGE_BOOTMEM_CMA` and stores the CMA pointer.

## Reservation Setup

`hugetlb_cma_reserve()` is the boot-time CMA declaration path. It first checks that the architecture supplies a nonzero `arch_hugetlb_cma_order()` and warns if the order is not larger than `MAX_PAGE_ORDER`, because this path is intended for gigantic pages. It validates node-specific requests against memory nodes and minimum size, then either reserves the requested per-node sizes or spreads a global request across memory nodes rounded to the gigantic-page size.

The CMA declaration uses `cma_declare_contiguous_multi()` with a name of `hugetlb<nid>`. The "order per bit" argument is `HUGETLB_PAGE_ORDER`, which matters when demotion later returns smaller huge pages to CMA. If all reservations fail, `hugetlb_cma_size` is reset to zero so allocation helpers know CMA is unavailable.

## Policy Helpers

`hugetlb_cma_exclusive_alloc()` reports whether `hugetlb_cma_only` is set. `hugetlb_cma_total_size()` reports whether any CMA reservation was requested/successfully kept. `hugetlb_cma_validate_params()` clears CMA-only mode if there is no CMA area. `hugetlb_early_cma()` tells `hugetlb.c` to allocate gigantic boot pages through CMA when the architecture lacks a huge bootmem allocator and CMA-only mode is active.

This file is compiled behind `CONFIG_CMA`; the companion header provides no-op stubs otherwise.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cma.h -->
# File Research: sources/os/linux/linux/mm/hugetlb_cma.h

## Purpose

`hugetlb_cma.h` is the internal interface between core HugeTLB code and the optional HugeTLB CMA implementation. It declares CMA allocation, freeing, boot reservation, and policy helpers when `CONFIG_CMA` is enabled and supplies inline no-op fallbacks when CMA is not built.

## Interface

With `CONFIG_CMA`, it exposes:

- `hugetlb_cma_free_frozen_folio()` to return a frozen HugeTLB CMA folio to CMA.
- `hugetlb_cma_alloc_frozen_folio()` to allocate a frozen compound folio for runtime HugeTLB allocation.
- `hugetlb_cma_alloc_bootmem()` to reserve a boot-time HugeTLB page from CMA.
- `hugetlb_cma_exclusive_alloc()` to report CMA-only allocation mode.
- `hugetlb_cma_total_size()` to report configured/reserved HugeTLB CMA size.
- `hugetlb_cma_validate_params()` to normalize command-line state after parsing.
- `hugetlb_early_cma()` to decide whether a gigantic hstate should allocate boot pages through CMA.

Without `CONFIG_CMA`, all allocation helpers return `NULL`, size returns `0`, exclusive/early-CMA helpers return `false`, and free/validation helpers are empty. This lets `hugetlb.c` call the interface unconditionally while compiling out CMA behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_cma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_internal.h -->
# File Research: sources/os/linux/linux/mm/hugetlb_internal.h

## Purpose

`hugetlb_internal.h` collects internal HugeTLB helpers and declarations shared by the core, sysfs, sysctl, and CMA-adjacent implementation files. It is not a public HugeTLB API; it exists to keep cross-file internals consistent.

## Helpers

The key inline predicate is `hstate_is_gigantic_no_runtime()`, which detects hstates whose order is gigantic while runtime gigantic-page allocation/freeing is unsupported. Sysfs, sysctl, allocation, free, and resize paths use it to reject or skip operations that cannot work on such hstates.

The header also provides node-rotation helpers for pool balancing:

- `next_node_allowed()` advances within a nodemask and asserts a valid node.
- `get_valid_node_allowed()` repairs a saved next-node value that is outside the current allowed mask.
- `hstate_next_node_to_alloc()` returns and advances an external next-allocation node cursor.
- `hstate_next_node_to_free()` returns and advances an hstate's next-free node cursor.
- `for_each_node_mask_to_alloc` and `for_each_node_mask_to_free` wrap these helpers for bounded iteration over allowed nodes.

These helpers allow `hugetlb.c` to spread persistent huge page allocation/freeing across changing cpuset or mempolicy node masks without trusting stale cursor values.

## Cross-File Declarations

The header declares core pool manipulation and sysfs/sysctl entry points used across files:

- `remove_hugetlb_folio()`, `add_hugetlb_folio()`, `init_new_hugetlb_folio()`, and `prep_and_add_allocated_folios()`.
- `demote_pool_huge_page()` for sysfs demotion requests.
- `__nr_hugepages_store_common()` for sysfs and sysctl pool resizing.
- `hugetlb_sysfs_init()` and `hugetlb_sysctl_init()`.

When `CONFIG_SYSCTL` is disabled, `hugetlb_sysctl_init()` is an inline no-op so `hugetlb.c` can call it unconditionally.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_sysctl.c -->
# File Research: sources/os/linux/linux/mm/hugetlb_sysctl.c

## Purpose

`hugetlb_sysctl.c` registers `/proc/sys/vm` sysctl controls for the default HugeTLB hstate. It bridges text sysctl reads/writes to the core pool resize and overcommit logic in `hugetlb.c`, while also exposing the hugetlb shared-memory group and optional gigantic-page migration knob.

## Controls

The sysctl table registers:

- `vm/nr_hugepages`: read or resize the default hstate persistent huge page pool.
- `vm/nr_hugepages_mempolicy` under `CONFIG_NUMA`: same resize path, but honoring the caller's memory policy where possible.
- `vm/hugetlb_shm_group`: group id allowed to create SysV hugepage shared memory without extra privilege.
- `vm/nr_overcommit_hugepages`: read or update the default hstate surplus overcommit limit.
- `vm/movable_gigantic_pages` under `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION`: global integer controlling movable gigantic-page behavior.

## Implementation Details

`proc_hugetlb_doulongvec_minmax()` duplicates the `ctl_table` before changing `.data`, avoiding races with the generic `proc_doulongvec_minmax()` handler. `hugetlb_sysctl_handler_common()` reads the default hstate's `max_huge_pages` into a temporary value, lets the proc helper parse/update it, then on writes calls `__nr_hugepages_store_common()` with or without mempolicy enforcement.

`hugetlb_overcommit_handler()` similarly parses into a temporary value and commits `h->nr_overcommit_huge_pages` under `hugetlb_lock`. It rejects writes for gigantic hstates without runtime support. All HugeTLB handlers return `-EOPNOTSUPP` when the architecture does not support huge pages.

`hugetlb_sysctl_init()` registers the table under `vm` during HugeTLB initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_sysfs.c -->
# File Research: sources/os/linux/linux/mm/hugetlb_sysfs.c

## Purpose

`hugetlb_sysfs.c` builds the sysfs interface for HugeTLB hstates under `/sys/kernel/mm/hugepages` and, on NUMA systems, per-node HugeTLB directories under node devices. It exposes pool sizing, free/reserved/surplus counts, overcommit limits, optional mempolicy-based resizing, and demotion controls.

## Global Hstate Interface

During `hugetlb_sysfs_init()`, the file creates `mm_kobj/hugepages`, then one hstate kobject per HugeTLB page size using the hstate name such as `hugepages-2048kB`. Each hstate gets the common attribute group:

- `nr_hugepages`: read/write persistent pool size.
- `nr_overcommit_hugepages`: read/write surplus overcommit limit.
- `free_hugepages`: read-only free count.
- `resv_hugepages`: read-only global reservation count.
- `surplus_hugepages`: read-only surplus count.
- `nr_hugepages_mempolicy` under `CONFIG_NUMA`: read/write pool size honoring caller mempolicy.

Read helpers use `kobj_to_hstate()` to resolve whether a kobject is global or node-specific. Writes parse unsigned long values and call `__nr_hugepages_store_common()` with the resolved hstate and node id. Overcommit writes update `h->nr_overcommit_huge_pages` under `hugetlb_lock` and reject hstates whose gigantic pages cannot be managed at runtime.

## Demotion Interface

If an hstate has `h->demote_order`, `hugetlb_sysfs_add_hstate()` also creates a demotion attribute group:

- `demote`: write-only count of free huge pages to demote.
- `demote_size`: read/write target huge page size.

`demote_store()` parses the requested count, chooses either a single-node or all-memory-node mask, takes `h->resize_lock` and `hugetlb_lock`, checks free unreserved availability, and calls `demote_pool_huge_page()` until the request is satisfied or an error occurs. `demote_size_store()` parses a size, requires it to match an existing hstate with smaller order and at least `HUGETLB_PAGE_ORDER`, and updates `h->demote_order` under the resize lock.

## NUMA Node Interface

Under `CONFIG_NUMA`, the file maintains `node_hstates[MAX_NUMNODES]`, each with a `hugepages` kobject and per-hstate child kobjects attached to the node device. Per-node hstate directories expose a subset of attributes:

- `nr_hugepages`
- `free_hugepages`
- `surplus_hugepages`

`hugetlb_register_node()` creates these directories for a node after sysfs initialization, while `hugetlb_unregister_node()` removes demotion and per-node groups and drops kobject references. `hugetlb_register_all_nodes()` registers all online nodes during HugeTLB sysfs init. `kobj_to_node_hstate()` maps a node hstate kobject back to its global hstate and node id.

## Integration and Error Handling

The file relies on `hugetlb_internal.h` for the shared resize and demotion helpers. Sysfs setup is best-effort: failure to create one hstate logs an error, while failure to add demotion attributes removes the partially created hstate group. NUMA registration is guarded by `hugetlb_sysfs_initialized` so node hotplug callbacks before HugeTLB setup do not create incomplete directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hugetlb_sysfs.c -->