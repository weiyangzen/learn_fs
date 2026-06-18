# sources/distributed-fs/ceph-client/mm/madvise.c

## Purpose

`madvise.c` implements `madvise(2)`, `process_madvise(2)`, anonymous VMA naming, and the kernel-side dispatch for memory advice behaviors. It translates user ranges and behavior codes into VMA flag updates, page-cache or swap readahead, page deactivation/pageout, lazy free, discard/zap, THP collapse policy, KSM policy, guard-page marker install/removal, population faults, and memory-failure injection.

## Important APIs, types, and functions

The core state carrier is `struct madvise_behavior`, containing the target `mm_struct`, behavior code, optional `mmu_gather`, selected lock mode, optional anonymous name, current range, current/previous VMA, and a `lock_dropped` flag. `struct madvise_behavior_range` tracks the active subrange, and `enum madvise_lock_mode` chooses no lock, mmap read/write lock, or per-VMA read lock.

Public entry points are `do_madvise()`, `SYSCALL_DEFINE3(madvise)`, `SYSCALL_DEFINE5(process_madvise)`, and, under `CONFIG_ANON_VMA_NAME`, `set_anon_vma_name()`, `anon_vma_name_alloc()`, `anon_vma_name_free()`, and `anon_vma_name()`. Major internal handlers include `madvise_vma_behavior()`, `madvise_walk_vmas()`, `madvise_willneed()`, `madvise_cold()`, `madvise_pageout()`, `madvise_free_single_vma()`, `madvise_dontneed_free()`, `madvise_populate()`, `madvise_remove()`, `madvise_guard_install()`, `madvise_guard_remove()`, `madvise_inject_error()`, and `vector_madvise()`.

## Control flow

`do_madvise()` validates alignment, length overflow, and behavior, acquires the lock selected by `get_lock_mode()`, optionally starts batched TLB gathering for discard/free operations, and dispatches through `madvise_do_behavior()`. Memory-failure behaviors bypass normal VMA walking. Populate behaviors call `faultin_page_range()` directly. Other behaviors call `madvise_walk_vmas()`, which applies `madvise_vma_behavior()` to each overlapping VMA and records `-ENOMEM` for holes while still processing mapped parts.

`madvise_vma_behavior()` first rejects prohibited modifications of sealed mappings, then either performs immediate operations (`MADV_REMOVE`, `WILLNEED`, `COLD`, `PAGEOUT`, `FREE`, `DONTNEED`, `COLLAPSE`, guard install/remove) or computes new VMA flags for policy-style advice and applies them with `madvise_update_vma()`. KSM advice delegates to `ksm_madvise()`, THP advice delegates to `hugepage_madvise()`/`madvise_collapse()`, and anonymous naming modifies VMA metadata through `vma_modify_name()`.

Page-table walkers handle the heavy page operations. `madvise_cold_or_pageout_pte_range()` clears young state, deactivates pages, or isolates pages for reclaim while respecting shared mappings, file-pageout permissions, large folio splitting rules, and THP PMDs. `madvise_free_pte_range()` handles `MADV_FREE` by clearing swap entries, clearing dirty/young PTE bits, freeing swapcache where possible, and marking folios lazyfree. `madvise_dontneed_single_vma()` zaps ranges with batched TLB work. Guard install tries to install `PTE_MARKER_GUARD` markers optimistically and zaps/retries when populated PTEs or huge entries race in; guard removal clears only guard markers.

`process_madvise()` imports an iovec, resolves a pidfd, checks ptrace access, restricts remote behaviors to non-destructive advice (`COLD`, `PAGEOUT`, `WILLNEED`, `COLLAPSE`), requires `CAP_SYS_NICE` for remote influence, then calls `vector_madvise()`.

## State and persistence behavior

Persistent effects depend on behavior. Flag advice changes `vma->flags` and may split/merge VMAs. KSM and THP advice updates VMA policy bits and may enroll an mm in KSM. `DONTNEED` zaps PTEs and releases pages/swap resources; `FREE` lazily marks anonymous pages discardable; `PAGEOUT` can reclaim pages; `WILLNEED` schedules I/O or swapin. Guard install persists not-present PTE markers and sets `VMA_MAYBE_GUARD_BIT`. Anonymous naming stores reference-counted `struct anon_vma_name` objects in VMAs. Population creates page tables/pages. Memory-failure injection changes page hardware-poison/offline state.

## Dependencies and integration points

This file is a hub for MM subsystems: VMA maple-tree modification, mmap and VMA locks, pagewalk, mmu_gather/TLB flushing, MMU notifiers, userfaultfd remove events, swap and shmem swapin, file `fadvise`/`fallocate`, reclaim/LRU, folio splitting, THP, hugetlb validation, KSM, mseal checks, mempolicy/page isolation, pidfd/task/mm access checks, ptrace permissions, capabilities, and anonymous VMA name reference counting.

## Risks and edge cases

Lock mode selection is central: write-lock behaviors may split/merge VMAs, read-lock behaviors may drop and reacquire the mmap lock around filesystem/userfaultfd work, and VMA read-lock fast paths are allowed only for local single-VMA ranges without userfaultfd or required anon-vma preparation. Operations that drop `mmap_lock` must not reuse stale VMA pointers. Large folio/THP handling avoids dirty tracking loss but can leave ranges partially untreated if splitting fails. Remote `process_madvise()` must not allow destructive operations or leak address-space metadata. Guard install can restart to resolve races. Sealed anonymous mappings reject discard-like operations when the user lacks write access. `MADV_DONTNEED` on hugetlb ranges rounds end down to hugepage size to avoid unexpected data loss.

## Test signals

Test signals include syscall ABI validation for alignment, overflow, empty ranges, unknown behaviors, VMA holes, and return values; per-behavior tests for flag changes and VMA splitting/merging; KSM/THP delegation tests; `MADV_FREE` and `DONTNEED` PTE/swap accounting; file-backed `REMOVE` and `WILLNEED` with lock dropping; remote `process_madvise()` permission and behavior filtering; guard marker install/remove including races with faults and THP; userfaultfd remove event sequencing; sealed VMA permission tests; anonymous VMA naming validation and refcounts; and lockdep/MMU-notifier/TLB stress under concurrent mmap, fork, reclaim, and signals.
