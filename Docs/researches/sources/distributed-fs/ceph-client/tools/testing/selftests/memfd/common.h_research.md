# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/common.h

Purpose: declarations for shared memfd helpers.

Important APIs/types/functions: declares `extern int hugetlbfs_test`, `default_huge_page_size()`, and `sys_memfd_create()`.

Control flow: none.

State and persistence: exposes the process-global hugetlbfs mode.

Dependencies and integration points: included by `memfd_test.c` and `fuse_test.c`.

Risks: direct global access can make mode changes implicit across helper users.

Test signals: none directly.
