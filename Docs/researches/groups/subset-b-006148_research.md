# Research: subset-b-006148

Work item `subset-b-006148` covers the VMA, userfaultfd, hardened usercopy, and mm utility files under `sources/distributed-fs/ceph-client/mm/`. The sections below are source-tree aligned and wrapped for reconciliation into one report per source file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/usercopy.c -->
# sources/distributed-fs/ceph-client/mm/usercopy.c

## Purpose

`usercopy.c` implements the hardened usercopy object-size validator used by `copy_to_user()` and `copy_from_user()` paths. It rejects kernel text exposure, bogus addresses, invalid stack ranges, and heap/slab/vmalloc ranges that exceed allocator-owned objects or explicit slab usercopy whitelists. It also wires the runtime `hardened_usercopy=` boot option into the `validate_usercopy_range` static key.

## Important APIs, Types, and Functions

- `DEFINE_STATIC_KEY_MAYBE_RO(CONFIG_HARDENED_USERCOPY_DEFAULT_ON, validate_usercopy_range)` exports the static branch controlling whether call sites perform object validation.
- `__check_object_size(const void *ptr, unsigned long n, bool to_user)` is the exported validator. It is the public integration point for usercopy range checks.
- `usercopy_abort(...)` logs the attempted exposure or overwrite and ends execution with `BUG()`.
- `check_stack_object()` classifies a range as `NOT_STACK`, `GOOD_FRAME`, `GOOD_STACK`, or `BAD_STACK` using `task_stack_page(current)`, `THREAD_SIZE`, `arch_within_stack_frames()`, and optionally `current_stack_pointer`.
- `check_heap_object()` validates kmap, vmalloc, slab, and compound-page allocations. Slab allocations are delegated to `__check_heap_object()`.
- `check_kernel_text_object()` rejects overlap with `_stext.._etext` and the linear alias returned by `lm_alias()`.
- `parse_hardened_usercopy()` and `set_hardened_usercopy()` parse the boot parameter and enable/disable the static branch at `late_initcall`.

## Control Flow

`__check_object_size()` first returns immediately for zero-length copies. It then rejects wrapped or null/zero-size addresses via `check_bogus_address()`. Stack ranges are checked before heap ranges: a valid stack frame/range returns successfully, while a partial or below-current-stack object aborts. Non-stack ranges proceed to heap validation, where kmap objects must stay in one page, vmalloc objects must stay inside a live vmap area when page faults are enabled, slab objects are checked against allocator metadata, and compound page allocations must stay inside the compound allocation. Finally, the range is checked against kernel text and linear text aliases.

## State and Persistence

There is no durable per-object state. Runtime state consists of the read-mostly static key `validate_usercopy_range` and the `__initdata` `enable_checks` boot-parameter value. The rest of the logic derives state from current task stack metadata, vmap metadata, slab/page metadata, and linker section symbols.

## Dependencies and Integration Points

This file depends on scheduler/task stack APIs, architecture stack-frame helpers, vmalloc/vmap lookup, slab internals through `slab.h`, highmem/kmap predicates, linker section symbols, `lm_alias()`, static keys, and boot parameter parsing. Its exported symbols are consumed by hardened usercopy call sites in architecture and generic uaccess code.

## Risks

- False negatives are possible for non-compound page allocations because the allocator cannot reliably know whether a multi-page non-compound allocation is being crossed.
- vmalloc checking is skipped while page faults are disabled, so callers must not assume vmalloc bounds are always enforced in atomic contexts.
- `usercopy_abort()` uses `BUG()`, so any false positive is fatal.
- Correctness depends on architecture implementations of stack frame introspection and linear text aliasing.

## Test Signals

Useful signals include hardened usercopy LKDTM tests, slab usercopy whitelist tests, stack copy boundary tests, vmalloc/kmap range tests, booting with `hardened_usercopy=on/off`, and observing that invalid copies produce the expected emergency log and BUG while valid stack/slab/vmalloc copies proceed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/userfaultfd.c -->
# sources/distributed-fs/ceph-client/mm/userfaultfd.c

## Purpose

`userfaultfd.c` implements kernel-side helpers for userfaultfd operations over ordinary VMAs: atomic missing-page fill, zero-page fill, continue, poison, write-protect changes, zero-copy anonymous page moves, registration, clear, and release. It coordinates VMA lookup/locking, page-table installation, mmu notifier invalidation, rmap updates, hugetlb special cases, and VMA flag/context mutation.

## Important APIs, Types, and Functions

- `struct mfill_state` carries one atomic fill operation: userfaultfd context, source/destination ranges, mode flags, current VMA, current source/destination page addresses, and destination PMD.
- `vma_uffd_ops()` selects anonymous UFFD operations or filesystem-provided `vm_ops->uffd_ops`.
- `validate_dst_vma()` ensures a destination range stays inside a single registered VMA.
- `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, and `mfill_atomic_poison()` are exported operation helpers that select a mode and call `mfill_atomic()`.
- `mwriteprotect_range()` and `uffd_wp_range()` apply or resolve userfaultfd write protection over VMA ranges.
- `move_pages()` implements `UFFDIO_MOVE` for anonymous, compatible VMAs, returning either bytes moved or a negative error.
- `vma_can_userfault()`, `userfaultfd_register_range()`, `userfaultfd_clear_vma()`, `userfaultfd_release_new()`, and `userfaultfd_release_all()` manage VMA eligibility and context/flag lifecycle.
- `double_pt_lock()` and `double_pt_unlock()` impose deterministic page-table-lock ordering for source/destination PTE operations.

## Control Flow

Atomic fill starts in `mfill_atomic()`, which validates page alignment/wrap conditions, locks a destination VMA with either per-VMA locking or `mmap_read_lock()`, takes `ctx->map_changing_lock`, checks `ctx->mmap_changing`, rejects unsupported modes, and dispatches hugetlb ranges to `mfill_atomic_hugetlb()`. For normal PTEs it establishes a PMD, selects the page-level handler, and advances page by page, returning a partial byte count if progress was made before an error or fatal signal.

Copy/zero fill allocates or obtains a folio through `vm_uffd_ops`, copies from userspace with a retry path that temporarily drops mapping locks to avoid mmap-lock deadlocks, marks the folio uptodate, optionally inserts it into file cache, and installs the PTE with `mfill_atomic_install_pte()`. PTE installation constructs dirty/writable/UFFD-WP PTEs, rejects non-empty destinations except allowed UFFD markers, updates rmap/mm counters, unlocks file-cache folios after successful install, and updates the MMU cache. Continue looks up an existing file-cache folio without allocation. Poison installs a poisoned PTE marker and refuses to overwrite any existing PTE.

`mwriteprotect_range()` walks VMAs under `mmap_read_lock()` and `map_changing_lock`, verifies each VMA is UFFD-WP capable, handles hugetlb alignment, and calls `uffd_wp_range()`, which wraps `change_protection()` in an `mmu_gather`.

`move_pages()` locks source and destination VMAs, validates that ranges are single-VMA, anonymous, writable, non-shared, compatible, and registered with the same context. It then walks PMD/PTE ranges. Huge PMDs may be moved whole if naturally aligned and destination-empty; otherwise they are split. PTE moves handle present anonymous folios, zero pages, swap entries, migration entries, holes, and destination-exists conditions. `move_pages_ptes()` uses mmu notifier invalidation and carefully rechecks PTE and PMD stability after taking locks.

Registration walks the target range with the mmap write lock held, validates `vma_can_userfault()`, uses `vma_modify_flags_uffd()` to split or merge as needed, assigns `vm_userfaultfd_ctx`, sets UFFD flags, and disables hugetlb PMD sharing when necessary. Release paths reset matching VMA contexts and clear UFFD flags, using `userfaultfd_clear_vma()` to resolve outstanding write-protect PTEs before flag removal.

## State and Persistence

The durable state is embedded in VMAs and page tables: `vma->vm_userfaultfd_ctx`, `VM_UFFD_*` flags, UFFD-WP PTE bits/markers, poison markers, and moved/installed PTE mappings. Transient state includes `mfill_state`, `ctx->map_changing_lock`, `ctx->mmap_changing`, PMD/PTE locks, folio locks/references, mmu notifier ranges, and hugetlb fault mutexes. Successful registration persists until explicit release, VMA modification, or process teardown.

## Dependencies and Integration Points

This file integrates with core mm locking (`mmap_lock`, per-VMA locks, page-table locks), VMA mutation from `vma.c`, folio allocation/rmap/LRU/memcg, shmem/filesystem `vm_uffd_ops`, hugetlb helpers, transparent huge page split/move helpers, swap and migration entries, mmu notifiers, TLB/cache flushing, soft-dirty support, and the userfaultfd context in `linux/userfaultfd_k.h`.

## Risks

- Many paths intentionally return `-EAGAIN` when mappings change, PMDs collapse/split, PTEs race, or per-VMA locking cannot stabilize the range. User space must be prepared to retry.
- `move_pages()` is conservative: shared, file-backed, PFNMAP/IO/MIXEDMAP/hugetlb/shadow-stack, non-writable, mlocked-mismatch, and protection-mismatch cases are rejected.
- Atomic fill can return partial progress; callers must not treat a short positive result as full success.
- Correctness depends on exact lock ordering between mmap locks, VMA locks, hugetlb locks, folio locks, and page-table locks.
- File-size checks prevent filling beyond EOF only while PTE locks are held; filesystem size and page-cache behavior are central to correctness.
- UFFD-WP on shared mappings changes write-notify/page-protection behavior, so interactions with dirty tracking and filesystem writeback need coverage.

## Test Signals

Signals include selftests for `UFFDIO_COPY`, `ZEROPAGE`, `CONTINUE`, `POISON`, `WRITEPROTECT`, and `MOVE`; hugetlb and THP variants; concurrent `mremap()`/`munmap()`/fork retry behavior; partial-progress/fatal-signal behavior; EOF fill rejection; WP marker support disabled/enabled cases; and mmu notifier/rmap validation under KASAN, lockdep, and debug VM configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/userfaultfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/util.c -->
# sources/distributed-fs/ceph-client/mm/util.c

## Purpose

`util.c` provides broad memory-management utilities: kernel/user memory duplication helpers, stack and mmap randomization, locked-memory accounting, wrappers around `do_mmap()`, vmalloc array helpers, folio mapping/copy helpers, overcommit sysctls and accounting, task command-line extraction, object provenance reporting, page-offline synchronization, VMA mmap compatibility shims, page snapshots, mmap action preparation/completion, and selected folio/PFN helpers.

## Important APIs, Types, and Functions

- String/memory helpers: `kfree_const()`, `kstrdup()`, `kstrdup_const()`, `kstrndup()`, `kmemdup_noprof()`, `kmemdup_array()`, `kvmemdup()`, `kmemdup_nul()`, `memdup_user()`, `vmemdup_user()`, `strndup_user()`, and `memdup_user_nul()`.
- VMA/setup helpers: `vma_is_stack_for_current()`, `vma_set_file()`, `randomize_stack_top()`, `randomize_page()`, `arch_randomize_brk()`, `arch_mmap_rnd()`, and `arch_pick_mmap_layout()`.
- Lock/accounting/mapping helpers: `__account_locked_vm()`, `account_locked_vm()`, `vm_mmap_pgoff()`, `vm_mmap()`, and optional `vm_mmap_shadow_stack()`.
- Virtual allocation helpers: `__vmalloc_array_noprof()`, `vmalloc_array_noprof()`, `__vcalloc_noprof()`, and `vcalloc_noprof()`.
- Folio/page helpers: `folio_anon_vma()`, `folio_mapping()`, `folio_copy()`, `folio_mc_copy()`, `memcmp_pages()`, `flush_dcache_folio()`, `snapshot_page()`, `folio_pte_batch()`, and `page_range_contiguous()`.
- Overcommit state: `sysctl_overcommit_memory`, `sysctl_max_map_count`, `sysctl_user_reserve_kbytes`, `sysctl_admin_reserve_kbytes`, `vm_committed_as`, `vm_commit_limit()`, `vm_memory_committed()`, and `__vm_enough_memory()`.
- Mmap compatibility/action helpers: `compat_set_desc_from_vma()`, `__compat_vma_mmap()`, `compat_vma_mmap()`, `mmap_action_prepare()`, and `mmap_action_complete()`.

## Control Flow

The allocation helper group either duplicates kernel memory with kmalloc/kvmalloc or duplicates userspace memory with `copy_from_user()`, returning `ERR_PTR()` for user-copy failures. `user_buckets` is initialized at `subsys_initcall()` for user memdup allocations.

ASLR helpers compute stack, brk, and mmap base randomization from process flags, compat mode, rlimits, `mmap_rnd_bits`, and layout personality. `arch_pick_mmap_layout()` selects legacy bottom-up or top-down layout and updates `MMF_TOPDOWN`.

Locked memory accounting updates `mm->locked_vm` under the mmap write lock and enforces `RLIMIT_MEMLOCK` unless the caller bypasses it. `vm_mmap_pgoff()` performs LSM and fsnotify checks, takes `mmap_write_lock_killable()`, calls `do_mmap()`, unlocks, completes userfaultfd unmap notifications, and populates prefaulted memory.

Overcommit sysctls update the global policy, ratio, or kbytes values. Switching to strict overcommit recomputes batching and synchronizes the per-CPU committed counter on each CPU before publishing the policy. `__vm_enough_memory()` reserves virtual memory, applies policy-specific checks and admin/user reserves, logs failures, and unaccounts on denial.

The compatibility mmap path converts a live VMA into `struct vm_area_desc`, invokes `.mmap_prepare()` on stacked drivers, copies descriptor fields back to the VMA, prepares/remaps requested PFN/kernel-page actions, then completes mapped/success/error hooks. `mmap_action_finish()` may unmap a newly created VMA on action failure outside compatibility mode.

`snapshot_page()` repeatedly copies struct page/folio metadata to produce a stable-ish `page_snapshot`; it marks the snapshot unfaithful if compound state cannot be reconciled after retries.

## State and Persistence

Persistent or global state includes overcommit sysctls, `vm_committed_as`, `sysctl_max_map_count`, reserve kbytes, and the `user_buckets` allocator. Per-mm state changes include `mmap_base`, `MMF_TOPDOWN`, `locked_vm`, and mappings created by `vm_mmap*()`. VMA state can be mutated by `vma_set_file()`, compatibility mmap descriptor application, action completion, and mapped hooks. Page-offline coordination is guarded by a static `rw_semaphore`.

## Dependencies and Integration Points

The file depends on uaccess, security/LSM hooks, fsnotify, mmap/do_mmap, userfaultfd unmap completion, rlimits/capabilities, sysctl registration, percpu counters, hugetlb accounting, folio/page-cache/swap helpers, architecture randomization hooks, VMA descriptor/action APIs, remap helpers, KUnit export visibility, and optional architecture shadow-stack support.

## Risks

- User duplication helpers must handle oversized lengths and `copy_from_user()` faults correctly; `memdup_user_nul()` adds one byte and depends on allocator overflow safety in the bucket allocator path.
- `vma_set_file()` assumes use only during initial setup and takes/drops file references around a swap; misuse on anonymous or established VMAs can corrupt mapping lifetime.
- Overcommit policy changes and committed memory counters are global, performance-sensitive, and race-prone without the explicit sync path.
- `vm_mmap_pgoff()` must always pair userfaultfd completion and population after unlocking; failures in `do_mmap()` must not leak locks or uf list state.
- Compatibility `.mmap_prepare()` handling allows drivers to change whitelisted fields; incorrect field propagation can break VMA merge, rmap visibility, or file references.
- `snapshot_page()` is best-effort for concurrently changing compound pages, so consumers must check snapshot faithfulness.

## Test Signals

Signals include unit or selftests for string/memory duplication fault paths, ASLR layout bounds, memlock rlimit enforcement, `vm_mmap()` offset overflow/alignment, strict overcommit sysctl transitions, task cmdline extraction after `setproctitle()`-style overwrites, mmap action prepare/complete error unwinding, page snapshot fidelity under folio split, and sparsemem `page_range_contiguous()` debug cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma.h -->
# sources/distributed-fs/ceph-client/mm/vma.h

## Purpose

`vma.h` declares and inlines the core VMA manipulation API implemented by `vma.c`, `vma_init.c`, and `vma_exec.c`. It defines operation-state structures for merge, munmap, preparation, unlink batching, and unmap descriptors, plus helper macros and iterator wrappers used across MM code.

## Important APIs, Types, and Functions

- `struct vma_prepare` describes the VMAs, file mapping, anon_vma, insert/remove targets, and uprobe behavior for a pending VMA mutation.
- `struct unlink_vma_file_batch` batches up to eight file-backed VMAs sharing a mapping for unlinking from `i_mmap`.
- `struct vma_munmap_struct` tracks a munmap operation: iterator, first/prev/next VMAs, userfaultfd list, aligned range, PTE-clearing range, detached counts, accounting totals, and unlock behavior.
- `enum vma_merge_state` and `struct vma_merge_struct` encode a merge attempt and its mutable internal flags.
- `struct unmap_desc`, `unmap_all_init()`, `unmap_pgtable_init()`, and `UNMAP_STATE` parameterize page-table unmap/free operations.
- `VMG_STATE` and `VMG_VMA_STATE` initialize merge state for new ranges and existing VMA modifications.
- Public prototypes cover VMA expand/shrink/modify/merge, munmap, unlink batching, copy, anon-vma lookup, dirty tracking, all-lock collection, mmap/brk/gap search, stack expansion, insertion, allocation/dup/free, and exec stack helpers.
- Inline helpers wrap maple-tree VMA iterator operations and classify mappings as exec/stack/data.
- `map_deny_write_exec()` implements MDWE policy checks for writable-executable or newly executable mappings.

## Control Flow

The header itself does not execute high-level operations, but its initializer macros determine how callers seed merge and munmap state. `VMG_VMA_STATE` snapshots a VMA's flags, pgoff, file, anon_vma, policy, UFFD context, and anon name so modification helpers can compare against neighbors. Iterator helpers normalize maple tree range setup, preallocation, store, clear, load, previous/next range movement, and gap finding.

Mapping classifiers feed accounting code: executable mappings are executable, non-writable, non-stack; stack mappings include `VM_STACK` and shadow stacks; data mappings are private writable non-stack ranges. `map_deny_write_exec()` first exits unless current mm has MDWE, then denies new executable mappings that are writable or transitions from non-executable to executable.

## State and Persistence

The structs in this header are transient operation state, but they reference persistent mm/VMA/file/anon-vma/mapping state. Inline store helpers mark VMAs attached and update maple-tree ranges. MDWE checks read `current->mm` flags but do not mutate state.

## Dependencies and Integration Points

The API is tightly coupled to `struct vm_area_struct`, `struct mm_struct`, `vma_iterator`, maple-tree `ma_state`, mempolicy, anon-vma names, userfaultfd contexts, `struct vm_area_desc`, page-table constants, stack direction configuration, `CONFIG_MMU`, `CONFIG_DEBUG_VM_MAPLE_TREE`, `CONFIG_STACK_GROWSUP`, and `CONFIG_64BIT` sealed VMA support.

## Risks

- Callers must respect comments about iterator position, mmap lock mode, and whether actual flag/name/policy mutations are applied by the caller after split/merge preparation.
- `struct vma_merge_struct` is intentionally mutated during merge; callers cannot rely on fields retaining input values after helper calls.
- Iterator helpers store ranges as `[start, end - 1]`; off-by-one errors in callers can corrupt maple-tree coverage.
- `vma_set_file()` compatibility helper in this header assumes partially established VMA state and should not be treated as a general VMA mutation API.
- MDWE checks rely on old/new VMA flag sets being accurate, especially in mprotect-like flows.

## Test Signals

Signals include compile coverage across MMU/NOMMU, stack grows up/down, 32/64-bit, debug maple tree, and MDWE configs; API consumers that exercise split/merge/munmap/mmap paths; maple-tree validation; and tests verifying mapping accounting classifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_exec.c -->
# sources/distributed-fs/ceph-client/mm/vma_exec.c

## Purpose

`vma_exec.c` contains VMA-only helpers used during `execve()` setup: creation of the temporary initial stack VMA at the architecture maximum stack address and relocation of that stack VMA downward once the final placement is known.

## Important APIs, Types, and Functions

- `create_init_stack_vma(struct mm_struct *mm, struct vm_area_struct **vmap, unsigned long *top_mem_p)` allocates and inserts the one-page initial stack VMA with `VM_STACK_FLAGS | VM_STACK_INCOMPLETE_SETUP`.
- `relocate_vma_down(struct vm_area_struct *vma, unsigned long shift)` expands a VMA to cover old and new stack ranges, moves page tables downward, frees old page-table ranges, and shrinks the VMA to the relocated range.
- The implementation uses `VMG_STATE`, `vma_expand()`, `PAGETABLE_MOVE`, `move_page_tables()`, `free_pgd_range()`, `mmu_gather`, and `vma_shrink()`.

## Control Flow

`create_init_stack_vma()` allocates a VMA, marks it anonymous, takes the mmap write lock killably, runs `ksm_execve()`, initializes a one-page stack at `[STACK_TOP_MAX - PAGE_SIZE, STACK_TOP_MAX)`, applies soft-dirty when supported, sets page protections, inserts it with `insert_vm_struct()`, initializes `mm->stack_vm` and `mm->total_vm`, unlocks, and returns the VMA plus the highest word-addressable stack location. Error paths unwind KSM, mmap lock, and the VMA allocation.

`relocate_vma_down()` computes old/new ranges, verifies no VMA exists between the new start and old VMA, expands the VMA to cover `[new_start, old_end)`, moves page tables with `for_stack = true`, frees the cleared old PGD range with different bounds for overlapping versus non-overlapping moves, then shrinks the VMA to `[new_start, new_end)`.

## State and Persistence

The functions mutate the target `mm_struct` and stack VMA: VMA range, pgoff, page tables, `mm->stack_vm`, `mm->total_vm`, KSM exec state, and maple-tree placement. Transient state includes `vma_iterator`, `vma_merge_struct`, `mmu_gather`, and `pagetable_move_control`.

## Dependencies and Integration Points

This file depends on VMA allocation/insertion/expand/shrink from the VMA subsystem, KSM exec hooks, architecture stack limits, page-table movement/freeing, mmap locking, soft-dirty support, and exec code that later finalizes stack placement.

## Risks

- The relocation helper is explicitly specialized for early exec stack relocation; using it for general VMA moves would bypass many checks that `mremap()` or mmap paths perform.
- If `move_page_tables()` moves only a partial range, the function returns `-ENOMEM` and relies on process cleanup to remove the inconsistent intermediate state.
- The no-intervening-VMA check and range arithmetic must hold, or expansion can cover an unintended mapping.
- Error unwinding in initial stack creation must keep KSM and mmap lock state balanced.

## Test Signals

Signals include execve tests across stack-randomization paths, failure injection for `vm_area_alloc()`, `mmap_write_lock_killable()`, `ksm_execve()`, `insert_vm_struct()`, and `move_page_tables()`, plus debug VM/maple-tree validation after stack relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_init.c -->
# sources/distributed-fs/ceph-client/mm/vma_init.c

## Purpose

`vma_init.c` owns initialization, allocation, duplication, and freeing of `struct vm_area_struct` objects shared by MMU and NOMMU configurations. It sets up the VMA slab cache and centralizes field copying and cleanup for VMA lifetime management.

## Important APIs, Types, and Functions

- `vma_state_init()` creates the `vm_area_struct` kmem cache with a free pointer offset, sheaf capacity, cacheline alignment, panic-on-failure, RCU type safety, and accounting.
- `vm_area_alloc(struct mm_struct *mm)` allocates from the VMA cache and calls `vma_init()`.
- `vm_area_dup(struct vm_area_struct *orig)` allocates and initializes a copy of an existing VMA, including locks, anon-vma chain, NUMA balancing state, anon name, and optional PFNMAP tracking.
- `vm_area_free(struct vm_area_struct *vma)` asserts detachment and releases NUMA, anon-name, PFNMAP tracking, and slab storage.
- `vm_area_init_from()` is the internal field-by-field copier.
- Optional `vma_pfnmap_track_ctx_dup()` and `vma_pfnmap_track_ctx_release()` reference-count PFNMAP tracking contexts.

## Control Flow

The boot-time `vma_state_init()` configures the cache before VMA allocations are needed. `vm_area_alloc()` performs a plain allocation and initializes a fresh VMA for an mm. `vm_area_dup()` allocates raw storage, asserts exclusive writer access to key mutable fields in the original, copies structural fields, duplicates optional PFNMAP tracking with kref protection, initializes the VMA lock as already detached/new, initializes anon-vma chain and NUMA state, and duplicates anon-vma names. `vm_area_free()` asserts the VMA is detached from address-space structures before releasing auxiliary state and freeing the object.

## State and Persistence

The persistent allocator state is the static `vm_area_cachep`. Per-VMA copied state includes mm, ops, range, anon_vma pointer, pgoff, file pointer, private data, flags, page protection, shared interval-tree node contents, userfaultfd context, optional anon name, swap readahead, NOMMU region, NUMA policy, and PFNMAP tracking. Duplication does not itself take file or mempolicy references; callers in `vma.c` handle those as part of split/copy operations.

## Dependencies and Integration Points

This file depends on slab APIs, `vma_init()`, VMA lock initialization, anon-vma name helpers, NUMA balancing state helpers, optional swap/NOMMU/NUMA/PFNMAP features, RCU-safe VMA cache semantics, and all VMA mutation code that allocates, duplicates, or frees VMAs.

## Risks

- Field copying is intentionally selective; adding fields to `struct vm_area_struct` requires auditing this copier.
- `shared` is copied with `data_race()` because `dup_mmap()` may see concurrent modification, and consumers must reinitialize/link it appropriately before use.
- PFNMAP tracking duplication can fail on reference-count saturation, making VMA duplication fail.
- `vm_area_free()` assumes the VMA has already been detached; freeing attached VMAs would leave stale maple-tree or interval-tree references.
- File, mempolicy, and anon-vma chain lifetime adjustments are split between this file and callers, so misuse can leak or double-release references.

## Test Signals

Signals include boot/slab initialization checks, split/mremap/fork paths using `vm_area_dup()`, debug assertions for detached frees, PFNMAP tracking reference tests, NUMA/anon-name cleanup checks, and configuration matrix builds with swap, NOMMU, NUMA, and PFNMAP tracking toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_internal.h -->
# sources/distributed-fs/ceph-client/mm/vma_internal.h

## Purpose

`vma_internal.h` is the private include aggregator for VMA implementation files. It centralizes the kernel and architecture headers required by `vma.c`, `vma_exec.c`, and `vma_init.c`, with a comment noting that these headers can be substituted when testing VMA functionality.

## Important APIs, Types, and Functions

The file declares no functions or data structures of its own. Its important role is dependency aggregation. It includes headers for backing devices, bit operations, filesystems, hugetlb, KSM/khugepaged, lists, maple trees, mempolicy, core mm types, mmap locking/debugging, MMU context, mutexes/rwsems, pagemap, perf events, personality, PFN helpers, RCU, rmap, scheduler signals, security, shmem, swap, uprobes, userfaultfd, page tables, current task, TLB handling, and local `"internal.h"`.

## Control Flow

There is no runtime control flow. Inclusion order provides compile-time visibility for VMA implementation code.

## State and Persistence

This header has no state. It exposes definitions and declarations for code that mutates VMAs, page tables, mappings, locks, policies, and accounting elsewhere.

## Dependencies and Integration Points

Its integration point is compilation: VMA source files include this private header before `"vma.h"`. By grouping broad MM dependencies here, implementation files stay focused and tests can potentially replace this include surface with stubs or controlled substitutes.

## Risks

- Aggregator headers can hide excessive dependencies; changes here may mask missing direct includes in implementation files.
- Testing substitution only works if the replacement supplies every type/helper actually used by the VMA implementation.
- Include-order changes can affect inline definitions, configuration guards, or architecture-specific declarations.

## Test Signals

Signals include successful builds across the VMA-related configuration matrix, compile-only tests with substituted test headers if available, and include-what-you-use or dependency-pruning checks to catch accidental reliance on unrelated transitive includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vma_internal.h -->
