# sources/distributed-fs/ceph-client/mm/memory.c

## Purpose

`memory.c` is a Linux `mm/memory.c` snapshot placed under the Ceph client source tree. It is not Ceph-specific code; it supplies the generic virtual-memory machinery that a filesystem client such as Ceph relies on when user processes `mmap()` files, fault file-cache folios into userspace, dirty shared mappings, truncate or invalidate mapped pages, and tear down process address spaces.

The file owns core page-table operations for normal user mappings: page-table allocation/freeing, fork-time page-table copying, VMA unmapping/zapping, driver PFN/page insertion, physical remapping helpers, page-fault dispatch, copy-on-write, swap-in, NUMA hinting faults, transparent huge page fallbacks, remote process memory access, and page-table lock allocation.

## Important APIs, Types, and Functions

Important data types are mostly generic MM structures supplied by included Linux headers:

- `struct mm_struct`, `struct vm_area_struct`, `struct vm_fault`, and `struct mmu_gather` model address spaces, VMAs, fault context, and deferred TLB/page-table freeing.
- Page-table entry types `pgd_t`, `p4d_t`, `pud_t`, `pmd_t`, and `pte_t` are traversed throughout the file.
- `struct page` and `struct folio` are the physical memory units whose mappings, refcounts, rmap state, dirty/accessed state, LRU membership, swap-cache state, and memory-cgroup charges are maintained here.
- `struct zap_details`, `struct unmap_desc`, `struct follow_pfnmap_args`, `struct vm_area_desc`, and `struct mmap_action` parameterize unmap, batched mmap setup, PFN lookup, and remap operations.

Page-table lifetime APIs:

- `free_pgd_range()`, `free_pgtables()`, and lower helpers free page-table levels after mappings have already been removed.
- `pmd_install()`, `__pte_alloc()`, `__pte_alloc_kernel()`, `__p4d_alloc()`, `__pud_alloc()`, and `__pmd_alloc()` allocate and publish page-table pages with the required locking and write barriers.
- `apply_to_page_range()` and `apply_to_existing_page_range()` walk page-table leaves and invoke a caller-supplied `pte_fn_t`, optionally allocating missing tables.

Fork/copy APIs:

- `copy_page_range()` is the exported fork-time page-table copier. It uses `vma_needs_copy()` to skip lazily faultable VMAs, handles hugetlb separately, and wraps COW permission downgrades with MMU notifier invalidations.
- `copy_pte_range()`, `copy_present_ptes()`, and `copy_nonpresent_pte()` copy present PTEs, swap entries, migration entries, device-private/exclusive entries, and PTE markers while updating RSS counters and rmap state.

Unmap/zap APIs:

- `unmap_vmas()`, `zap_vma_range_batched()`, `zap_vma_range()`, `zap_special_vma_range()`, `zap_vma_for_reaping()`, and `__zap_vma_range()` remove mappings over VMA ranges.
- `zap_pte_range()`, `zap_present_ptes()`, and `zap_nonpresent_ptes()` clear PTEs, remove reverse mappings, decrement RSS/swap counters, install userfaultfd write-protect markers when required, and batch TLB/rmap work.
- `unmap_mapping_folio()`, `unmap_mapping_pages()`, and `unmap_mapping_range()` unmap file-backed mappings through an address_space's `i_mmap` interval tree, which is the key integration point for filesystem truncation and page-cache invalidation.

Driver and PFN mapping APIs:

- `vm_insert_page()`, `vm_insert_pages()`, `vm_map_pages()`, `vm_map_pages_zero()`, `vmf_insert_page_mkwrite()`, `vmf_insert_pfn()`, `vmf_insert_pfn_prot()`, `vmf_insert_mixed()`, and `vmf_insert_mixed_mkwrite()` let drivers place specific pages or PFNs into user VMAs.
- `remap_pfn_range()`, `remap_pfn_range_prepare()`, `remap_pfn_range_complete()`, `vm_iomap_memory()`, and `simple_ioremap_prepare()` map physical memory ranges to userspace, with optional PFN tracking and cache-mode validation.
- `follow_pfnmap_start()` and `follow_pfnmap_end()` safely inspect IO/PFN mappings while holding the relevant page-table lock.

Fault handling APIs:

- `handle_mm_fault()` is the public page-fault entry point. It validates fault flags and VMA access permissions, handles memcg fault state and LRU-generation tracking, routes hugetlb faults to `hugetlb_fault()`, and otherwise calls `__handle_mm_fault()`.
- `__handle_mm_fault()` walks or allocates upper page-table levels, tries huge PUD/PMD fault handling, handles huge-page write protection/NUMA cases, and falls back to `handle_pte_fault()`.
- `handle_pte_fault()` dispatches PTE-level faults to missing-page handling, swap/device/migration/marker handling, NUMA hinting, write-protect handling, or access/dirty-bit updates.
- `do_anonymous_page()`, `do_fault()`, `do_read_fault()`, `do_cow_fault()`, `do_shared_fault()`, `finish_fault()`, `set_pte_range()`, `do_wp_page()`, `wp_page_copy()`, and `do_swap_page()` implement anonymous allocation, file faults, COW, shared write faults, PTE installation, write-protect faults, and swap-in.

Utility and diagnostics:

- `vm_normal_page()`, `vm_normal_folio()`, and huge-leaf variants classify whether a mapping has an ordinary refcounted `struct page`.
- `print_bad_page_map()` and `print_bad_pte()` report corrupt or invalid mappings with rate limiting and tainting.
- `mm_account_fault()` updates VM, memcg, task, and perf page-fault counters.
- `access_remote_vm()`, `access_process_vm()`, and, under BPF, `copy_remote_vm_str()` copy data from another process by using GUP or VMA `access` callbacks.
- `folio_zero_user()`, `copy_user_large_folio()`, and `copy_folio_from_user()` optimize zeroing/copying of large folios and huge pages.
- `ptlock_cache_init()`, `ptlock_alloc()`, and `ptlock_free()` manage split page-table lock storage when configured.

## Control Flow

Page-table teardown starts after VMAs have been unmapped. `free_pgtables()` iterates the `unmap_desc` maple tree state, unlinks anonymous and file VMA metadata, batches adjacent VMAs, then calls `free_pgd_range()`. The free path descends from PGD to PTE, clears each page-table pointer, queues page-table pages in the `mmu_gather`, and decrements per-mm page-table counters. Boundary checks around `floor` and `ceiling` prevent freeing page-table pages still shared by neighboring VMAs.

Fork-time copying begins in `copy_page_range()`. The path skips VMAs whose mappings can be recreated lazily, routes hugetlb VMAs to hugetlb code, and uses MMU notifiers plus `write_protect_seq` when private COW mappings require parent PTE write-protection. It walks page-table levels and copies PTEs in `copy_pte_range()`. Present folio mappings are either refcounted and rmap-duplicated or copied into a preallocated anonymous folio when pinned/exclusive constraints require it. Non-present entries duplicate swap references, preserve or clear userfaultfd write-protect metadata, restore device-exclusive entries if necessary, and copy PTE markers when meaningful.

Unmapping flows through `unmap_vmas()` or the `zap_*()` APIs. Callers initialize an `mmu_notifier_range`, gather TLB work, and descend to `zap_pte_range()`. Present PTEs are batched where possible across contiguous folio pages, then cleared, removed from the TLB batch, removed from rmap, and charged out of RSS. Non-present PTEs handle swap, migration, hwpoison, device-private/exclusive, userfaultfd, poison, and guard markers. The code can reclaim an empty PTE table when the requested zap covers the whole table and no marker or skipped entry prevents reclaim.

File mapping invalidation uses `unmap_mapping_range_tree()` to traverse the `address_space->i_mmap` interval tree. For each VMA range covering the file indices, it gathers a local TLB batch and calls `zap_vma_range_batched()`. `unmap_mapping_folio()` skips private COW pages and targets one locked folio; `unmap_mapping_pages()` and `unmap_mapping_range()` handle broader invalidation or truncation and choose whether COWed private pages are also removed.

The normal page-fault entry is `handle_mm_fault()`. It sanitizes impossible write/unshare flag combinations, checks architecture VMA permissions, enters memcg user-fault state, then dispatches to hugetlb or `__handle_mm_fault()`. The lower fault path walks PGD/P4D/PUD/PMD levels, tries transparent huge PUD/PMD faults, handles huge-page migration/device-private/NUMA/write-protect cases, and falls back to PTE handling.

`handle_pte_fault()` treats an absent PTE as either anonymous allocation or file fault. A non-present PTE is handled by `do_swap_page()`, including migration waits, device-private migration back to RAM, device-exclusive restoration, PTE marker interpretation, swap-cache lookup or readahead, memcg charging, rmap insertion, and optional write-protect follow-up. A present NUMA-protnone PTE goes to `do_numa_page()`. A write or unshare fault on a read-only PTE goes to `do_wp_page()`, which either reuses an exclusive anonymous folio, handles shared `page_mkwrite`/`pfn_mkwrite`, or allocates and installs a copied anonymous folio.

File faults are handled by `do_fault()`. Missing read faults can first call `vm_ops->map_pages()` for fault-around; otherwise `__do_fault()` invokes the filesystem or driver `vm_ops->fault()` callback. `finish_fault()` then installs a PTE or PMD mapping, with fallbacks that preserve SIGBUS semantics at file EOF and userfaultfd per-page behavior. Shared write faults call `page_mkwrite()` before dirtying, and COW faults preallocate the private folio before invoking the file fault path.

## State and Persistence Behavior

This code persists virtual-memory state in process page tables and associated kernel accounting, not in an on-disk format. Durable filesystem data is affected indirectly through dirtying and writeback interactions.

State updated here includes:

- Page-table contents at all levels, including present PTEs, huge PMD/PUD entries, swap entries, migration entries, device-private/exclusive entries, guard markers, poisoned markers, and userfaultfd write-protect markers.
- Per-mm RSS counters, swap-entry counters, page-table counters, high-water RSS, task minor/major fault counters, VM event counters, memcg event counters, and perf software fault counters.
- Folio/page state: refcounts, mapcounts, rmap entries, LRU membership, dirty/accessed bits, uptodate state, swap-cache references, KSM/COW exclusivity, NUMA cpupid/access metadata, and memory-cgroup charges.
- VMA state such as `VM_MIXEDMAP`, `VM_PFNMAP`, remap flags, `vm_pgoff`, PFN tracking context, and anon_vma attachment.
- Global tunables: `randomize_va_space` via the `kernel.randomize_va_space` sysctl and boot-time `norandmaps`; `fault_around_pages` via debugfs when enabled.

Dirty shared file mappings are especially important for persistence. `do_page_mkwrite()`, `finish_mkwrite_fault()`, and `fault_dirty_shared_page()` coordinate `vm_ops->page_mkwrite`, `folio_mark_dirty()`, `file_update_time()`, mmap-lock release around IO throttling, and `balance_dirty_pages_ratelimited()`. Filesystems such as Ceph participate through `vm_operations_struct` and `address_space_operations`; this generic code ensures dirtying is visible to the page cache and writeback policy but does not itself send data to Ceph OSDs.

## Dependencies

The file depends on nearly every core MM subsystem:

- Page-table architecture hooks: `set_pte_at`, `ptep_get`, TLB flush APIs, `update_mmu_cache*`, `pfn_modify_allowed`, `flush_cache_*`, huge-page accessors, and architecture-specific swap restore.
- Memory management subsystems: rmap, LRU, KSM, memcg, swap, zswap, migration, mlock, NUMA balancing, transparent huge pages, hugetlb, DAX, userfaultfd, MMU notifiers, page-table allocation, and page-table lock infrastructure.
- Filesystem/page-cache interfaces: `struct address_space`, `vm_ops->fault`, `map_pages`, `page_mkwrite`, `pfn_mkwrite`, `huge_fault`, `find_normal_page`, `a_ops->read_folio`, `i_mmap`, `file_update_time()`, and dirty/writeback throttling.
- Driver and IO interfaces: PFN mappings, `ioremap_prot`, `memremap`, `dev_pagemap`, device-private migration, device-exclusive entries, and raw IO VMA access callbacks.
- Kernel observability and control: tracepoints, debugfs, perf events, delay accounting, sysctl registration, and kernel warning/taint facilities.

## Integration Points

For a distributed filesystem client, the most relevant integration is mmap/page-cache behavior:

- File-backed faults call the filesystem-provided `vma->vm_ops->fault()` and optionally `map_pages()`, `page_mkwrite()`, or `huge_fault()`. A Ceph file mapping would enter this code through the generic VM fault path and then rely on Ceph's address_space and VMA operations to fetch or prepare file data.
- Shared writable mappings call `page_mkwrite()` before PTEs become writable. This is where a filesystem can serialize against truncation, snapshots, layout changes, writeback, or distributed coherency state before userspace modifies a mapped page.
- Truncate, hole-punch, cache invalidation, and remote coherence invalidations use `unmap_mapping_pages()` or `unmap_mapping_range()` to zap userspace mappings from an `address_space`.
- Dirty accounting and `balance_dirty_pages_ratelimited()` integrate mmap writes with writeback throttling, which ultimately controls how aggressively filesystem dirty data is flushed.
- MMU notifiers protect secondary MMUs such as KVM, device memory mirrors, and GPU mappings whenever page permissions or mappings are removed.
- Driver-facing mapping helpers are used by non-filesystem device mappings and DAX-like paths; DAX and PFNMAP/MIXEDMAP rules are explicitly handled to avoid treating special mappings as normal refcounted pages.

## Risks and Edge Cases

Concurrency is the dominant risk. Many paths intentionally drop and reacquire page-table locks, folio locks, VMA locks, or the mmap lock. They must revalidate PTEs with `pte_same()`, handle transient `pte_offset_map*()` failure, and avoid dereferencing a VMA after a fault handler may have dropped the mmap lock.

TLB and rmap ordering are fragile. `wp_page_copy()` clears and flushes the old PTE before installing the new one so stale TLBs cannot access an old page after mapcount changes make it reusable. Zap paths sometimes force TLB flushes before dropping locks when delayed rmap removal or batch limits require it.

COW and exclusivity handling has many special cases: pinned anonymous pages must be copied instead of shared with the child, swap exclusive markers can be invalidated by stable-writeback requirements, KSM can require copy-on-read, userfaultfd write-protect bits must be propagated or cleared according to the destination VMA, and anonymous large folios can only be reused when refcount/mapcount invariants prove exclusivity.

Filesystem correctness depends on `page_mkwrite()` and invalidation discipline. If a filesystem returns from `page_mkwrite()` without protecting against truncation or distributed invalidation, this generic code can legally make a PTE writable and dirty the folio. Conversely, incorrect invalidation ranges can leave stale user mappings to page-cache folios.

Special mappings are easy to misclassify. `vm_normal_page()` treats PFNMAP, MIXEDMAP, zero pages, special PTEs, and device pages differently depending on architecture support for `pte_special`. Incorrect flags or refcount expectations can lead to bad map reports, leaks, or use-after-free.

Large folios and THP paths preserve userfaultfd semantics, EOF SIGBUS semantics, page-table boundary constraints, and hwpoison isolation by falling back to per-page mappings when necessary. Regressions here typically surface only under mixed large-folio, mmap, truncation, and fault-around workloads.

Remote access helpers deliberately avoid raw page-table walks for normal memory and use GUP or VMA `access` callbacks. Callers that retain PFNs from `follow_pfnmap_start()` after `follow_pfnmap_end()` need their own invalidation synchronization, as noted by the in-code security warning.

## Test Signals

Useful validation signals for this file are broad MM and filesystem mmap tests rather than Ceph-only unit tests:

- Fork/COW: fork-heavy workloads, private writable file mappings, pinned-page fork tests, KSM COW tests, and `FAULT_FLAG_UNSHARE`/GUP interactions.
- Fault handling: anonymous read/write faults, file read faults, shared mmap write faults, `page_mkwrite()` failures, EOF SIGBUS behavior, fault-around coverage, and retry paths where the mmap lock is dropped.
- Swap: swap-in/out under memory pressure, swapoff races, swapcache exclusivity, zswap enabled/disabled, synchronous swap devices, hwpoisoned swapcache pages, and large-folio swap-in fallback.
- Unmap/invalidation: `munmap`, `mremap`, truncation, hole punching, page-cache invalidation, OOM reaper `zap_vma_for_reaping()`, and userfaultfd marker preservation/removal.
- Filesystem mmap: shared writable mmap on a Ceph-like network filesystem, truncation racing mmap writes, invalidation from remote updates, dirty-page throttling, and page-cache writeback visibility.
- THP/large folios: file THP faults, anonymous multi-size THP faults, huge PMD/PUD fallback, large-folio PTE batch mapping, and hwpoison within a large folio.
- NUMA: NUMA balancing hint faults, misplaced folio migration, writable restoration after protnone, and shared-vs-private grouping flags.
- Device/PFN/DAX: `vm_insert_page(s)`, `vmf_insert_pfn*`, `remap_pfn_range`, DAX `pfn_mkwrite`, IO VMA `access`, device-private migration to RAM, and device-exclusive restoration.
- Observability: `PGFAULT`, `PGMAJFAULT`, task `min_flt`/`maj_flt`, memcg fault events, THP mapped counters, bad PTE warnings, suppressed bad-page-map reports, debugfs `fault_around_bytes`, and lockdep assertions around PFN map following.
