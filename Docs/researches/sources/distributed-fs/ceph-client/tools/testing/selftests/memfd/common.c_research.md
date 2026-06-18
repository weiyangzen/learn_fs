# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.c

Purpose: shared memfd helpers and hugetlbfs mode toggle.

Important APIs/types/functions: global `hugetlbfs_test`, `default_huge_page_size()` parsing `/proc/meminfo`, and `sys_memfd_create()` wrapping `syscall(__NR_memfd_create)` while adding `MFD_HUGETLB` when hugetlbfs mode is active.

Control flow: huge page size helper reads lines until `Hugepagesize:` is found, converts kB to bytes, and returns zero on failure. The syscall wrapper mutates flags based on global mode.

State and persistence: process-global `hugetlbfs_test` controls memfd creation behavior.

Dependencies and integration points: `/proc/meminfo`, memfd uapi, syscall numbers.

Risks: global mode affects all callers in the process. Parser assumes the meminfo field spelling/spacing used by Linux.

Test signals: callers skip/fail when huge page size cannot be determined or memfd creation fails.
