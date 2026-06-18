# Group Research: group_909_linux_sources_os_linux_linux_mm_usercopy_c_sources_os_linux_linux_mm_7d4ec5baeee7

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/usercopy.c -->
# File Research: sources/os/linux/linux/mm/usercopy.c

This file implements hardened usercopy validation for `copy_to_user()` / `copy_from_user()` paths. Its role is defensive: reject kernel text exposure, invalid addresses, stack-frame misuse, and heap-object copies outside allocator-approved ranges.

Key elements:
- `check_stack_object()` classifies a copy range as off-stack, valid stack frame, valid stack range, or bad stack. It uses `task_stack_page(current)`, `THREAD_SIZE`, `arch_within_stack_frames()`, and optionally `current_stack_pointer`.
- `usercopy_abort()` reports whether the operation is kernel memory exposure or overwrite, then calls `BUG()`.
- `check_kernel_text_object()` blocks copies overlapping `_stext.._etext` and, when present, the linear alias returned by `lm_alias()`.
- `check_bogus_address()` catches wraparound ranges and `NULL` / zero-size allocation sentinel pointers.
- `check_heap_object()` validates kmap, vmalloc, direct-map, slab, and compound-page cases. Slab objects defer to `__check_heap_object()`, while compound pages are bounded by `page_size()`.
- `__check_object_size()` is the exported central validator. It skips zero-length copies, runs bogus-address checks, stack checks, heap checks, then kernel-text checks.
- `validate_usercopy_range` is a static branch configured by `CONFIG_HARDENED_USERCOPY_DEFAULT_ON` and the `hardened_usercopy=` boot option.

Important dependencies:
- Slab allocator usercopy metadata via `__check_heap_object()`.
- Architecture stack-frame support via `arch_within_stack_frames()`.
- vmalloc metadata via `find_vmap_area()`.
- kernel section symbols `_stext` and `_etext`.

Research notes:
- The code deliberately allows non-compound direct-map pages without exact boundary validation, because such pages may be part of larger allocations.
- vmalloc checking is skipped while page faults are disabled.
- The failure mode is intentionally fatal; violations are treated as kernel corruption/security bugs, not recoverable syscall errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/usercopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/userfaultfd.c -->
# File Research: sources/os/linux/linux/mm/userfaultfd.c

This file implements the mm-side mechanics for userfaultfd operations: atomic missing-page fills, zero-page fills, minor-fault continuation, poison markers, write-protection range changes, page-table based page moves, and VMA registration/release.

Major structures and helpers:
- `struct mfill_state` carries userfaultfd context, source/destination ranges, current VMA, current addresses, and current PMD during fill operations.
- `anon_uffd_ops` supplies anonymous-memory userfaultfd behavior: no minor mode, folio allocation through `vma_alloc_folio()` and memcg charging.
- `vma_uffd_ops()` dispatches anonymous VMAs to `anon_uffd_ops`; file-backed VMAs use `vma->vm_ops->uffd_ops`.
- `uffd_mfill_lock()` / `uffd_mfill_unlock()` abstract either per-VMA read locking or mmap read locking.
- `mfill_get_vma()` validates the target range, registered context, mmap-changing state, mode compatibility, hugetlb routing, and availability of VMA-specific uffd operations.
- `mfill_establish_pmd()` allocates and validates the destination PMD/PTE page without overwriting huge/leaf PMDs.

Atomic fill path:
- `mfill_atomic_install_pte()` installs the final PTE for anon or file-cache folios, handles UFFD write-protect markers, rmap setup, mm counters, folio LRU insertion, file-cache unlock, and MMU cache update.
- `mfill_copy_folio_locked()` copies from userspace with page faults disabled while mmap locking is held to avoid recursive mmap-lock deadlocks.
- `mfill_copy_folio_retry()` drops locks, copies with faults enabled, then reacquires and verifies that the VMA still matches saved retry state.
- `__mfill_atomic_pte()` implements COPY and ZEROPAGE folio creation, page-content initialization, filemap insertion, and PTE installation.
- `mfill_atomic_pte_zeropage()` prefers the shared zero page when legal and falls back to a zeroed folio for shared mappings or architectures that forbid zeropage.
- `mfill_atomic_pte_continue()` handles minor-fault continuation by locating an existing file-cache folio with `get_folio_noalloc()`.
- `mfill_atomic_pte_poison()` installs a `PTE_MARKER_POISONED` marker into an empty PTE.
- `mfill_atomic_hugetlb()` is the hugepage-specific path, with alignment checks, hugetlb fault mutex locking, huge PTE allocation, retry after copying outside locks, and explicit unsupported zeropage handling.
- Public wrappers are `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, and `mfill_atomic_poison()`.

Write-protect path:
- `uffd_wp_range()` changes page protections with `MM_CP_UFFD_WP` or `MM_CP_UFFD_WP_RESOLVE`, optionally trying writable upgrades when resolving write-protect.
- `mwriteprotect_range()` validates each VMA in the requested range, handles hugetlb alignment, coordinates with `map_changing_lock`, and invokes `uffd_wp_range()`.

Move path:
- `double_pt_lock()` and `double_pt_unlock()` impose stable ordering for two PTE locks.
- `move_pages_ptes()` handles page-by-page movement for present PTEs, zero-page PTEs, swap PTEs, and migration entries. It uses MMU notifier invalidation, PTE stability checks, PMD stability checks, folio locking, swap-cache validation, and large-folio splitting.
- `move_present_ptes()` can batch contiguous anonymous exclusive order-0 folios when destination PTEs are empty and source folios remain stable.
- `move_swap_pte()` moves exclusive swap entries and updates swap-cache folio rmap/index state if a cached folio exists.
- `move_zeropage_pte()` remaps a zero page to the destination.
- `move_pages()` is the exported userfaultfd move engine. It validates source/destination VMAs, forbids shared/non-anonymous/incompatible mappings, supports THP PMD moves when possible, splits huge PMDs when necessary, and returns either bytes moved or an error.

Registration and release:
- `vma_can_userfault()` checks UFFD mode support, droppable mappings, async WP behavior, PTE marker support, and VMA uffd ops.
- `userfaultfd_set_vm_flags()` updates UFFD flags and recalculates page protections for shared UFFD-WP mappings.
- `userfaultfd_register_range()` modifies VMAs through `vma_modify_flags_uffd()`, verifies MAYWRITE and context consistency, and disables hugetlb PMD sharing when required.
- `userfaultfd_clear_vma()` clears UFFD flags/context and resolves write-protection markers before modifying VMA layout.
- `userfaultfd_release_new()` and `userfaultfd_release_all()` clear contexts from VMAs during context teardown.

Concurrency and correctness themes:
- The file is heavily defensive around VMA replacement, mmap changes, PMD/PTE page disappearance, THP races, swap-cache races, and fatal signals.
- `map_changing_lock` and `ctx->mmap_changing` protect against non-cooperative mapping changes.
- Retry-state comparison checks UFFD flags, VMA type, file identity, inode, and `vm_pgoff` after dropping locks.
- `UFFDIO_MOVE` is intentionally strict: destination must be empty, source holes fail unless explicitly allowed, and incompatible mappings return errors rather than silently degrading.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/userfaultfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/util.c -->
# File Research: sources/os/linux/linux/mm/util.c

This file is a broad mm utility collection. It provides allocation/string duplication helpers, userspace memory duplication helpers, mmap layout randomization, locked-memory accounting, mmap entry wrappers, folio/page helpers, overcommit accounting, command-line extraction, page-offline synchronization, mmap descriptor compatibility helpers, mmap action dispatch, and page snapshot support.

Memory/string helpers:
- `kfree_const()` frees only non-rodata pointers.
- `kstrdup()`, `kstrdup_const()`, `kstrndup()`, `kmemdup_noprof()`, `kmemdup_array()`, `kvmemdup()`, and `kmemdup_nul()` implement common kernel duplication patterns.
- `memdup_user()`, `vmemdup_user()`, `strndup_user()`, and `memdup_user_nul()` allocate kernel memory and copy user buffers with correct `ERR_PTR()` failure signaling.
- `user_buckets` is initialized for user-copy duplication allocation buckets.

Mapping/layout helpers:
- `vma_is_stack_for_current()` tests whether a VMA contains the current stack pointer.
- `vma_set_file()` swaps a VMA file reference during initial setup.
- `randomize_stack_top()` and `randomize_page()` provide stack and page-aligned ASLR helpers.
- `arch_pick_mmap_layout()` selects legacy or top-down mmap layout based on personality, stack rlimit, randomization, and architecture configuration.
- `vm_mmap_pgoff()` and `vm_mmap()` wrap `do_mmap()` with security, fsnotify, mmap locking, userfaultfd completion, and population handling.
- `vm_mmap_shadow_stack()` maps architecture shadow stacks when enabled.

Accounting and overcommit:
- `__account_locked_vm()` and `account_locked_vm()` update `mm->locked_vm` with `RLIMIT_MEMLOCK` enforcement.
- Sysctls cover `overcommit_memory`, `overcommit_ratio`, `overcommit_kbytes`, `user_reserve_kbytes`, and `admin_reserve_kbytes`.
- `vm_commit_limit()` computes strict overcommit allowance from RAM, hugetlb pages, swap, and ratio/kbytes settings.
- `vm_memory_committed()` exports the committed-as counter.
- `__vm_enough_memory()` enforces overcommit policies and rolls back committed accounting on failure.

Folio/page helpers:
- `folio_anon_vma()` returns an anon_vma from encoded folio mapping state.
- `folio_mapping()` resolves page-cache, swap-cache, or NULL mapping for a folio.
- `folio_copy()` and `folio_mc_copy()` copy all pages in a folio, with machine-check-aware copy support.
- `memcmp_pages()` maps and compares two pages.
- `flush_dcache_folio()` falls back to per-page dcache flushing if not architecture-provided.
- `snapshot_page()` safely captures page and folio metadata into a `page_snapshot`, marking snapshots unfaithful if compound state is unstable.
- `page_range_contiguous()` validates memmap contiguity for sparsemem without vmemmap.

Diagnostics and synchronization:
- `get_cmdline()` reads a task’s argv/env memory using `access_process_vm()`, including setproctitle-style handling.
- `mem_dump_obj()` reports object provenance through slab/vmalloc helpers or coarse memory type classification.
- `page_offline_freeze()`, `page_offline_thaw()`, `page_offline_begin()`, and `page_offline_end()` coordinate readers with drivers setting `PageOffline()`.

mmap descriptor compatibility/actions:
- `compat_set_desc_from_vma()` builds a `vm_area_desc` from an existing VMA for stacked mmap compatibility.
- `compat_set_vma_from_desc()` is declared inline in `vma.h` and used here by `__compat_vma_mmap()`.
- `compat_vma_mmap()` lets legacy `.mmap()`-style stacked drivers invoke underlying `.mmap_prepare()` logic.
- `mmap_action_prepare()` dispatches preparatory actions such as remap PFN, IO remap, simple IO remap, and map-kernel-pages.
- `mmap_action_complete()` completes supported actions and funnels cleanup through `mmap_action_finish()`.
- `mmap_action_finish()` calls `vm_ops->mapped`, success/error hooks, releases temporary rmap locks, and unmaps the VMA on post-map failure when not in compatibility mode.
- `folio_pte_batch()` is a wrapper for detecting same-folio PTE runs in MMU builds.

Research notes:
- This file bridges core mm policy with user-facing syscall-like behavior, especially mmap and overcommit.
- Several functions are compatibility scaffolding for converting drivers from `.mmap()` to `.mmap_prepare()`.
- Error cleanup is careful because mmap action completion can occur after a VMA has become visible.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vma.c -->
# File Research: sources/os/linux/linux/mm/vma.c

This file implements core VMA manipulation for MMU mappings: merge, split, expand, shrink, munmap, mmap region creation, brk growth, unmapped-area search, stack expansion, VMA insertion, dirty-tracking policy, and global lock acquisition.

Core state:
- `struct mmap_state` carries all transient state for `mmap_region()`: target range, file, flags, page protections, descriptor-updated fields, accounting, adjacent VMAs, munmap state, and detached Maple Tree state.
- `MMAP_STATE` initializes mapping state.
- `VMG_MMAP_STATE` translates mmap state into a `vma_merge_struct`.

Merge and split logic:
- `is_mergeable_vma()` checks policy, flags excluding ignored merge flags, file identity, userfaultfd context, and anon name.
- `is_mergeable_anon_vma()` prevents merges that would create problematic anon_vma sharing, especially fork-derived anon_vma chains.
- `can_vma_merge_before()`, `can_vma_merge_after()`, `can_vma_merge_left()`, and `can_vma_merge_right()` enforce adjacency and `vm_pgoff` continuity.
- `vma_prepare()` removes VMAs from file and anon interval trees and takes required locks before structural mutation.
- `vma_complete()` reinserts interval-tree entries, stores newly split VMAs, removes merged-away VMAs, drops references, updates map count, and runs uprobe callbacks.
- `__split_vma()` duplicates a VMA, adjusts endpoints/pgoff, clones policy and anon_vma state, handles file refs and `vm_ops->open`, splits THP/hugetlb state at the boundary, then inserts the new VMA.
- `split_vma()` wraps `__split_vma()` with `sysctl_max_map_count` enforcement.
- `dup_anon_vma()` propagates anon_vma state to an unfaulted merge target when necessary.
- `vma_merge_existing_range()` handles merge opportunities after changing attributes within an existing VMA.
- `vma_merge_new_range()` merges a newly proposed range into adjacent compatible VMAs.
- `vma_merge_copied_range()` adapts merge logic for `mremap()` copy targets.
- `vma_expand()` expands a target VMA and optionally removes the next VMA.
- `vma_shrink()` reduces a VMA from one side and clears the obsolete Maple Tree range.

VMA modification APIs:
- `vma_modify()` first tries merge, then splits leading/trailing ranges as needed.
- `vma_modify_flags()`, `vma_modify_name()`, `vma_modify_policy()`, and `vma_modify_flags_uffd()` specialize `vma_modify()` for flags, anon names, NUMA policy, and userfaultfd context.
- `vma_merge_extend()` expands a VMA by a delta when compatible.

Munmap:
- `vms_gather_munmap_vmas()` splits edge VMAs, checks sealed VMAs, detaches target VMAs into a temporary Maple Tree, accounts pages/locked/accounted/exec/stack/data totals, and prepares userfaultfd unmap notifications.
- `vms_clear_ptes()` and `vms_clean_up_area()` clear page tables and call close hooks as needed.
- `vms_complete_munmap_vmas()` updates map count and mm accounting, optionally downgrades/unlocks mmap lock, removes VMAs, unaccounts memory, validates the mm, and destroys the detached tree.
- `reattach_vmas()` restores detached VMAs on abort before destructive cleanup.
- `vms_abort_munmap_vmas()` either reattaches detached VMAs or completes removal if PTEs/close state already made rollback unsafe.
- `do_vmi_align_munmap()` is the aligned munmap engine.
- `do_vmi_munmap()` validates start/length, finds the first overlapping VMA, and calls the aligned engine.
- `__vm_munmap()` wraps munmap with mmap write locking and userfaultfd completion.

mmap creation:
- `accountable_mapping()` identifies private writable non-hugetlb mappings that need overcommit accounting.
- `__mmap_setup()` prepares overlapping VMA removal, checks expansion limits, handles memory accounting, clears old PTEs, and initializes a descriptor.
- `call_mmap_prepare()` invokes `f_op->mmap_prepare()` before merge attempts and accepts only whitelisted descriptor changes.
- `can_set_ksm_flags_early()` determines whether KSM flags can be applied before callbacks without disrupting mergeability.
- `__mmap_new_file_vma()` attaches file state and invokes legacy `.mmap()` if present, undoing partial driver mappings on failure.
- `__mmap_new_vma()` allocates and inserts a fresh VMA when merge fails.
- `__mmap_complete()` finalizes mmap accounting, perf event, userfaultfd cleanup, mlock state, uprobe mapping, soft-dirty flag, and page protections.
- `__mmap_region()` orchestrates setup, mmap_prepare, KSM updates, merge attempt, new VMA allocation, descriptor fields, completion, and abort cleanup.
- `mmap_region()` is the exported internal entry, enforcing MDWE, architecture flag validation, and writable-file mapping guards.

Other functionality:
- `copy_vma()` creates or merges a target VMA for `mremap()` page-table moves.
- `find_mergeable_anon_vma()` finds adjacent reusable anon_vma state to improve later merging after faults/mprotect.
- `vma_needs_dirty_tracking()` and `vma_wants_writenotify()` decide when shared writable mappings need write fault notification or dirty tracking.
- `mm_take_all_locks()` and `mm_drop_all_locks()` acquire/release all relevant VMA, mapping, hugetlb, and anon_vma locks for operations needing global mm stability.
- `do_brk_flags()` grows or creates the heap/brk VMA with accounting, KSM flags, soft-dirty handling, and merge attempt.
- `unmapped_area()` and `unmapped_area_topdown()` search Maple Tree gaps with alignment and guard-gap constraints.
- `expand_upwards()` and `expand_downwards()` grow stack VMAs with guard-gap, rlimit, mlock, hugepage-only range, overcommit, anon_vma, and Maple Tree updates.
- `insert_vm_struct()` inserts a prebuilt VMA, including anonymous `vm_pgoff` normalization and accounting.
- `vma_mmu_pagesize()` weakly defaults MMU granularity to `vma_kernel_pagesize()`.

Research notes:
- The central design is a two-phase mutation protocol: preallocate Maple Tree changes before modifying VMAs, then alter interval trees, VMA ranges, and mm counters only after rollback boundaries are clear.
- Merge logic preserves sticky flags and avoids removing VMAs with close hooks.
- Munmap intentionally accepts that some rare userfaultfd/split failures can leave VMAs split while reporting an error.
- File-backed VMAs require synchronization with `i_mmap` interval trees and uprobe callbacks; anonymous VMAs require anon_vma interval-tree synchronization.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vma.h -->
# File Research: sources/os/linux/linux/mm/vma.h

This header defines the internal API and state objects for VMA manipulation implemented mostly in `vma.c`, with shared use from mmap, munmap, exec, userfaultfd, and related mm code.

Key structures:
- `struct vma_prepare` describes VMAs/files/anon_vmas involved in a pending structural update, including inserted and removed VMAs.
- `struct unlink_vma_file_batch` batches removal of file-backed VMAs from an address_space interval tree.
- `struct vma_munmap_struct` tracks munmap ranges, neighboring VMAs, userfaultfd list, unlock behavior, accounting totals, and whether PTEs need clearing.
- `enum vma_merge_state` records merge progress/error/success.
- `struct vma_merge_struct` is the central merge descriptor: mm, iterator, prev/middle/next/target VMAs, range, flags, file, anon_vma, policy, userfaultfd context, anon name, copied-from VMA, caller controls, and internal merge-operation flags.
- `struct unmap_desc` describes VMA/page-table ranges for unmapping and page-table freeing.

Important inline helpers and macros:
- `unmap_all_init()` and `unmap_pgtable_init()` initialize `unmap_desc` for broad VMA or page-table removal.
- `UNMAP_STATE` builds an `unmap_desc` around a VMA range and neighbors.
- `VMG_STATE` and `VMG_VMA_STATE` initialize merge descriptors for new ranges or existing VMA modifications.
- `vmg_nomem()` tests for merge OOM state.
- `vma_pgoff_offset()` computes file/page offset for an address inside a VMA.
- `vma_iter_*` helpers wrap Maple Tree iterator operations for preallocation, storage, clearing, loading, gap search, range traversal, rewind, and address/end extraction.
- `compat_set_vma_from_desc()` applies selected `vm_area_desc` fields back to an existing VMA for mmap compatibility paths.
- `is_exec_mapping()`, `is_stack_mapping()`, `is_data_mapping()`, and `is_data_mapping_vma_flags()` classify VMAs for mm accounting.
- `vma_wants_manual_pte_write_upgrade()` identifies VMAs where individual PTE writable upgrades must be handled manually.
- `vm_pgprot_modify()` derives protections from VMA flags.
- `vma_is_sealed()` is enabled only on 64-bit builds.
- `map_deny_write_exec()` enforces MDWE rules by denying writable-executable mappings and executable upgrades from previously non-executable VMAs.

Declared API:
- Structural operations: `vma_expand()`, `vma_shrink()`, `vma_merge_new_range()`, `vma_merge_extend()`, `copy_vma()`, `insert_vm_struct()`.
- Modification helpers: `vma_modify_flags()`, `vma_modify_name()`, `vma_modify_policy()`, `vma_modify_flags_uffd()`.
- Unmap helpers: `do_vmi_align_munmap()`, `do_vmi_munmap()`, `remove_vma()`, `unmap_region()`, `__vm_munmap()`.
- File unlink batching: `unlink_file_vma_batch_init()`, `unlink_file_vma_batch_add()`, `unlink_file_vma_batch_final()`.
- Mapping/search/accounting helpers: `mmap_region()`, `do_brk_flags()`, `unmapped_area()`, `unmapped_area_topdown()`, `find_mergeable_anon_vma()`, `vma_needs_dirty_tracking()`, `vma_wants_writenotify()`.
- Locking helpers: `mm_take_all_locks()`, `mm_drop_all_locks()`.
- Stack growth: `expand_upwards()` when configured, and `expand_downwards()`.
- VMA allocation lifecycle from `vma_init.c`: `vma_state_init()`, `vm_area_alloc()`, `vm_area_dup()`, `vm_area_free()`.
- Exec helpers from `vma_exec.c`: `create_init_stack_vma()` and `relocate_vma_down()`.

Research notes:
- This header is the contract boundary for the VMA subsystem after splitting VMA logic out of larger mm files.
- It encodes assumptions about Maple Tree iterator positioning, mmap write-lock ownership, sticky flags, and caller responsibility for applying modifications after split/merge preparation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vma_exec.c -->
# File Research: sources/os/linux/linux/mm/vma_exec.c

This file contains exec-specific operations that are still purely VMA logic: creating the temporary initial stack VMA and relocating it downward during exec setup.

Functions:
- `relocate_vma_down()` shifts a VMA downward by `shift` bytes. It expands the VMA to cover both old and new ranges, moves page tables with `move_page_tables()`, frees obsolete PGD ranges with `free_pgd_range()`, and then shrinks the VMA to the new range with `vma_shrink()`.
- `create_init_stack_vma()` allocates and inserts the temporary initial stack VMA at `STACK_TOP_MAX - PAGE_SIZE .. STACK_TOP_MAX`, marks it anonymous, applies `VM_STACK_FLAGS | VM_STACK_INCOMPLETE_SETUP`, handles soft-dirty support, runs `ksm_execve()`, inserts the VMA, and initializes `mm->stack_vm` / `mm->total_vm`.

Important behavior:
- `relocate_vma_down()` requires the destination gap between new and old ranges to be empty and verifies this through the VMA iterator.
- It sets `pmc.for_stack = true`, making the page-table move stack-specific.
- On page-table move failure, cleanup is delegated to later process cleanup because partial movement may already have occurred.
- `create_init_stack_vma()` takes the mmap write lock killably and unwinds through `ksm_exit()`, unlock, and `vm_area_free()` on error.
- The stack is temporarily placed at the architecture’s maximum stack address rather than `STACK_TOP`, because final process attributes might not be configured yet.

Research notes:
- These helpers are intentionally documented as not general-purpose VMA relocation/creation APIs.
- The file depends on core VMA merge/shrink behavior from `vma.c` and allocation from `vma_init.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vma_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vma_init.c -->
# File Research: sources/os/linux/linux/mm/vma_init.c

This file provides VMA allocation, duplication, initialization-from-existing, and freeing shared by MMU and NOMMU configurations.

Key elements:
- `vm_area_cachep` is the slab cache for `struct vm_area_struct`.
- `vma_state_init()` creates the `vm_area_struct` cache with hardware-cache alignment, panic-on-failure, RCU type safety, accounting, a free pointer offset at `vm_freeptr`, and sheaf capacity 32.
- `vm_area_alloc()` allocates a VMA from the cache and initializes it with `vma_init(vma, mm)`.
- `vm_area_init_from()` copies the fields needed to duplicate an existing VMA: mm, ops, range, anon_vma, pgoff, file, private data, flags, page protection, shared interval-tree state, userfaultfd context, optional anon name, swap readahead, NOMMU region, NUMA policy, and PFNMAP tracking reset.
- `vm_area_dup()` allocates a duplicate, copies state, duplicates PFNMAP tracking context if present, initializes the VMA lock, anon_vma chain, NUMA balancing state, and anon name.
- `vm_area_free()` asserts the VMA is detached, frees NUMA balancing state, anon name, PFNMAP tracking context, and returns it to the cache.

PFNMAP tracking:
- When `__HAVE_PFNMAP_TRACKING` is enabled, `vma_pfnmap_track_ctx_dup()` increments a kref on the tracking context unless it would overflow.
- `vma_pfnmap_track_ctx_release()` drops the reference and clears the VMA pointer.
- Stub versions are compiled otherwise.

Research notes:
- This file centralizes lifecycle invariants for VMA objects, separating allocation/dup/free mechanics from structural address-space manipulation.
- `vm_area_dup()` does not attach the duplicate into any tree; callers must finish policy/anon_vma/file setup and insert it through VMA APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vma_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vma_internal.h -->
# File Research: sources/os/linux/linux/mm/vma_internal.h

This internal header aggregates the kernel headers needed by `vma.c` and related VMA implementation files. It exists so VMA functionality can substitute these dependencies more easily in tests.

Content:
- Includes core mm/VMA dependencies: `mm.h`, `mm_types.h`, `mman.h`, `mmap_lock.h`, `mm_inline.h`, `mmu_context.h`, `pgtable.h`, `pagemap.h`, `rmap.h`, `swap.h`, and `internal.h`.
- Includes file and filesystem dependencies: `file.h`, `fs.h`, `backing-dev.h`, `shmem_fs.h`.
- Includes policy and special mapping support: `mempolicy.h`, `huge_mm.h`, `hugetlb.h`, `hugetlb_inline.h`, `userfaultfd_k.h`, `ksm.h`, `khugepaged.h`, `uprobes.h`.
- Includes synchronization, tree, debug, and scheduler support: `maple_tree.h`, `rwsem.h`, `mutex.h`, `rcupdate.h`, `sched/signal.h`, `mmdebug.h`, `bug.h`, `security.h`, and architecture `tlb.h` / `current.h`.

Research notes:
- There are no functions or data structures defined here beyond the include guard.
- Its main architectural role is dependency consolidation for the VMA implementation split.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vma_internal.h -->