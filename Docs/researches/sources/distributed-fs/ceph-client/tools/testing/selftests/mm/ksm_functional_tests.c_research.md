# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksm_functional_tests.c

## Purpose
`ksm_functional_tests.c` validates Kernel Samepage Merging behavior around merging, unmerging, zero pages, discarded PTEs, userfaultfd write protection, process-wide PRCTL controls, fork/exec inheritance, protected mappings, and per-process merge accounting.

## Important APIs, types, and functions
The file uses KSM helpers from `vm_util.h`, `/sys/kernel/mm/ksm` controls, `/proc/self/mem`, `/proc/self/pagemap`, `prctl(PR_SET_MEMORY_MERGE/PR_GET_MEMORY_MERGE)`, `madvise(MADV_MERGEABLE/MADV_UNMERGEABLE/MADV_DONTNEED/MADV_NOHUGEPAGE)`, and optional userfaultfd write-protect ioctls. `range_maps_duplicates()` compares PFNs to infer sharing. `__mmap_and_merge_range()` and `mmap_and_merge_range()` build mergeable ranges under a selected `enum ksm_merge_mode`.

## Control flow
`main()` handles a fork/exec child mode, sets a kselftest plan, initializes global file handles, then runs tests. `test_unmerge`, `test_unmerge_zero_pages`, and `test_unmerge_discarded` validate unmerging normal, zero, and partially discarded ranges. `test_unmerge_uffd_wp` adds UFFD-WP registration and write protection when supported. `test_prot_none` merges a `PROT_NONE` range, modifies half through `/proc/self/mem`, and unmerges the other half. PRCTL tests verify set/get, inheritance across fork, inheritance across exec of the same binary, and unmerge on disabling PRCTL merging. `test_fork_ksm_merging_page_count` ensures `ksm_merging_pages` accounting is not inherited by children.

## State and persistence behavior
The suite actively starts/stops KSM, writes `pages_to_scan` and `sleep_millisecs`, toggles zero-page merging, mmaps private anonymous memory, changes protections, forks/execs children, and reads pagemap PFNs. `stop_ksmd_and_restore_frequency()` restores selected KSM scan frequency values after the fork/exec test, but the suite generally assumes control of KSM sysfs state during execution.

## Dependencies and integration points
Requires KSM support and writable `/sys/kernel/mm/ksm` controls. Some checks require readable `/proc/self/pagemap`; `test_prot_none` requires `/proc/self/mem`; UFFD-WP coverage requires `__NR_userfaultfd` and `UFFD_FEATURE_PAGEFAULT_FLAG_WP`. The fork/exec test expects the binary to be available as `./ksm_functional_tests`.

## Risks and edge cases
PFN visibility may be restricted, causing skips. KSM merge timing is controlled through sysfs frequency but still depends on kernel scanning behavior. PRCTL operations may be unsupported on older kernels and are skipped on `EINVAL`. The child exit status encodes several failure modes that the parent maps to kselftest results.

## Test signals
Passing signals include absence of duplicate PFNs after unmerge operations, correct `ksm_zero_pages` accounting transitions, successful PRCTL set/get and inheritance behavior, no inherited child `ksm_merging_pages`, and expected UFFD-WP unmerge behavior when available.
