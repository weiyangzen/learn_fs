# sources/distributed-fs/ceph-client/include/linux/ksm.h

## Purpose

`ksm.h` declares Kernel Samepage Merging interfaces for marking VMAs/MMs mergeable, handling fork/exec/exit, tracking KSM zero pages, copying swapped KSM pages, reverse mapping, migration, and process profitability. The source was read as a complete 164-line file.

## Important APIs, Types, and Functions

With `CONFIG_KSM`, APIs include `ksm_madvise()`, `ksm_vma_flags()`, `ksm_enable_merge_any()`, `ksm_disable_merge_any()`, `ksm_disable()`, `__ksm_enter()`, `__ksm_exit()`, `ksm_map_zero_page()`, `ksm_might_unmap_zero_page()`, `mm_ksm_zero_pages()`, `ksm_fork()`, `ksm_execve()`, `ksm_exit()`, `ksm_might_need_to_copy()`, `rmap_walk_ksm()`, `folio_migrate_ksm()`, `collect_procs_ksm()`, `ksm_process_profit()`, and `ksm_process_mergeable()`.

## Control Flow

`madvise()` and merge-any paths set mm/VMA mergeability, mm lifecycle hooks enroll or remove address spaces, ksmd scans and merges identical anonymous pages, and fault/swap paths call `ksm_might_need_to_copy()` when a former KSM page may need private ownership.

## State and Persistence Behavior

KSM state is in mm flags, counters such as `ksm_zero_pages`, per-mm KSM fields, rmap items, and merged folios. State persists while address spaces and merged pages exist.

## Dependencies and Integration Points

It integrates with MM, pagemap, rmap, scheduler/mm lifecycle, folio migration, zero page accounting, and `madvise()`.

## Risks and Edge Cases

KSM zero page tracking reuses PTE dirty bit semantics. Fork enrollment is best effort. Swap-in of former KSM pages can require copying because anon_vma context may no longer match. Disabled builds stub most behavior.

## Test Signals

KSM selftests, madvise merge/unmerge tests, fork/exec/exit tests, zero-page accounting tests, swap-in copy tests, folio migration tests, and disabled-config build coverage are useful.
