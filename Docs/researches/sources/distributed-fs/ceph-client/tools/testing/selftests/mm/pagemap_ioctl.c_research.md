# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pagemap_ioctl.c

Purpose: broad regression coverage for the `/proc/self/pagemap` `PAGEMAP_SCAN` ioctl, especially `PAGE_IS_WRITTEN` tracking with userfaultfd asynchronous write protection across anonymous, file-backed, THP, hugetlb, memfd, shmem, unmapped, mprotect, concurrent-fault, and PFN-zero cases.

Important APIs and functions: `pagemap_ioctl()` and `pagemap_ioc()` build `struct pm_scan_arg`; `init_uffd()`, `wp_init()`, `wp_addr_range()`, and `wp_free()` manage userfaultfd write protection; `base_tests()`, `sanity_tests_sd()`, `sanity_tests()`, `hpage_unit_tests()`, `mprotect_tests()`, `transact_test()`, `userfaultfd_tests()`, and `zeropfn_tests()` provide the scenarios.

Control flow: `main()` initializes userfaultfd, opens pagemap, sets a 117-test plan, then runs validation over normal pages, large ranges, THP, hugetlb variants, file mappings, walk-end handling, concurrent updates, unmapped ranges, and zero-page detection.

State and dependencies: state is per-process mappings, temporary files/memfds, SYSV shm IDs, `pagemap_fd`, `uffd`, and kernel write-protect metadata. It depends on recent pagemap scan categories, userfaultfd WP async features, hugepage availability, `vm_util.h`, and kselftest.

Risks and test signals: failures show wrong return counts, malformed `page_region` ranges/categories, incorrect `walk_end`, lost concurrent updates, hugepage accounting errors, or bad `PAGE_IS_PFNZERO` classification. Some temp files are not explicitly unlinked.
