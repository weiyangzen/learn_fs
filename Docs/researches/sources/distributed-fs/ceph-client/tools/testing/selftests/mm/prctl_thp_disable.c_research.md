# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/prctl_thp_disable.c

Purpose: verifies `PR_SET_THP_DISABLE` and `PR_GET_THP_DISABLE`, including `PR_THP_DISABLE_EXCEPT_ADVISED`, against global THP policies and fork inheritance.

Important APIs and functions: `test_mmap_thp()` allocates a PMD-aligned anonymous range, applies optional `MADV_NOHUGEPAGE`, `MADV_HUGEPAGE`, or `MADV_COLLAPSE`, faults pages, and checks `AnonHugePages`. Fixture setup uses `thp_save_settings()`, edits global policy, and restores it in teardown.

Control flow: two fixtures run across `never`, `madvise`, and `always` global policy variants. Each fixture has `nofork` and `fork` tests, proving current-process behavior and child inheritance.

State and dependencies: modifies process prctl state and global THP sysfs settings through `thp_settings`. Depends on THP availability, PMD size discovery, `MADV_COLLAPSE`, `kselftest_harness.h`, and `vm_util.h`.

Risks and test signals: failures indicate broken prctl value reporting, incorrect override precedence, or missing fork inheritance. Interrupted runs can leave global THP sysfs settings changed.
