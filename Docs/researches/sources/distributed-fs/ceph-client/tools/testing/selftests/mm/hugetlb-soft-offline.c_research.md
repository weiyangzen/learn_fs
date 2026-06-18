# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-soft-offline.c

## Purpose
`hugetlb-soft-offline.c` validates `MADV_SOFT_OFFLINE` behavior for HugeTLB pages with `/proc/sys/vm/enable_soft_offline` both enabled and disabled.

## Important APIs, types, and functions
`do_soft_offline()` creates a populated hugetlb mapping and calls `madvise(..., MADV_SOFT_OFFLINE)` on an address inside it. `set_enable_soft_offline()` writes the sysctl using `popen("echo ...")`. `read_nr_hugepages()` reads the relevant sysfs `nr_hugepages` file. `create_hugetlbfs_file()` creates and validates a hugetlb memfd. `test_soft_offline_common()` orchestrates one enabled/disabled case.

## Control flow
`main()` sets a two-test plan, runs the enabled case expecting successful soft offline and one fewer hugepage in `nr_hugepages`, then runs the disabled case expecting `EOPNOTSUPP` and unchanged hugepage count.

## State and persistence behavior
The test changes the global `enable_soft_offline` sysctl and observes persistent hugetlb pool count changes. It creates a temporary hugetlb memfd and resets its size to zero after each mapping. The code does not restore the sysctl to its original value, so callers must run it in a controlled environment.

## Dependencies and integration points
Requires root-like permission to write `/proc/sys/vm/enable_soft_offline`, hugetlb memfd support, and sysfs hugepage counters under `/sys/kernel/mm/hugepages/hugepages-<size>kB/`.

## Risks and edge cases
Global sysctl mutation is invasive. Exact hugepage count comparisons can be disturbed by concurrent hugepage activity. The test checks `errno` after `madvise()` and expects it to match the configured mode.

## Test signals
The two kselftest results pass when the enabled run reduces `nr_hugepages` by one and the disabled run preserves the count while returning the expected unsupported error.
