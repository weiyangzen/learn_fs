# Research: sources/distributed-fs/ceph-client/mm/huge_memory.c

## Purpose

`huge_memory.c` is the Linux transparent huge page (THP) implementation for PMD-sized and, where supported, PUD-sized huge mappings. It owns the runtime THP policy flags, sysfs/debugfs control surfaces, huge zero folio lifetime, anonymous huge PMD fault handling, huge file/PFN insertion helpers, huge PMD/PUD copy/zap/move/protection paths, THP splitting, deferred split shrinkers, and THP migration entries.

Although it lives in the `distributed-fs/ceph-client` source tree, the file is generic kernel MM infrastructure. Ceph or other filesystems integrate with it indirectly through address-space large-folio support, read-only file THP eligibility, shmem/tmpfs policy, DAX/special mappings, page-cache accounting, and generic fault/zap/migrate paths.

## Important APIs, Types, and State

Core exported or cross-MM entry points:

- `__thp_vma_allowable_orders()` filters candidate THP orders by VMA type, global/anonymous order policy, DAX/special/file rules, alignment, shmem policy, `MADV_HUGEPAGE`, forced collapse, and page-fault versus collapse context.
- `thp_get_unmapped_area_vmflags()` / `thp_get_unmapped_area()` ask the generic unmapped-area allocator for padded space so file offsets can land on PMD-size boundaries.
- `do_huge_pmd_anonymous_page()` handles anonymous PMD faults, including huge zero PMD mappings for read faults and real huge anonymous folio allocation for write faults.
- `do_huge_pmd_wp_page()` handles write faults on huge PMDs, reusing exclusive anonymous THPs when possible and splitting when COW cannot safely stay huge.
- `do_huge_pmd_numa_page()` handles NUMA hinting faults on huge PMDs and may migrate misplaced THPs.
- `copy_huge_pmd()` / `copy_huge_pud()` duplicate huge mappings across fork-like address-space copies.
- `zap_huge_pmd()` / `zap_huge_pud()` remove huge mappings, update rmap and counters, withdraw deposited page tables, and queue TLB removal.
- `move_huge_pmd()` and, under userfaultfd, `move_pages_huge_pmd()` move huge PMD mappings during `mremap()`/UFFD-style operations.
- `change_huge_pmd()` / `change_huge_pud()` update huge mapping protections for `mprotect()`, NUMA balancing, soft-dirty, and userfaultfd write-protect.
- `vmf_insert_pfn_pmd()`, `vmf_insert_folio_pmd()`, `vmf_insert_pfn_pud()`, and `vmf_insert_folio_pud()` let drivers/filesystems install huge PFN or folio mappings in fault handlers.
- `split_huge_pmd_locked()`, `__split_huge_pmd()`, `split_huge_pmd_address()`, `__split_huge_pud()`, `__split_huge_page_to_list_to_order()`, `folio_split()`, `folio_split_unmapped()`, `split_folio_to_list()`, and `min_order_for_split()` implement page-table and physical-folio splitting.
- `deferred_split_folio()`, `__folio_unqueue_deferred_split()`, `deferred_split_count()`, `deferred_split_scan()`, and `reparent_deferred_split_queue()` implement deferred splitting and shrinker integration.
- `set_pmd_migration_entry()` and `remove_migration_pmd()` convert huge PMDs to and from PMD-level migration/device-private entries.

Important local structures and globals:

- `transparent_hugepage_flags` is the primary global bitmask for THP enablement, defrag mode, unsupported state, and huge zero page use.
- `huge_anon_orders_always`, `huge_anon_orders_madvise`, and `huge_anon_orders_inherit` store multi-size anonymous THP policy by folio order.
- `huge_zero_folio`, `huge_zero_pfn`, and `huge_zero_refcount` manage the PMD-sized huge zero folio.
- `deferred_split_shrinker` and `huge_zero_folio_shrinker` connect THP reclaim work to the shrinker API.
- `split_underused_thp` controls whether non-partially-mapped but underused THPs are queued for splitting.
- `DEFINE_PER_CPU(struct mthp_stat, mthp_stats)` backs per-order sysfs statistics.
- `struct folio_or_pfn` is a small local union used by PMD/PUD insertion helpers.
- `struct thpsize` kobjects, declared in `include/linux/huge_mm.h`, are created per supported THP order under sysfs.

## Control Flow

Initialization starts at `subsys_initcall(hugepage_init)`. The init path checks `has_transparent_hugepage()`, creates `/sys/kernel/mm/transparent_hugepage`, registers the top-level THP attributes and `khugepaged` attribute group, creates per-size `hugepages-<size>kB` kobjects, initializes `khugepaged`, registers the deferred split shrinker and optional huge-zero-folio shrinker, disables THP by default on systems below 512 MiB RAM, then starts or stops `khugepaged` according to policy. Boot parameters `transparent_hugepage=` and `thp_anon=` preconfigure the global mode and anonymous order policies.

Sysfs control flow is split between global knobs and per-order knobs. `enabled_store()` changes `always`/`madvise`/`never` global policy and restarts `khugepaged` or recalculates watermarks. `defrag_store()` rewrites the mutually exclusive defrag bits. `use_zero_page_store()` and `split_underused_thp_store()` update simple boolean policy. Per-order `anon_enabled_store()` writes one of `always`, `inherit`, `madvise`, or `never` into the order bitmaps under `huge_anon_orders_lock`.

Anonymous huge PMD fault flow enters `do_huge_pmd_anonymous_page()`. The function first checks PMD-order suitability and prepares anonymous VMA state. Read faults may map the huge zero folio when enabled and allowed; this allocates a deposited PTE table, locks the PMD, handles userfaultfd-missing if necessary, then installs a special huge zero PMD. Other faults call `__do_huge_pmd_anonymous_page()`, which allocates and memcg-charges a PMD-order folio, allocates the deposited PTE table, validates that the PMD is still empty and the address space is stable, handles userfaultfd-missing, deposits the table, installs the PMD, updates counters, and queues the folio for deferred split.

Huge write-protect fault flow enters `do_huge_pmd_wp_page()`. Huge zero PMDs are replaced by newly allocated anonymous THPs through `do_huge_zero_wp_pmd()`, with MMU notifier invalidation around the clear/install. For normal anonymous THPs, the function tries to reuse exclusive mappings, handles swapcache cleanup, sets `PageAnonExclusive`, and upgrades access bits. If references, pins, or exclusivity prevent safe reuse, it splits the PMD and returns `VM_FAULT_FALLBACK`.

Page-table maintenance follows a lock-and-revalidate pattern. Copy, zap, move, and change paths lock the relevant PMD/PUD, recheck the entry against the observed value, update rmap and mm counters, preserve soft-dirty and userfaultfd write-protect bits, and use MMU notifier/TLB gather APIs when entries are cleared or protection is changed. PMD code handles anonymous, file, huge zero, migration, and device-private entries. PUD support is conditional on `CONFIG_HAVE_ARCH_TRANSPARENT_HUGEPAGE_PUD` and is narrower, especially for anonymous PUDs.

Splitting has two layers. `__split_huge_pmd_locked()` splits a huge PMD mapping into PTEs, converting present THPs, huge zero PMDs, migration entries, and device-private entries while preserving dirty, young, soft-dirty, uffd-wp, write, and anon-exclusive state. Physical folio splitting is handled by `__folio_split()`: it validates splittability, locks anon-vma or mapping state, releases filesystem-private metadata, unmaps the folio, freezes the expected refcount, updates xarray/page-cache/swapcache/LRU/memcg/page-owner metadata, calls `__split_unmapped_folio()`, then remaps anonymous folios through migration entries. Uniform splitting targets one order for all resulting folios; non-uniform splitting recursively splits only the region containing `split_at`, producing mixed-order folios.

Deferred splitting starts when new or partially mapped THPs call `deferred_split_folio()`. Eligible folios are placed on a NUMA-node or memcg split queue and counted in per-order stats. `deferred_split_scan()` pins queued folios in batches, drops them from the queue, splits partially mapped or zero-underused folios when possible, and requeues partially mapped folios that could not be processed. `reparent_deferred_split_queue()` moves queued folios from a dying memcg to its parent.

Debugfs flow is available under `CONFIG_DEBUG_FS` through `split_huge_pages`. Writes can request splitting all LRU THPs, THPs in a PID virtual-address range, or file-backed THPs over file offsets. The parser accepts optional target `new_order` and `in_folio_offset` values, then calls the same folio splitting APIs used by reclaim and MM paths.

## State and Persistence Behavior

This file maintains kernel-resident runtime state only; it does not persist data across reboot. State is exposed and mutated through boot parameters, sysfs, debugfs, VM counters, and shrinker queues.

Persistent runtime state includes global THP flags, anonymous order policy bitmaps, per-order per-CPU stats, huge zero folio state, the `split_underused_thp` policy, and deferred split queues. The huge zero folio can either be shrinkable or persistent depending on `CONFIG_PERSISTENT_HUGE_ZERO_FOLIO`. Non-persistent mode tracks per-mm use with `MMF_HUGE_ZERO_FOLIO`; the shrinker frees the global zero folio only when the refcount indicates that only the shrinker-held reference remains.

Folio and mapping state changes are durable only in memory: rmap entries, page-cache xarray slots, swapcache replacement, LRU membership, memcg refs, page-owner tags, dirty/accessed bits, userfaultfd write-protect bits, soft-dirty bits, migration entries, and mm counters are updated as THPs are mapped, copied, moved, zapped, split, or migrated. File-backed dirty state can propagate to normal writeback accounting when split pages beyond EOF or dirty file THPs are handled.

## Dependencies and Integration Points

Build integration is through `mm/Makefile`, which builds `huge_memory.o` and `khugepaged.o` under `CONFIG_TRANSPARENT_HUGEPAGE`. Public declarations and policy macros live in `include/linux/huge_mm.h`. Kconfig controls global THP defaults, shmem/tmpfs hugepage defaults, PUD hugepage support, THP migration, read-only filesystem THP support, debugfs, sysfs, memcg, persistent huge zero folio, userfaultfd, and architecture page-table capabilities.

Major kernel subsystem dependencies:

- Page fault and VMA management: `vm_fault`, `vm_area_struct`, `vm_flags`, `anon_vma`, `mmap_lock`, `vma_lookup()`, `vmf_anon_prepare()`, and VMA lock retry handling.
- Page-table architecture hooks: PMD/PUD lock helpers, huge leaf builders, deposited page tables, TLB flush helpers, cache update hooks, `arch_needs_pgtable_deposit()`, and huge-leaf capability macros.
- Rmap and migration: anonymous/file rmap add/remove helpers, anon-exclusive handling, migration/device-private swp entries, `try_to_migrate()`, `remove_migration_ptes()`, and NUMA migration helpers.
- Reclaim and memory accounting: LRU vectors, shrinkers, memcg split queues, vmstat/mthp stats, mm counters, `set_recommended_min_free_kbytes()`, and OOM/reclaim-facing split APIs.
- Page cache and filesystems: address-space xarray, mapping min-order, `mapping_large_folio_support()`, `filemap_release_folio()`, `filemap_nr_thps_dec()`, shmem accounting and hugepage policy, read-only regular-file THP, DAX, and PFNMAP/MIXEDMAP mappings.
- MMU notifiers and accelerators: invalidation ranges around huge PMD clear/replace operations keep secondary MMUs, KVM, device memory, and GUP-fast interactions coherent.
- Userfaultfd and soft-dirty: missing faults, write-protect propagation, move operations, and non-present huge PMD state preserve userspace-visible tracking semantics.

## Risks and Edge Cases

- PMD/PUD clear-and-reinstall races are high risk. Several paths explicitly avoid leaving a PMD transiently clear under only `mmap_read_lock()` because concurrent `MADV_DONTNEED` or walkers could skip the range.
- TLB coherence is subtle during splits. The code invalidates huge PMDs before installing PTE tables to avoid simultaneous huge and small TLB entries for the same address, and relies on ordering barriers before publishing populated tables.
- Reference-count assumptions gate folio splitting. Extra GUP pins, DMA pins, unexpected references, writeback, filesystem-private metadata, truncation, swapcache restrictions, or anon-vma disappearance can make split return `-EAGAIN`, `-EBUSY`, or `-EINVAL`.
- Anonymous order 1 is deliberately unsupported because THP deferred-list storage uses subpage metadata that an order-1 anonymous folio cannot provide.
- Huge zero folio lifetime depends on atomic refcount discipline. Incorrect `MMF_HUGE_ZERO_FOLIO` handling or shrinker races could leak or free the global zero folio incorrectly.
- Device-private and migration entries require preservation of writable, young, dirty, soft-dirty, uffd-wp, and anon-exclusive semantics across PMD-to-PTE splits and migration removal.
- File THP splitting must honor `mapping_min_folio_order()` and filesystem large-folio support. Splitting below a mapping's minimum order or assuming large-folio support for read-only collapsed THPs can corrupt page-cache expectations.
- Debugfs split controls are powerful and intentionally low-level. They can force broad THP splitting across the system, by PID, or by file, so failures and partial progress are normal when locks, references, or mapping constraints block splits.
- Memcg reparenting creates a window where a dying memcg's deferred split queue must be avoided or redirected; the queue-lock helpers retry against the parent to prevent folios becoming invisible to shrinkers.

## Test Signals

Useful validation signals for changes touching this file:

- Boot with `CONFIG_TRANSPARENT_HUGEPAGE=y` and check `/sys/kernel/mm/transparent_hugepage/enabled`, `defrag`, `use_zero_page`, `shrink_underused`, and per-size `hugepages-<size>kB/enabled` and `stats/*`.
- Exercise boot parameters `transparent_hugepage=always|madvise|never` and `thp_anon=<range>:<policy>` and verify sysfs policy reflects parsed state.
- Run anonymous THP allocation/COW tests: read-fault huge zero PMD, write fault replacement, fork COW on THP, `MADV_HUGEPAGE`, `MADV_NOHUGEPAGE`, `MADV_FREE`, and `MADV_DONTNEED`.
- Monitor `/proc/vmstat` events such as `THP_FAULT_ALLOC`, `THP_FAULT_FALLBACK`, `THP_ZERO_PAGE_ALLOC`, `THP_SPLIT_PAGE`, `THP_SPLIT_PAGE_FAILED`, `THP_DEFERRED_SPLIT_PAGE`, and `THP_UNDERUSED_SPLIT_PAGE`.
- Run multi-size THP tests that verify per-order mTHP stats, fallback-charge accounting, and `split_folio()` behavior for uniform and non-uniform splits.
- Use `tools/testing/selftests/mm` style coverage for THP, `mremap`, `userfaultfd`, soft-dirty, NUMA balancing, migration, GUP pinning, and hugepage split behavior.
- With memcg enabled, allocate THPs inside cgroups, trigger partial unmaps and memory pressure, then verify deferred split shrinker counts, reparenting on cgroup removal, and stat consistency.
- For file-backed paths, test read-only regular file THP, shmem/tmpfs hugepage policy, DAX/special mapping exclusion, truncation around large folios, and splitting through debugfs file-offset commands.
- Under `CONFIG_ARCH_ENABLE_THP_MIGRATION`, validate PMD migration entry install/removal, device-private migration, NUMA migration, and dirty/young/uffd-wp/soft-dirty preservation.
