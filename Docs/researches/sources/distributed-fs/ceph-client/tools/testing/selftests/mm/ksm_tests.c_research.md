# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_tests.c

## Purpose

`ksm_tests.c` is a Linux mm kselftest executable for Kernel Samepage Merging. It validates basic page merge and unmerge behavior, zero-page merging, NUMA-aware merging, and timing-oriented KSM performance paths. The same program can exercise both VMA-level `MADV_MERGEABLE` opt-in and process-wide `PR_SET_MEMORY_MERGE` opt-in.

## Important APIs, Types, and Functions

The main state type is `struct ksm_sysfs`, a snapshot of `/sys/kernel/mm/ksm` tunables that the test modifies and later restores. `enum ksm_merge_type` chooses `madvise(MADV_MERGEABLE)` versus `prctl(PR_SET_MEMORY_MERGE)`. `enum ksm_test_name` selects the command-line test mode.

Key helpers are `ksm_write_sysfs()`/`ksm_read_sysfs()`, `allocate_memory()`, `ksm_do_scan()`, `ksm_merge_pages()`, `ksm_unmerge_pages()`, `assert_ksm_pages_count()`, `ksm_save_def()`, and `ksm_restore()`. Test bodies are `check_ksm_merge()`, `check_ksm_unmerge()`, `check_ksm_zero_page_merge()`, `check_ksm_numa_merge()`, `ksm_merge_time()`, `ksm_merge_hugepages_time()`, `ksm_unmerge_time()`, and `ksm_cow_time()`.

## Control Flow

`main()` parses flags, verifies that KSM sysfs exists, saves current tunables, forces an aggressive scan configuration, runs one selected test, restores the original sysfs values, and returns the kselftest status. Merge tests allocate duplicate anonymous pages, opt them into KSM, start scanning by writing `run=1`, wait for enough `full_scans`, then compare `pages_shared` and `pages_sharing` against the expected sharing model. Unmerge tests write into merged pages and wait for KSM to observe the change. Timing paths measure scan, unmerge, or COW duration using `CLOCK_MONOTONIC_RAW`.

## State and Persistence Behavior

The test mutates persistent kernel tunables under `/sys/kernel/mm/ksm`: `run`, `pages_to_scan`, `sleep_millisecs`, `merge_across_nodes`, `use_zero_pages`, `max_page_sharing`, and `stable_node_chains_prune_millisecs`. It attempts to restore them before exit. Runtime allocations are anonymous mappings or NUMA allocations and are unmapped/freed in normal paths. `PR_SET_MEMORY_MERGE` process state is cleared where used.

## Dependencies and Integration Points

It depends on kselftest helpers, `vm_util.h`, `thp_settings.h`, libnuma, KSM sysfs, `/proc/self/ksm_stat`, `/proc/self/pagemap`, and transparent hugepage support for the hugepage timing mode. It integrates with the mm selftests Makefile as an opt-in executable that often requires root or writable KSM sysfs.

## Risks and Edge Cases

The `ksm_save_def()` and `ksm_restore()` expressions mix `||` with a ternary around `numa_available()`, which is subtle and easy to misread. Tests can leave sysfs tunables changed if they fail before restore. Timing tests are noisy and depend on scan speed, THP availability, NUMA topology, and page count. `assert_ksm_pages_count()` accounts for `max_page_sharing` groups and a leftover-page corner case. Hugepage counting includes a duplicated increment after `allocate_transhuge()` success in the visible code, so printed hugepage counts should be treated as diagnostic rather than a strict oracle.

## Test Signals

Pass signals are exact KSM counter relationships, successful unmerge to zero shared pages, zero-page behavior matching `use_zero_pages`, NUMA merge behavior matching `merge_across_nodes`, and timing output for merge/unmerge/COW scenarios. Skip signals include missing KSM, missing NUMA, insufficient NUMA nodes, or disabled THP.
