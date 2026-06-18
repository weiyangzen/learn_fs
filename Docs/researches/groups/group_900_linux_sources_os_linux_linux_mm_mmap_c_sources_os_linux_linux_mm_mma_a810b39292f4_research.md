# Group Research: group_900_linux_sources_os_linux_linux_mm_mmap_c_sources_os_linux_linux_mm_mma_a810b39292f4

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mmap.c -->
# File Research: sources/os/linux/linux/mm/mmap.c

Linux core user virtual-address-space management. This file implements major mapping syscalls and helpers around `brk`, `mmap`, `munmap`, deprecated `remap_file_pages`, process mmap teardown, special kernel mappings, mmap sysctls, and fork-time VMA duplication.

Key responsibilities:
- Implements `brk`, `mmap_pgoff`, legacy `old_mmap`, `munmap`, deprecated `remap_file_pages`, and `vm_brk_flags()`.
- Provides `do_mmap()` and `ksys_mmap_pgoff()` validation and setup for anonymous, file-backed, hugetlb, shared/private, droppable, locked, populated, noreserve, and memfd-sealed mappings.
- Provides generic bottom-up/top-down unmapped-area search and wrappers around architecture/file `get_unmapped_area()` hooks.
- Exports VMA lookup helpers including `find_vma()`, `find_vma_intersection()`, `find_vma_prev()`, and `mm_get_unmapped_area()`.
- Handles stack expansion, stack guard gap parsing, and fault-time read-to-write mmap-lock upgrade for legacy stack growth.
- Releases all VMAs in `exit_mmap()` using MMU notifiers, cache/TLB teardown, page-table freeing, maple tree destruction, and accounting cleanup.
- Implements special mappings such as vDSO/VVAR-style page-array mappings with custom fault/name/close/mremap behavior.
- Initializes mmap-related sysctls and overcommit reserve defaults, and updates reserves on memory hotplug.
- Implements `dup_mmap()` for fork, including maple tree duplication, VMA duplication, file mapping interval insertion, userfaultfd duplication, anon-vma setup, hugetlb private state, KSM/khugepaged fork hooks, page-table copying, and failure cleanup.

Important behavior:
- `do_mmap()` assumes the current mm is write-locked and returns either an address or error value. It only reports whether population is needed; callers do `mm_populate()`.
- Protection flags are translated through `calc_vm_prot_bits()`, `calc_vm_flag_bits()`, default mm flags, and execute-only pkey handling.
- `MAP_FIXED_NOREPLACE` is forced through fixed-address selection but rejects existing VMA intersections with `-EEXIST`.
- File mappings check file size overflow, access mode, append/swapfile restrictions, `MAP_SHARED_VALIDATE`, noexec mounts, file mmap support, memfd seals, and hugetlb alignment.
- Anonymous `MAP_DROPPABLE` mappings are forced noreserve, wipe-on-fork, dontdump, nonlocked, nonstack, and non-hugetlb.
- `brk()` updates `mm->brk` carefully around shrinking because successful unmap can drop the mmap lock.
- Generic unmapped-area search honors stack guard placement, `mmap_min_addr`, architecture address-space limits, top-down fallback, hugepage alignment, shmem THP area hooks, and LSM `security_mmap_addr()`.
- `remap_file_pages()` emulates old nonlinear remapping via a fixed shared mmap after read-lock lookup, security checking outside mmap lock, and write-lock revalidation.
- `exit_mmap()` first notifies secondary MMUs, unmaps pages under read lock, then takes write lock to clear the maple tree, free page tables, close/free VMAs, and unaccount memory.
- `dup_mmap()` builds a duplicate maple tree first, then replaces each duplicated slot with fully initialized child VMAs; on failure it unmaps and tears down only the initialized prefix.

Dependencies:
- Core MM: VMA/maple iterators, `mmap_region()`, `do_vmi_munmap()`, `do_brk_flags()`, VMA merge/split/insert helpers, page-table copy/unmap/free helpers, rmap, anon_vma, mempolicy, KSM, khugepaged, hugetlb, THP, mlock, overcommit, pkeys, userfaultfd, MMU notifiers, and TLB gather.
- VFS/security: files, inodes, mapping interval trees, `get_file()`/`fput()`, file mmap hooks, memfd seals, LSM mmap/mprotect hooks, audit, mounts, and noexec path checks.
- Architecture hooks: mmap layout, tagged-address handling, cache/TLB flushing, execute-only pkeys, stack growth direction, and `arch_*_mmap()` hooks.

Notable risks:
- Many paths deliberately drop, downgrade, or reacquire mmap locks; callers must handle invalidated VMAs and userfaultfd completion lists correctly.
- Fixed mappings and brk/mremap interactions rely on downstream unmap helpers to enforce VMA sealing and split/merge invariants.
- Fork duplication has complex cleanup paths because maple tree state, file interval trees, anon_vmas, userfaultfd contexts, and page tables are initialized in stages.
- Accounting for `VM_ACCOUNT`, locked memory, data limits, map-count limits, and overcommit reserves must remain paired with VMA mutation and unmap behavior.
- Special mappings forbid splitting and may fault SIGBUS past their page arrays; users must preserve their lifetime assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mmap_lock.c -->
# File Research: sources/os/linux/linux/mm/mmap_lock.c

Mmap-lock tracing and VMA-lock support. This file supplies tracepoint wrappers, per-VMA lock exclusion mechanics, RCU VMA lookup/locking fast paths, and careful mmap-lock acquisition for page-fault handling.

Key responsibilities:
- Exports mmap-lock tracepoints and tracing helper functions when tracing is enabled.
- Implements per-VMA reader exclusion under `CONFIG_PER_VMA_LOCK` using VMA refcounts, lock sequence numbers, `rcuwait`, and lockdep annotations.
- Provides `lock_vma_under_rcu()` for stable RCU lookup plus per-VMA read locking without taking `mmap_lock`.
- Provides `lock_next_vma()` for RCU-safe VMA iteration with fallback to mmap read locking when speculation fails.
- Implements `lock_mm_and_find_vma()` for page-fault paths under `CONFIG_LOCK_MM_AND_FIND_VMA`, including careful kernel-fault exception-table checks and stack expansion.
- Provides a no-MMU fallback that simply takes `mmap_read_lock()` and looks up the VMA.

Important behavior:
- `__vma_start_write()` excludes VMA readers, records the mm lock sequence into `vma->vm_lock_seq`, then ends exclusion so later readers see the VMA as write-locked relative to the mm sequence.
- Detaching a VMA uses a special exclusion target so the writer waits until no readers remain and then leaves the VMA detached.
- `vma_start_read()` may return false locked results, but must never return a false unlocked result; it uses refcount acquisition and sequence checks to reject VMAs under write.
- If a VMA is detached during RCU lookup, the RCU walker can retry from the address instead of trusting stale iterator state.
- `lock_next_vma()` speculates on mmap-lock sequence state to verify gaps; if uncertain, it reacquires under mmap read lock and restarts the iterator.
- Fault-time `lock_mm_and_find_vma()` avoids deadlock on kernel faults by only blocking on the mmap lock when the faulting instruction is exception-table-covered.

Dependencies:
- VMA refcount fields, `mm_lock_seq`, maple/VMA iterators, mmap rwsem helpers, RCU, rcuwait, lockdep, exception tables, stack expansion helpers, and VM event counters.

Notable risks:
- Per-VMA locking depends on subtle refcount states and sequence-number ordering; false positives are acceptable only when they force fallback, not when they allow unsafe access.
- RCU iterator state must be reset after fallback locking or detach races.
- Kernel page faults must not blindly block on mmap locks unless exception-table metadata proves the fault is recoverable.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mmap_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mmu_gather.c -->
# File Research: sources/os/linux/linux/mm/mmu_gather.c

TLB gather and deferred page/page-table freeing implementation. This file batches pages and page tables removed from page tables, coordinates TLB shootdowns, delayed rmap removal, RCU table freeing, and final cleanup for unmap/protection teardown paths.

Key responsibilities:
- Provides `tlb_gather_mmu()`, `tlb_gather_mmu_fullmm()`, `tlb_gather_mmu_vma()`, `tlb_flush_mmu()`, and `tlb_finish_mmu()`.
- Batches freed pages through local and allocated `mmu_gather_batch` structures unless `CONFIG_MMU_GATHER_NO_GATHER` is set.
- Supports encoded page entries that can include delayed rmap removal and multi-page folio run lengths.
- Frees batches in bounded chunks to avoid soft lockups, with different chunking when page poisoning or init-on-free increases per-page cost.
- Supports batched page-table freeing under `CONFIG_MMU_GATHER_TABLE_FREE`.
- Uses RCU or IPI synchronization for architectures with lockless software page-table walkers.
- Tracks nested TLB flush situations and forces full-mm/range reset behavior when parallel batching could leave stale translations.

Important behavior:
- `tlb_next_batch()` stops allocating additional batches when delayed rmaps are pending outside the local batch, ensuring delayed rmap processing stays bounded.
- `tlb_flush_rmaps()` removes rmap entries only after a TLB flush, preserving ordering for concurrent users.
- `tlb_remove_table()` batches page-table pages when possible, otherwise performs immediate table invalidation and single-table freeing.
- RCU table freeing uses sched-RCU semantics because lockless page-table walkers rely on IRQ/preempt-disabled sections.
- `tlb_finish_mmu()` warns if fully unshared page tables remain, handles nested flush escalation, flushes TLBs, frees batched pages/tables, releases extra batch pages, and decrements pending flush state.

Dependencies:
- Architecture TLB APIs, page-table allocation/free hooks, RCU, SMP IPIs, hugetlb page size handling, swap cache freeing, folio/page poisoning, rmap removal, and mm pending-TLB-flush counters.

Notable risks:
- Pages and page tables must not be freed before stale CPU or software-walker references are invalidated.
- Delayed rmap removal must remain paired with post-flush processing.
- Nested batched PTE changes can require broader TLB flushing than the nominal range.
- Allocation failure in table batching must still guarantee progress through single-table fallback.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mmu_gather.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mmu_notifier.c -->
# File Research: sources/os/linux/linux/mm/mmu_notifier.c

MMU notifier core for secondary MMUs and interval subscribers. This file coordinates invalidation callbacks, notifier registration/lifetime, mm teardown release notifications, young-bit callbacks, and interval-tree collision detection for shadow page-table users.

Key responsibilities:
- Maintains `struct mmu_notifier_subscriptions` per mm, including classic hlist notifiers, interval-tree notifiers, invalidation sequence state, active invalidation counts, waitqueue, and deferred interval-tree updates.
- Implements `mmu_interval_read_begin()` and interval invalidation sequencing for sleeping shadow-PTE setup/teardown protocols.
- Implements release-time invalidation for both interval-tree subscribers and classic hlist subscribers.
- Implements young-bit operations: clear-and-flush young, clear young, and test young.
- Implements invalidate-range start/end dispatch for interval and hlist notifiers, including non-blocking `-EAGAIN` handling.
- Provides notifier registration APIs, single-notifier get/put APIs, unregister, async free via SRCU, and module exit synchronization.
- Provides interval notifier insertion/removal, both with and without caller-held mmap write lock.

Important behavior:
- Interval invalidation uses a sequence value where odd values mean a colliding invalidation is active; readers sleep if their observed sequence equals the active invalidating sequence.
- Multiple invalidation writers can be active concurrently; the interval tree is only mutable in the partially excluded state or via deferred add/remove lists drained at final invalidation end.
- `mn_itree_invalidate()` calls interval `invalidate_start`/`invalidate_finish` pairs or legacy `invalidate`, collecting finish callbacks in a lockless list.
- Classic hlist callbacks are protected by a global SRCU domain so unregister/release can wait for in-flight callbacks.
- Non-blocking invalidations that receive `-EAGAIN` call `invalidate_range_end` for already-started notifiers and warn if a blocking callback fails.
- `__mmu_notifier_register()` installs the subscription object under mmap write lock and `mm_take_all_locks()`, with release/acquire ordering for unlocked readers.
- `mmu_notifier_put()` removes the subscription from the list and frees asynchronously through `call_srcu()`.
- Interval insertion grabs an mm count pin and may defer tree insertion if invalidation is in progress; removal waits for any deferred invalidation sequence to finish.

Dependencies:
- SRCU, RCU hlist traversal, interval trees, spinlocks, wait queues, mm lifetime pins, mmap locks, `mm_take_all_locks()`, and notifier operation contracts used by KVM, HMM, GPUs, RDMA, and other secondary-MMU users.

Notable risks:
- Callback ordering is correctness-critical: drivers must drop shadow mappings before core MM frees or repurposes PTEs/pages.
- Interval-tree add/remove during invalidation cannot use sleeping locks and relies on deferred-list draining at final invalidation end.
- `mmu_notifier_put()` is asynchronous; modules using it must call `mmu_notifier_synchronize()` before unload.
- Non-blocking invalidation callbacks must return only expected retry errors and cannot also require normal end callbacks after failing start.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mmu_notifier.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mmzone.c -->
# File Research: sources/os/linux/linux/mm/mmzone.c

Small zone, pgdat, zonelist, LRU-vector, and NUMA balancing helpers.

Key responsibilities:
- Provides online-node iteration helpers `first_online_pgdat()` and `next_online_pgdat()`.
- Provides `next_zone()` for `for_each_zone()` style zone iteration across node boundaries.
- Provides `__next_zones_zonelist()` for allocation zonelist scanning subject to highest zone index and optional NUMA nodemask.
- Initializes `struct lruvec` state, including lock, zswap state, LRU list heads, unevictable-list poisoning, and multi-gen LRU state.
- Provides `folio_xchg_last_cpupid()` when NUMA balancing stores last CPU/PID outside page flags abstraction.

Important behavior:
- `__next_zones_zonelist()` skips zones above the caller’s allowed highest zone and, on NUMA, zones whose node is not in the nodemask.
- `lruvec_init()` deliberately deletes/poisons the unevictable LRU list head because unevictable pages are not actually threaded on that list.
- `folio_xchg_last_cpupid()` updates encoded folio flag bits with a compare-exchange loop and returns the old cpupid.

Dependencies:
- Online node APIs, `NODE_DATA`, zonelists, LRU definitions, zswap lruvec state, multi-gen LRU initialization, NUMA balancing flags, and folio flag atomic updates.

Notable risks:
- Zonelist scanning must preserve sentinel behavior and not dereference invalid zone references.
- Unevictable LRU list poisoning is intentional; code must not treat it like a normal list.
- The cpupid exchange path depends on correct flag bit masks and atomic retry semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mmzone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mprotect.c -->
# File Research: sources/os/linux/linux/mm/mprotect.c

Protection-changing implementation for `mprotect`, `pkey_mprotect`, memory protection keys, and shared internal page-table protection updates.

Key responsibilities:
- Implements `mprotect`, `pkey_mprotect`, `pkey_alloc`, and `pkey_free`.
- Provides `mprotect_fixup()` for VMA flag/prot updates, VMA splitting/merging, accounting, perf notifications, and page-table protection changes.
- Exports `change_protection()` for internal callers such as NUMA balancing, soft-dirty tracking, and userfaultfd write-protect.
- Walks page tables across PTE/PMD/PUD/P4D/PGD levels, including THP, hugetlb, migration entries, device-private entries, poison/guard markers, and userfaultfd markers.
- Optimizes batches of PTE updates for large folios while respecting write, soft-dirty, uffd-wp, and anon-exclusive constraints.
- Implements pkey allocation/freeing against architecture pkey state.

Important behavior:
- Writable PTE upgrades are only done when they match what the fault handler would safely do: dirty shared PTEs, or exclusive anonymous private pages, and not soft-dirty/uffd-wp/protnone entries.
- Large anonymous folio batches may be split into sub-batches because per-page `PageAnonExclusive` can differ inside one folio.
- Nonpresent entries are adjusted for migration/device-private writable-to-readable conversion and uffd-wp set/resolve. Guard and poison markers are not converted.
- File-backed uffd-wp may require populating page tables and installing PTE markers even for `pte_none()`.
- Huge PMD/PUD entries are changed in place when range-aligned and supported, otherwise split to PTE level.
- `change_protection()` uses `PAGE_NONE` for NUMA balancing and otherwise uses `vma->vm_page_prot`; hugetlb is delegated to hugetlb-specific helpers.
- `mprotect_fixup()` rejects sealed VMAs, checks PFN permission for PROT_NONE PFN mappings, handles commit accounting when private mappings become writable, updates VMA flags/prot, and populates private locked VMAs that become writable.
- `do_mprotect_pkey()` validates alignment, growth flags, architecture protection/flag rules, pkey allocation, VMA contiguity, may-access flags, W^X policy, LSM hooks, VMA-specific `mprotect` hooks, and then performs fixups under an `mmu_gather`.

Dependencies:
- Page-table walkers and modification helpers, TLB gather, MMU notifiers, hugetlb/THP helpers, soft-dirty, userfaultfd, swap/migration/device-private entries, pkeys, LSM, map-deny-write-exec policy, VMA modification helpers, commit accounting, mlock population, and architecture protection validation.

Notable risks:
- Writable fast-upgrades must stay consistent with write-fault/COW rules or they can bypass required filesystem, uffd, soft-dirty, or COW behavior.
- Hugepage splitting/population paths can fail and require retry or error handling.
- VMA sealing blocks mprotect; callers must surface `-EPERM`.
- Accounting when adding/removing `VM_ACCOUNT` must remain paired with VMA mutation failure paths.
- `mprotect()` over multiple VMAs fails if any gap exists or if requested permissions exceed `VM_MAY*`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mprotect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mremap.c -->
# File Research: sources/os/linux/linux/mm/mremap.c

Implementation of `mremap(2)` and internal page-table moving. This file handles shrinking, expanding, moving, fixed-address remapping, `MREMAP_DONTUNMAP`, multi-VMA move-only remaps, userfaultfd notifications, hugetlb alignment, accounting, and efficient page-table relocation.

Key responsibilities:
- Implements `mremap` syscall through `do_mremap()` and a threaded `struct vma_remap_struct`.
- Provides `move_page_tables()` and helpers for moving PTEs, normal PMD/PUD page tables, huge PMDs/PUDs, and hugetlb page tables.
- Handles source/destination VMA copying with `copy_vma()`, page-table movement, VMA ops `mremap`, rollback on move failure, and hugetlb reservation fixup.
- Handles shrink-in-place, expand-in-place, expand-by-moving, fixed-address moving, and multi-VMA fixed move-only remaps.
- Coordinates `MREMAP_DONTUNMAP`, including keeping old VMA metadata, clearing mlock flags, and unlinking old anon_vma chains when appropriate.
- Validates map-count headroom, pgoff overflow, locked-memory limits, `VM_DONTEXPAND`, `VM_PFNMAP`, sealed VMAs, private zero-length duplication, hugetlb alignment, and new address overlap.
- Sends userfaultfd unmap/remap completion or failure notifications after releasing mmap lock.

Important behavior:
- `move_ptes()` copies PTEs under both old and new page-table locks, clears source entries, adjusts architecture PTE state with `move_pte()`, marks soft-dirty, optionally clears uffd-wp state, and flushes old TLB range before releasing locks for present entries.
- Rmap locks are taken when required so reverse-map walkers see either old or new PTEs and do not miss both during moves.
- Page-table move acceleration can move entire PMD/PUD page tables or huge entries when aligned, supported by the architecture, and compatible with userfaultfd state.
- `try_realign_addr()` opportunistically aligns source and destination down to page-table boundaries when safe, increasing chances of moving whole page-table entries.
- `move_page_tables()` wraps movement in cache flush and `MMU_NOTIFY_UNMAP` notifier start/end.
- `prep_move_vma()` checks map-count split headroom, VMA split permissions, and asks KSM to unmerge the source range before moving.
- `copy_vma_and_data()` creates/merges the destination VMA, moves page tables, calls VMA `mremap`, and on failure moves page tables back and sets state so the new mapping is unmapped.
- `unmap_source_vma()` temporarily clears `VM_ACCOUNT` during source unmap to avoid double unaccounting for accountable moves, then restores it on remaining source fragments.
- `mremap_to()` unmaps fixed destination first, shrinks before moving when needed, validates `MREMAP_DONTUNMAP` expansion accounting, picks a destination with `get_unmapped_area()`, then moves.
- `remap_move()` supports batched fixed move-only ranges across multiple VMAs while preserving inter-VMA gaps, but rejects armed userfaultfd VMAs and custom unmapped-area files unless known safe.

Dependencies:
- VMA copy/merge/split/unmap helpers, page-table allocation and lock helpers, architecture PMD/PUD move support, hugetlb/THP movement, rmap locks, KSM, userfaultfd, MMU notifiers, TLB/cache flushing, commit accounting, mlock limits, VMA sealing, and filesystem `get_unmapped_area()` hooks.

Notable risks:
- Page-table moves must preserve visibility to rmap walkers, secondary MMUs, userfaultfd state, and stale TLB invalidation ordering.
- Error recovery is intricate: partial destination VMAs and moved page tables must be reverted or unmapped without corrupting accounting.
- `MREMAP_DONTUNMAP` has unusual semantics: the source VMA remains but page tables move, mlock is cleared, and anon_vma links can be dropped.
- Fixed multi-VMA moves must account for gaps and custom placement hooks; unsafe cases are rejected.
- Sealed VMAs reject all mremap operations with `-EPERM`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mremap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mseal.c -->
# File Research: sources/os/linux/linux/mm/mseal.c

Implementation of the `mseal(2)` syscall, which seals VMA metadata over a fully mapped address range so later operations cannot alter the mapping layout or selected protections/contents.

Key responsibilities:
- Implements `do_mseal()` and `SYSCALL_DEFINE3(mseal)`.
- Validates flags, tagged/aligned start address, rounded length, overflow, zero-length no-op, and mmap write-lock acquisition.
- Rejects ranges that contain unmapped gaps at the start, middle, or end.
- Applies `VMA_SEALED_BIT` across all VMAs in the range, splitting/merging with `vma_modify_flags()` as needed.
- Allows repeated sealing of already sealed VMAs as a no-op.

Important behavior:
- `range_contains_unmapped()` walks VMAs from `start` to `end` and returns true if any gap exists before the next VMA or after the last VMA.
- `mseal_apply()` modifies only the overlapping portion of each VMA, updates iterator/previous VMA state, starts VMA write mode, and sets the sealed flag.
- The syscall holds mmap write lock across both validation and application so the range cannot change between the gap check and flag updates.
- Sealed VMAs are enforced by other files in this group: `mprotect.c` rejects protection changes, `mremap.c` rejects remaps, and mmap/munmap paths rely on unmap/fixed-map helpers checking seals.

Dependencies:
- VMA iterators, VMA flag modification helpers, per-VMA write locking, tagged-address handling, mmap write lock, and the shared `VMA_SEALED_BIT` semantics used by mmap/mprotect/mremap/madvise paths.

Notable risks:
- The syscall intentionally rejects ranges with holes to avoid giving callers a false sense that future mappings into holes are sealed.
- VMA modification can still fail due to splitting/merging allocation or map-count pressure.
- There is no unseal operation; setting `VMA_SEALED_BIT` is permanent for the VMA lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mseal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/msync.c -->
# File Research: sources/os/linux/linux/mm/msync.c

Implementation of `msync(2)` for synchronizing shared file-backed mappings.

Key responsibilities:
- Implements `SYSCALL_DEFINE3(msync)`.
- Validates flags, start alignment, length rounding, overflow, and empty range behavior.
- Walks VMAs overlapping the requested range under mmap read lock.
- Handles unmapped holes according to Linux `msync` behavior.
- For `MS_SYNC`, calls `vfs_fsync_range()` on shared file-backed mapping ranges after taking a file reference and dropping mmap lock.
- Rejects invalidation of locked VMAs with `-EBUSY`.

Important behavior:
- `MS_ASYNC` alone starts no I/O and marks no pages dirty; dirty tracking is handled elsewhere. If the range has holes and only `MS_ASYNC` is requested, it can return `-ENOMEM` immediately.
- Unmapped subranges are skipped but remembered so the syscall can return `-ENOMEM` after syncing mapped portions.
- File offsets are computed from VMA offset plus the virtual offset inside the VMA, and the synced file range is inclusive.
- The function drops mmap read lock around `vfs_fsync_range()` to avoid filesystem sync under mmap lock, then reacquires and resumes VMA lookup.

Dependencies:
- VMA lookup and mmap read lock, VFS file references, `vfs_fsync_range()`, shared mapping flags, tagged-address handling, and `MS_*` user API definitions.

Notable risks:
- Dropping mmap lock around fsync means VMAs may change between iterations; the code restarts lookup at the next virtual address.
- `MS_INVALIDATE` cannot apply to locked VMAs.
- Holes are not fatal until after mapped ranges are processed unless only no-op async behavior remains.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/msync.c -->