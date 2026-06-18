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
