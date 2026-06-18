# Group Research: group_893_linux_sources_os_linux_linux_mm_ksm_c_sources_os_linux_linux_mm_list_74e554330aeb

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/ksm.c -->
# File Research: sources/os/linux/linux/mm/ksm.c

Linux Kernel Samepage Merging implementation. This file owns the `ksmd` scanner, KSM reverse-map metadata, stable and unstable content trees, KSM page replacement, KSM page reverse mapping, KSM sysfs controls, process/VMA enablement hooks, and memory hotplug/migration integration.

Key responsibilities:
- Defines KSM metadata structures: `ksm_mm_slot`, `ksm_scan`, `ksm_stable_node`, and `ksm_rmap_item`.
- Maintains stable and unstable RB trees, optionally per NUMA node when `merge_across_nodes` is disabled.
- Tracks global KSM accounting: scanned pages, shared nodes, sharing mappings, unshared candidates, volatile rmap items, skipped pages, zero-page mappings, stable-node chains, and duplicate stable nodes.
- Runs the `ksmd` kernel thread, which walks mergeable VMAs, hashes and compares anonymous pages, merges identical pages, and rebuilds unstable trees after full scans.
- Implements the stable tree for write-protected KSM pages and the unstable tree for candidate pages whose checksum remains stable across scans.
- Supports stable-node chains/dups to cap reverse-map list length per KSM page while allowing multiple KSM pages with identical content.
- Handles KSM page creation by write-protecting anonymous pages, replacing PTEs with KSM pages or KSM-placed zero pages, and updating rmap/accounting.
- Handles unmerge paths through `break_ksm()`, `ksm_disable()`, `ksm_madvise(... MADV_UNMERGEABLE)`, and sysfs `run=2`.
- Exposes KSM entry points used by the wider MM: `ksm_vma_flags()`, `ksm_enable_merge_any()`, `ksm_disable_merge_any()`, `ksm_disable()`, `ksm_madvise()`, `__ksm_enter()`, `__ksm_exit()`, `ksm_might_need_to_copy()`, `rmap_walk_ksm()`, `collect_procs_ksm()`, and `folio_migrate_ksm()`.
- Provides `/sys/kernel/mm/ksm` controls and statistics when `CONFIG_SYSFS` is enabled.

Important behavior:
- KSM eligibility excludes shared/may-share VMAs, hugetlb, droppable, special VMAs, DAX mappings, and architecture-specific incompatible flags.
- `MADV_MERGEABLE` registers the `mm` with KSM on first use and marks compatible VMAs with `VM_MERGEABLE`.
- `MMF_VM_MERGE_ANY` enables automatic mergeability for all compatible VMAs in an `mm`; `ksm_vma_flags()` applies it to newly created VMAs.
- `scan_get_next_rmap_item()` is the scanner cursor: it walks mergeable VMAs, finds anonymous pages through a page-table walk, allocates or reuses sorted `ksm_rmap_item` entries, prunes stale rmap items, and advances across mms.
- `cmp_and_merge_page()` is the central merge decision path: it handles existing KSM pages, checksum stability, zero-page merging, stable-tree lookup, unstable-tree lookup/insert, two-page promotion, and stable-tree append.
- Stable-tree lookup uses page content comparison, stale-node pruning via the KSM page mapping back-pointer, NUMA tree placement checks, and max-sharing enforcement.
- The unstable tree is reset each full scan because candidate pages are not write-protected and their content ordering can become stale.
- Smart scanning ages repeatedly unmergeable candidates and skips them for increasing scan intervals while still always processing existing KSM pages.
- KSM pages deliberately avoid holding permanent page references from stable nodes; `ksm_get_folio()` validates the page through the folio mapping tag and removes stale nodes when the page has gone away.
- `write_protect_page()` clears writable/dirty PTE state, handles anon-exclusive sharing, checks mapcount/refcount to avoid racing direct I/O or pins, and records the original PTE for later replacement.
- `replace_page()` swaps an anonymous PTE to a KSM page or marked zero-page PTE, updates anon rmap and mm counters, flushes cache/TLB state, and drops the old folio mapping.
- Reverse-map walking for KSM pages first visits the tracked originating VMAs and then searches forked VMAs sharing the anon_vma.
- Memory hotremove blocks KSM tree scans while memory is going offline and prunes stable nodes whose PFNs fall in an offline range.
- Sysfs controls include `run`, `sleep_millisecs`, `pages_to_scan`, `merge_across_nodes`, `use_zero_pages`, `max_page_sharing`, `smart_scan`, stable-chain pruning, and scan-time advisor settings.
- The scan-time advisor adjusts `pages_to_scan` based on observed scan duration, target scan time, and estimated CPU cost.

Dependencies:
- Core MM: VMAs, anon_vma, page tables, folios, rmap, swap, migration, memory failure, THP splitting, mmu notifiers, TLB/cache flushing, memcg charging, and mm flags.
- Data structures: RB trees, hlist/list primitives, mm-slot helpers, hashtable for `mm` lookup, slab caches.
- Kernel services: kthread/freezer, wait queues, sysfs, memory hotplug notifier, procfs helpers, tracepoints, xxhash, scheduler runtime accounting.
- Public behavior is tightly connected to `madvise.c` for `MADV_MERGEABLE`/`MADV_UNMERGEABLE` and to fork/mmap/exit paths through KSM mm flags.

Notable risks:
- Correctness relies on subtle lock ordering across mmap locks, VMA locks, page-table locks, anon_vma locks, folio locks, `ksm_thread_mutex`, and `ksm_mmlist_lock`.
- Stable nodes intentionally do not pin KSM pages, so stale-node detection depends on the folio mapping tag and memory-ordering with migration.
- Stable-node chain collapse, migration replacement, and duplicate insertion update RB-tree and hlist state in-place; bugs here would corrupt KSM reverse mapping.
- `break_ksm()` can fail with `-ENOMEM` while unmerging, leaving KSM pages for later retry and preventing `VM_MERGEABLE` from being cleared.
- KSM-placed zero pages are tracked via dirty special PTEs and separate accounting, which requires teardown paths to preserve the convention.
- Smart-scan skip state trades CPU for delayed deduplication and can leave candidates untried for several full scans.
- Changing `merge_across_nodes` or `max_page_sharing` is refused while stable pages remain because the stable tree layout/accounting cannot be safely retuned in place.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/ksm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/list_lru.c -->
# File Research: sources/os/linux/linux/mm/list_lru.c

Generic kernel LRU-list infrastructure for shrinkers, with optional per-memcg/per-NUMA accounting and reparenting support.

Key responsibilities:
- Provides exported operations to add, delete, isolate, move, count, walk, initialize, and destroy `struct list_lru`.
- Maintains one `list_lru_one` per NUMA node for non-memcg LRUs.
- Under `CONFIG_MEMCG`, maintains xarray-indexed per-memcg/per-node `list_lru_memcg` instances.
- Registers memcg-aware LRUs on a global `memcg_list_lrus` list so dying cgroups can reparent all associated LRUs.
- Integrates list activity with shrinker bits through `set_shrinker_bit()`.

Important behavior:
- `list_lru_add()` inserts only if the item list head is empty, increments local and node-wide counts, and sets the shrinker bit when a list transitions from empty.
- `list_lru_del()` removes only if the item is linked and decrements both local and node-wide counts.
- `list_lru_add_obj()` and `list_lru_del_obj()` derive the NUMA node and, when memcg-aware, the memcg from the object address.
- `__list_lru_walk_one()` walks a locked LRU and delegates isolation decisions to a callback returning `LRU_REMOVED`, `LRU_REMOVED_RETRY`, `LRU_ROTATE`, `LRU_SKIP`, `LRU_RETRY`, or `LRU_STOP`.
- `list_lru_walk_node()` first walks the root list for the node, then iterates memcg xarray entries when the LRU is memcg-aware.
- Memcg reparenting moves each dying cgroup's per-node lists into the parent, marks the source `nr_items` as `LONG_MIN`, erases the xarray slot, and frees the memcg LRU after RCU grace.
- `memcg_list_lru_alloc()` ensures a memcg and all not-yet-populated ancestors have list-LRU storage before use.
- `__list_lru_init()` allocates per-node storage, records the shrinker id, disables memcg awareness if kmem accounting is off, initializes locks/lists, and registers the LRU.
- `list_lru_destroy()` unregisters, frees all memcg xarray entries, releases node storage, and resets the shrinker id.

Dependencies:
- Uses `struct list_lru`, `list_lru_node`, `list_lru_one`, and callback semantics from `linux/list_lru.h`.
- Depends on memcg APIs, xarray, RCU, shrinker ids, NUMA node iteration, spin locks, and slab allocation helpers.
- Uses lockdep class assignment when a list LRU provides a lock class key.

Notable risks:
- Callers must ensure memcg lifetime for direct `list_lru_add()`/`list_lru_del()` calls.
- Reparenting races are handled by marking source lists with `LONG_MIN`; code that ignores this sentinel could corrupt lists or counts.
- Walk callbacks may drop the LRU lock for retry states, so traversal restarts and callback contracts must be respected.
- `list_lru_count_one()` clamps negative counts to zero because reparented/dead lists use a negative sentinel.
- Memcg allocation is ancestor-aware and can return xarray allocation errors; callers must be prepared for allocation failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/list_lru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/maccess.c -->
# File Research: sources/os/linux/linux/mm/maccess.c

Fault-suppressed memory access helpers for copying to/from kernel and user addresses from contexts where normal faults must not be taken.

Key responsibilities:
- Provides nofault kernel reads and writes: `copy_from_kernel_nofault()` and `copy_to_kernel_nofault()`.
- Provides nofault string helpers: `strncpy_from_kernel_nofault()`, `strncpy_from_user_nofault()`, and `strnlen_user_nofault()`.
- Provides nofault user copies: `copy_from_user_nofault()` and `copy_to_user_nofault()`.
- Exposes weak arch/filter hook `copy_from_kernel_nofault_allowed()`.
- Exports `__copy_overflow()` warning helper.

Important behavior:
- Kernel nofault copies disable page faults around repeated `__get_kernel_nofault()` or `__put_kernel_nofault()` operations.
- Copy loops choose `u64`, `u32`, `u16`, then `u8` chunks when alignment allows; inefficient unaligned architectures use source/destination alignment to avoid unsafe wide accesses.
- `copy_from_kernel_nofault()` invokes `kmsan_check_memory()` after reading chunks to avoid leaking uninitialized kernel memory.
- `copy_to_kernel_nofault()` invokes `instrument_write()` after stores.
- Kernel string copy always terminates `dst` with NUL on success or fault, returning copied length including the terminating NUL.
- User nofault read checks `__access_ok()` and `nmi_uaccess_okay()` before using `__copy_from_user_inatomic()`.
- User nofault write checks `access_ok()` before using `__copy_to_user_inatomic()`.
- User string copy uses `strncpy_from_user()` with page faults disabled and adjusts return value so success includes the trailing NUL.
- `strnlen_user_nofault()` simply wraps `strnlen_user()` with page faults disabled.

Dependencies:
- Low-level arch uaccess/nofault primitives: `__get_kernel_nofault`, `__put_kernel_nofault`, inatomic user copy helpers, `access_ok`, and `nmi_uaccess_okay`.
- Pagefault disable/enable machinery.
- KMSAN and instrumentation hooks.
- Exported for kernel subsystems that need best-effort probing without faulting.

Notable risks:
- These helpers suppress faults and report `-EFAULT`/zero-style failures; callers must not treat partial destination contents as complete.
- Kernel nofault reads can be filtered by architectures through `copy_from_kernel_nofault_allowed()`, returning `-ERANGE`.
- `strncpy_from_user_nofault()` may copy partial data before returning `-EFAULT`.
- User nofault helpers still depend on architecture-specific inatomic copy correctness in IRQ/NMI-sensitive contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/maccess.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/madvise.c -->
# File Research: sources/os/linux/linux/mm/madvise.c

Linux `madvise(2)` and `process_madvise(2)` implementation. This file validates advice requests, selects locking strategy, walks VMAs, applies per-behavior memory-management actions, supports anonymous VMA naming, and integrates with KSM, THP, userfaultfd, memory failure, reclaim, swapin, guard PTE markers, and remote process advice.

Key responsibilities:
- Implements `do_madvise()`, `SYSCALL_DEFINE3(madvise)`, vectorized `process_madvise`, and anonymous VMA naming support.
- Defines `struct madvise_behavior` state used across validation, locking, VMA walking, and behavior dispatch.
- Implements VMA flag-changing advice: normal/random/sequential, fork inheritance, wipe/keep-on-fork, core-dump inclusion, KSM mergeability, THP policy, and anonymous VMA names.
- Implements page-state advice: `MADV_WILLNEED`, `MADV_COLD`, `MADV_PAGEOUT`, `MADV_FREE`, `MADV_DONTNEED`, `MADV_DONTNEED_LOCKED`, `MADV_REMOVE`, `MADV_POPULATE_READ`, `MADV_POPULATE_WRITE`, and `MADV_COLLAPSE`.
- Implements guard marker operations: `MADV_GUARD_INSTALL` and `MADV_GUARD_REMOVE`.
- Implements optional memory failure injection: `MADV_HWPOISON` and `MADV_SOFT_OFFLINE`.
- Supports remote process advice through `process_madvise()` with pidfd, ptrace access checks, capability checks, and behavior filtering.

Important behavior:
- `madvise_should_skip()` validates behavior, page alignment, length rounding, and overflow before any locking.
- Lock mode is behavior-dependent: some paths take no mmap lock, some take read or write mmap lock, and some try a per-VMA read lock first.
- Per-VMA read locking is limited to local, single-VMA ranges without userfaultfd and without required `anon_vma_prepare()` under only VMA lock.
- `madvise_walk_vmas()` applies advice across all VMAs in range, reports `-ENOMEM` for gaps while still processing mapped VMAs, and handles paths that temporarily drop the mmap lock.
- `madvise_update_vma()` splits/merges VMAs as needed through VMA modification helpers and updates flags or anonymous VMA name under write mmap lock.
- `MADV_WILLNEED` swaps in anonymous/shmem pages or delegates file readahead to `vfs_fadvise()` after taking a file reference and dropping mmap read lock.
- `MADV_COLD` clears referenced/young state and deactivates eligible LRU folios.
- `MADV_PAGEOUT` isolates eligible folios and calls reclaim, with permission filtering for file-backed pagecache to avoid side channels.
- Large folios and THPs are either handled as whole mappings or split when the advised range only covers part of the folio.
- `MADV_FREE` clears swap entries or marks anonymous folios lazyfree after clearing young/dirty PTE state.
- `MADV_DONTNEED`/`MADV_DONTNEED_LOCKED` zap the target VMA range, with hugetlb alignment adjustments and userfaultfd remove notifications.
- `MADV_REMOVE` validates shared writable file mapping semantics and punches a hole with `vfs_fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`.
- `MADV_POPULATE_READ/WRITE` prefaults page tables using `faultin_page_range()` and maps VM fault results into syscall errors.
- Guard installation sets a VMA guard hint bit, optionally prepares anon_vma, tries to install guard PTE markers, and zaps/retries if populated or huge entries race with the install.
- Guard removal clears only guard PTE markers and permits locked VMAs because it is non-destructive.
- Sealed VMA restrictions block destructive discard operations for read-only anonymous sealed mappings unless the operation is otherwise permitted.
- `process_madvise()` only permits remote `MADV_COLD`, `MADV_PAGEOUT`, `MADV_WILLNEED`, and `MADV_COLLAPSE`, and requires `CAP_SYS_NICE` for remote mm influence.
- Anonymous VMA names are capped at 80 bytes and allow printable ASCII except selected shell/metacharacters.

Dependencies:
- Core MM and VMA APIs: maple/VMA iterators, mmap/VMA locks, VMA modification, page walking, zap, TLB gather, mmu notifiers, folio LRU/reclaim helpers, swap, shmem, hugetlb, THP, KSM, userfaultfd, mseal, and memory policy.
- Filesystem APIs: file references, inode permission checks, `vfs_fadvise()`, `vfs_fallocate()`, and DAX detection.
- Syscall/user APIs: iovec import, pidfd task lookup, ptrace-style mm access, capability checks, and user string duplication.
- Architecture hooks for tagged addresses and VMA access permission.

Notable risks:
- Several behaviors intentionally drop and reacquire mmap locks; callers and loops must tolerate VMA invalidation and range truncation after userfaultfd or filesystem operations.
- Per-VMA read-lock fast paths are limited and require careful fallback to mmap locking for multi-VMA, remote, userfaultfd, or anon-vma-preparation cases.
- Guard installation can return restart semantics after repeated races; vectorized `process_madvise()` cannot safely restart the whole aggregate operation and instead retries internally unless interrupted.
- Pageout for file-backed mappings is permission-filtered to avoid side channels, so behavior differs across anonymous, private file, and shared file mappings.
- Hugetlb `MADV_DONTNEED` rounds the end down to hugepage boundaries to avoid surprising data loss.
- Memory failure injection is privileged and compiled only with `CONFIG_MEMORY_FAILURE`.
- Anonymous VMA naming depends on optional `CONFIG_ANON_VMA_NAME`; without it, setting a name is rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/madvise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mapping_dirty_helpers.c -->
# File Research: sources/os/linux/linux/mm/mapping_dirty_helpers.c

Shared mapping dirty-tracking helpers for write-protecting and cleaning PTEs over an `address_space` page-offset range.

Key responsibilities:
- Provides `wp_shared_mapping_range()` to write-protect writable PTEs mapping a shared address-space range.
- Provides `clean_record_shared_mapping_range()` to clear dirty PTEs and record dirty page offsets in a caller bitmap.
- Defines page-walk state for write-protect and clean-record operations, including compact TLB flush ranges.
- Coordinates cache flushing, MMU notifier invalidation, TLB pending accounting, and range TLB flushing around page-table modifications.

Important behavior:
- `wp_pte()` checks each PTE and converts writable entries to read-only with `ptep_modify_prot_start()`/`commit()`, counting only PTEs actually changed.
- `clean_record_pte()` clears dirty PTEs, records the corresponding mapping page offset in the bitmap, and updates first/last modified bitmap bounds.
- PMD/PUD callbacks deliberately do not split transparent huge entries; they warn if huge entries are writable or dirty because tracking is PTE-level.
- `wp_clean_test_walk()` skips VMAs that are not shared, not may-write, or are hugetlb.
- `wp_clean_pre_vma()` initializes MMU notifier range, starts invalidation, flushes caches, initializes the touched TLB range, and increments pending TLB flush state.
- `wp_clean_post_vma()` flushes either the full notifier range for nested TLB flushes or the compact modified subrange, then ends notifier invalidation and decrements pending TLB state.
- Both exported functions hold `i_mmap_lock_read(mapping)` while walking all VMAs mapping the address-space range.
- `clean_record_shared_mapping_range()` guarantees dirty PTEs observed at start are recorded, while racing new dirties may remain dirty, be recorded, or both.

Dependencies:
- Uses `walk_page_mapping()` and `struct mm_walk_ops`.
- Depends on PTE modification helpers, THP PMD/PUD inspection, MMU notifier ranges, cache flushes, TLB flush APIs, and address-space interval locking.
- Intended for subsystems doing PTE-level dirty tracking over shared mappings.

Notable risks:
- Huge PMD/PUD entries are skipped rather than split, so callers needing complete hugepage dirty tracking need additional handling.
- Dirty recording is race-aware but not a full synchronization barrier against new writers; callers needing a closed dirty snapshot must first write-protect and block page-mkwrite/pfn-mkwrite paths.
- Bitmap indexing assumes the provided bitmap covers the requested mapping range relative to `bitmap_pgoff`.
- The functions `WARN_ON()` unexpected page-walk failures but otherwise return the number of PTEs modified.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mapping_dirty_helpers.c -->