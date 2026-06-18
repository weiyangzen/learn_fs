# sources/distributed-fs/ceph-client/mm/vma.c

## Purpose

`vma.c` is the central VMA manipulation implementation. It manages VMA linking/unlinking, splitting, merging, expanding, shrinking, munmap, mmap-region construction, brk growth, gap searches, stack growth, all-VMA lock collection, dirty/write-notify decisions, mremap VMA copying, and insertion into maple trees plus file/anon interval trees.

## Important APIs, Types, and Functions

- `struct mmap_state` carries all state for `mmap_region()`: address range, flags, file, page protections, VMA neighbors, detach tree, munmap state, and `.mmap_prepare()` outcomes.
- VMA merge core: `vma_merge_new_range()`, `vma_merge_extend()`, `vma_expand()`, `vma_shrink()`, `vma_modify_flags()`, `vma_modify_name()`, `vma_modify_policy()`, `vma_modify_flags_uffd()`, and internal `vma_modify()`, `vma_merge_existing_range()`, `commit_merge()`.
- Munmap core: `do_vmi_munmap()`, `do_vmi_align_munmap()`, `vms_gather_munmap_vmas()`, `vms_complete_munmap_vmas()`, `vms_abort_munmap_vmas()`, and `unmap_region()`.
- Mapping core: `mmap_region()`, `__mmap_region()`, `__mmap_setup()`, `__mmap_new_vma()`, `__mmap_new_file_vma()`, and `__mmap_complete()`.
- Other exported helpers: `remove_vma()`, `unlink_file_vma_batch_*()`, `copy_vma()`, `find_mergeable_anon_vma()`, `vma_needs_dirty_tracking()`, `vma_wants_writenotify()`, `mm_take_all_locks()`, `mm_drop_all_locks()`, `do_brk_flags()`, `unmapped_area()`, `unmapped_area_topdown()`, `expand_downwards()`, optional `expand_upwards()`, `__vm_munmap()`, `insert_vm_struct()`, and weak `vma_mmu_pagesize()`.

## Control Flow

VMA merging starts by checking equality of merge-relevant state: mempolicy, flags excluding ignore masks, file, userfaultfd context, anon name, pgoff continuity, and anon-vma compatibility. Existing-range modifications first try to merge the changed edge or whole VMA with neighbors; if no merge is possible, `vma_modify()` splits leading and trailing portions so the caller can update an exact range. New mappings try `vma_merge_new_range()` against adjacent VMAs before allocating a fresh VMA.

`commit_merge()` is the point where mutable state changes. It preallocates maple-tree storage before altering VMAs, calls `vma_prepare()` to remove file/anon interval-tree entries and lock rmap structures, adjusts THP/hugetlb boundaries, updates ranges/pgoffs, stores the target VMA, and calls `vma_complete()` to restore interval trees, fire uprobes, drop file/mempolicy references for removed VMAs, unlink anon_vmas, decrement map counts, and free removed VMAs.

Splitting duplicates a VMA, adjusts one side's start/end/pgoff, preallocates maple-tree storage, duplicates policy and anon-vma chains, references files, calls open hooks, writes both VMAs, splits THP/hugetlb state at the boundary, and inserts the new VMA through `vma_complete()`.

Munmap first aligns and validates ranges in `do_vmi_munmap()`. `vms_gather_munmap_vmas()` splits boundary VMAs, rejects sealed VMAs, detaches covered VMAs into a side maple tree, gathers accounting totals, and prepares userfaultfd unmap events. `do_vmi_align_munmap()` clears the main maple-tree range, then `vms_complete_munmap_vmas()` unmaps PTEs, updates mm accounting, removes VMAs, unaccounts memory, validates the mm, unlocks when requested, and destroys the side tree.

`mmap_region()` validates MDWE and architecture flags, pins writable file mappings, then calls `__mmap_region()`. Setup gathers overlapping VMAs for replacement, checks expansion and overcommit, cleans old PTEs while old VMAs remain visible, invokes optional `.mmap_prepare()`, applies KSM flags, attempts a merge, otherwise allocates and links a new VMA. Completion fires perf/uprobe events, accounts stats, handles mlock, marks soft-dirty, sets page protection, and completes mmap actions for newly allocated `.mmap_prepare()` mappings.

Stack growth checks grow direction, address limits, guard gaps, anon-vma availability, rlimit/overcommit/mlock limits, and hugepage-only ranges before updating VMA bounds and maple-tree entries under anon-vma locking.

## State and Persistence

Persistent state lives in `mm_struct` fields (`map_count`, `total_vm`, `locked_vm`, `exec_vm`, `stack_vm`, `data_vm`, maple tree), `vm_area_struct` fields (ranges, flags, pgoff, file, policy, anon-vma, page protections, userfaultfd context, anon name), address-space interval trees, anon-vma interval trees, rmap state, file writable mapping counters, and page tables. Temporary state includes `struct vma_prepare`, `struct vma_merge_struct`, `struct vma_munmap_struct`, side maple trees for detached VMAs, `struct mmap_state`, and batched unlink state.

## Dependencies and Integration Points

This file integrates with maple tree iteration/storage, anon-vma/rmap interval trees, file `i_mmap` trees, mempolicy, KSM/khugepaged, hugetlb/THP split/adjustment, userfaultfd unmap and registration helpers, uprobes, perf mmap events, LSM overcommit checks, fs/file mapping writable accounting, mmap prepare/action APIs, page table unmap/free paths, mlock and rlimit checks, soft-dirty tracking, MDWE enforcement, and architecture flag/page-size hooks.

## Risks

- The merge/split code depends on prealloc-before-mutate ordering. Any new mutation before successful maple-tree preallocation can break the OOM safety contract.
- Anon-vma compatibility deliberately avoids merging fork-complex anon_vmas for scalability; relaxing this can cause rmap lock contention.
- `vm_ops->close`, `open`, `may_split`, and `.mmap_prepare()` callbacks constrain when VMAs can be deleted, split, or merged.
- Munmap failure recovery differs before and after PTE clearing; after some cleanup it may leave a gap instead of restoring old VMAs.
- File interval-tree locking and uprobe notifications must bracket range updates correctly, or tracing/rmap/filesystem visibility becomes inconsistent.
- Stack growth arithmetic must guard pgoff underflow/overflow and guard-gap bypasses.
- `mm_take_all_locks()` uses marker bits in anon-vma and mapping state; missed cleanup would deadlock or corrupt later rmap operations.

## Test Signals

Signals include mm selftests for mmap/munmap/mremap/mprotect/brk, userfaultfd unmap event tests, lockdep with `mm_take_all_locks()`, debug maple-tree `validate_mm()`, THP/hugetlb split and merge tests, KSM mergeability tests, MDWE mmap denial tests, sealed VMA munmap failures, mmap prepare/action driver tests, stack expansion guard-gap/rlimit tests, and stress tests under concurrent faults/truncate/uprobe activity.
