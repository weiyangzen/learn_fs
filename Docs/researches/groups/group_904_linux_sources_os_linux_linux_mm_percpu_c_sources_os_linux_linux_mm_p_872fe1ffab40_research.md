# Group Research: group_904_linux_sources_os_linux_linux_mm_percpu_c_sources_os_linux_linux_mm_p_872fe1ffab40

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This grouped report covers the listed Linux `mm/` source files. Each file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/percpu.c -->
# File Research: sources/os/linux/linux/mm/percpu.c

## Purpose

`mm/percpu.c` implements Linux's generic percpu memory allocator. It manages static percpu data initialized during boot, optional reserved percpu space for module/static uses, and dynamic percpu allocations served through `pcpu_alloc_noprof()` / `free_percpu()`.

## Main Structures and State

Global geometry includes `pcpu_unit_pages`, `pcpu_unit_size`, `pcpu_nr_units`, `pcpu_unit_map`, `pcpu_unit_offsets`, group offsets/sizes, and `pcpu_base_addr`. Chunk state is centered on `pcpu_first_chunk`, optional `pcpu_reserved_chunk`, `pcpu_chunk_lists`, and special slots for free, sidelined, and depopulation candidates. `pcpu_lock` protects allocator structures; `pcpu_alloc_mutex` serializes sleeping chunk creation/destruction and population/depopulation work.

## Allocation and Freeing

Chunks use `alloc_map` and `bound_map` bitmaps. Metadata blocks track `first_free`, contiguous free hints, scan hints, and left/right free runs. `pcpu_alloc_noprof()` normalizes size/alignment, performs memcg precharge when needed, searches reserved or normal chunk slots, creates chunks for sleepable allocations if necessary, populates missing backing pages, zeroes the area for every possible CPU, and returns the percpu pointer. `free_percpu()` finds the owning chunk, frees the bitmap area, updates memcg/allocation profiling hooks, and schedules balance work when chunks become free or reclaimable.

## Reclaim and Boot Setup

`pcpu_balance_workfn()` frees excess empty chunks, depopulates empty populated pages from isolated chunks, maintains a small reserve for atomic allocations, and destroys fully depopulated chunks. `pcpu_setup_first_chunk()` initializes the static/reserved/dynamic first chunk layout from `struct pcpu_alloc_info`. SMP helpers build embedded or page-mapped first chunks; UP uses a simple km-based identity mapping.

## Filesystem/MM Relevance

This allocator backs per-CPU state used throughout VFS, page cache, block I/O, writeback, and MM. Its GFP behavior, memcg charging, and atomic allocation constraints matter when filesystem paths allocate percpu structures under reclaim or `GFP_NOFS`/`GFP_NOIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/pgalloc-track.h -->
# File Research: sources/os/linux/linux/mm/pgalloc-track.h

## Purpose

`mm/pgalloc-track.h` provides inline page-table allocation helpers that also update a `pgtbl_mod_mask`.

## Helpers

Under `CONFIG_MMU`, `p4d_alloc_track()`, `pud_alloc_track()`, and `pmd_alloc_track()` allocate missing page-table levels and set the matching `PGTBL_*_MODIFIED` bit. `pte_alloc_kernel_track()` does the same for kernel PTE tables under a PMD.

## Behavior

Existing entries are returned without marking modification. Allocation failures return `NULL`. The helpers rely on normal page-table locking and allocation rules supplied by their callers.

## Filesystem/MM Relevance

These helpers support MM paths that need to know whether page tables changed, such as mapping installation, page-table accounting, TLB/cache maintenance, and notifier-sensitive operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/pgalloc-track.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/pgtable-generic.c -->
# File Research: sources/os/linux/linux/mm/pgtable-generic.c

## Purpose

`mm/pgtable-generic.c` supplies generic fallback implementations for page-table operations that architectures may override.

## Key Areas

It provides bad-entry clearing for PGD/P4D/PUD/PMD levels, generic PTE accessed/dirty/write access updates, clear-and-flush helpers, transparent huge page PMD/PUD access helpers, huge clear/invalidate paths, and THP page-table deposit/withdraw support.

## PTE Mapping

`__pte_offset_map()` and the `pte_offset_map_*()` helpers safely map PTE tables under RCU, reject none/non-present/THP/bad PMDs, and provide correct page-table lock pointers. `pte_offset_map_lock()` retries if the PMD changes after acquiring the PTE lock.

## Deferred Freeing

If an architecture does not provide `pte_free_defer`, this file queues PTE table freeing through RCU. With `CONFIG_ASYNC_KERNEL_PGTABLE_FREE`, kernel page tables can be freed asynchronously after IOMMU KVA invalidation.

## Filesystem/MM Relevance

Filesystem-backed mmap fault, dirty tracking, reclaim, migration, THP split/collapse, and page-table teardown all depend on these generic page-table operations and their TLB synchronization rules.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/pgtable-generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/process_vm_access.c -->
# File Research: sources/os/linux/linux/mm/process_vm_access.c

## Purpose

`mm/process_vm_access.c` implements `process_vm_readv(2)` and `process_vm_writev(2)`.

## Flow

`process_vm_rw()` validates flags, imports local and remote iovecs, and delegates to `process_vm_rw_core()`. The core routine looks up the target task, obtains its mm through `mm_access(..., PTRACE_MODE_ATTACH_REALCREDS)`, and processes each remote iovec. Remote pages are pinned in bounded batches with `pin_user_pages_remote()`, copied through iterator helpers, and unpinned with dirty marking for writes.

## Semantics

The syscall returns bytes copied if any progress occurred; otherwise it returns the error code. Temporary page-pointer storage uses a small stack array and only kmallocs larger bounded arrays when needed.

## Filesystem/MM Relevance

The code interacts with filesystem-backed mappings via GUP, faults, dirty tracking, and writeback semantics when remote writes dirty mapped file pages.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/process_vm_access.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/ptdump.c -->
# File Research: sources/os/linux/linux/mm/ptdump.c

## Purpose

`mm/ptdump.c` implements generic page-table dumping support around `mm_walk` and exposes a debugfs W+X check.

## Walk Logic

Callbacks inspect PGD, P4D, PUD, PMD, and PTE entries, call optional effective-protection hooks, and report leaf or hole entries to `struct ptdump_state`. KASAN shadow page tables are optimized by reporting the early shadow PTE directly instead of descending through large shadow regions.

## Public Interface

`ptdump_walk_pgd()` walks configured ranges under `get_online_mems()` and `mmap_write_lock(mm)`, then flushes the final accumulated state. `check_wx_pages` is created in debugfs and reports `SUCCESS` or `FAILED` from `ptdump_check_wx()`.

## Filesystem/MM Relevance

This is diagnostic MM infrastructure for inspecting kernel mappings and validating permission properties such as writable-and-executable mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/ptdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/readahead.c -->
# File Research: sources/os/linux/linux/mm/readahead.c

## Purpose

`mm/readahead.c` implements page-cache readahead for file reads and faults, including sync readahead, async readahead, forced readahead, large-folio readahead, `readahead_expand()`, and the `readahead(2)` syscall.

## Core Model

`struct file_ra_state` tracks the latest window: start, total size, async tail size, maximum pages, previous read position, and folio order. The first folio in the async tail is marked with `PG_readahead`; access to that folio triggers the next async window.

## I/O Submission

`read_pages()` submits prepared folios through `a_ops->readahead()` when present, otherwise through `a_ops->read_folio()`. It removes ignored folios, wraps submission in a block plug, and accounts PSI memstall when workingset folios are involved.

## Window Management

`page_cache_sync_ra()` handles demand misses using start-of-file, sequential, oversized, or cached-history heuristics. `page_cache_async_ra()` handles marked folio hits, grows the window, and recovers from interleaved reads by probing for cache misses. `page_cache_ra_order()` allocates large folios when supported and falls back to base readahead on conflicts.

## Syscall and Expansion

`ksys_readahead()` validates the fd, mapping, file type, and anonymous-file status, then delegates to `vfs_fadvise(..., POSIX_FADV_WILLNEED)`. `readahead_expand()` lets filesystems enlarge an existing request by inserting locked folios before or after the current window.

## Filesystem/MM Relevance

This file defines how filesystem `->readahead()` implementations receive prepared folios, how page-cache insertion is coordinated with `invalidate_lock`, and how read performance is shaped by congestion, large folios, and sequential-read detection.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/readahead.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/rmap.c -->
# File Research: sources/os/linux/linux/mm/rmap.c

## Purpose

`mm/rmap.c` implements reverse mapping: finding virtual mappings for physical folios/pages. It supports anonymous VMA ancestry, file and anon rmap walks, mapcount accounting, referenced/dirty/write-protect operations, reclaim unmapping, migration entries, device-exclusive mappings, and hugetlb anonymous rmap.

## Anonymous VMA Lifecycle

The file manages `anon_vma` and `anon_vma_chain` allocation, clone, fork, prepare, unlink, and free paths. Fork links child VMAs into parent anon-vma trees so rmap can find shared pre-COW pages while allowing COWed pages to move to a more specific anon_vma.

## Rmap Walking

`rmap_walk()` dispatches to KSM, anon, or file-backed walkers. Anonymous walks iterate `anon_vma_interval_tree`; file walks iterate `mapping->i_mmap`. Walk controls support invalid-VMA filters, try-lock contention reporting, early stop callbacks, and caller-held rmap locks.

## Accounting and Aging

`__folio_add_rmap()` and `__folio_remove_rmap()` update page/folio mapcounts, large-folio mapcounts, PMD/PUD entire-mapcount state, and VM statistics. `folio_referenced()` walks mappings to clear young/accessed state, handle mlocked VMAs, integrate with MGLRU, and report referenced mappings.

## Dirty, Unmap, and Migration

`folio_mkclean()`, `mapping_wrprotect_range()`, and `pfn_mkclean_range()` clear dirty/writable PTEs or PMDs with MMU notifier synchronization. `try_to_unmap()` removes mappings for reclaim or memory failure, handling mlock, lazyfree, swap entries, userfaultfd markers, dirty propagation, hwpoison, file RSS, and batched TLB flushes. `try_to_migrate()` replaces mappings with migration entries while preserving writable/exclusive/young/dirty/soft-dirty/uffd-wp metadata.

## Device and Hugetlb Paths

With `CONFIG_DEVICE_PRIVATE`, `make_device_exclusive()` converts a writable anonymous PTE into a device-exclusive PFN swap entry after MMU notifier invalidation. Hugetlb helpers maintain anonymous hugepage rmap and exclusivity state separately from normal LRU/accounting rules.

## Filesystem/MM Relevance

This is a core bridge between filesystem page cache and VM. Filesystems rely on it for mmap dirty tracking, writeback preparation, truncation/invalidation coordination, reclaim unmapping, migration, and file-backed VMA traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/rodata_test.c -->
# File Research: sources/os/linux/linux/mm/rodata_test.c

## Purpose

`mm/rodata_test.c` is a small functional test for kernel read-only data protection.

## Test Flow

`rodata_test()` verifies that `rodata_test_data` starts with the expected value, attempts a nofault kernel write that should fail, confirms the value did not change, and checks that `__start_rodata` and `__end_rodata` are page-aligned.

## Filesystem/MM Relevance

This is MM hardening validation. It verifies that kernel `.rodata` mappings are read-only and page-aligned.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/rodata_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/secretmem.c -->
# File Research: sources/os/linux/linux/mm/secretmem.c

## Purpose

`mm/secretmem.c` implements `memfd_secret(2)`, creating anonymous file descriptors whose mappings allocate pages removed from the kernel direct map.

## Fault and Mapping Behavior

`secretmem_fault()` allocates zeroed order-0 folios, invalidates their direct-map alias before page-cache insertion, marks them uptodate, inserts them into the file mapping, and flushes the kernel TLB range. Existing folios are locked and returned. Error paths restore direct-map state when insertion fails.

`secretmem_mmap_prepare()` requires shared mapping capability, sets locked and nondumpable VMA flags, checks `mlock_future_ok()`, and installs `secretmem_vm_ops`.

## File and Address-Space Operations

`secretmem_file_create()` creates a secure anonymous inode on an internal pseudo mount, sets the mapping GFP mask to `GFP_HIGHUSER`, marks it unevictable, installs inode/address-space operations, and increments `secretmem_users`. The address-space operations refuse migration, use `noop_dirty_folio`, and restore direct-map state plus zero the folio on free. `secretmem_setattr()` only permits sizing while the inode size is still zero.

## Syscall and Init

`memfd_secret()` rejects unsupported flags, disabled configurations, or architectures without direct-map controls, then creates the file and installs an fd with optional `O_CLOEXEC`. `secretmem_init()` mounts the internal pseudo filesystem during `fs_initcall`.

## Filesystem/MM Relevance

Secretmem is implemented as a pseudo filesystem plus file-backed mapping while enforcing MM secrecy properties: direct-map removal, locked unevictable pages, no migration, no core dump, and controlled fault-time allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/secretmem.c -->