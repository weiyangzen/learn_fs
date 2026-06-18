<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c

Purpose: Regression test ensuring explicit hugetlb mappings do not get confused with transparent huge pages.

Important APIs and types: Defines `SIZE`, `test_body()`, `test_main()`, and `main()`. Uses `mmap`, `madvise`, and kselftest harness helpers.

Control flow: The body maps a 16 MiB region, applies huge-page related advice, touches memory, and checks that hugetlb/THP behavior remains consistent with the kernel contract. `test_main` wraps skip conditions and harness execution.

State and persistence: Only transient anonymous mappings are used; no persistent state is kept.

Dependencies and integration points: Depends on Linux huge page/THP VM behavior, `utils.h`, and page-size support on the running kernel.

Risks: Host hugepage configuration can affect skip/failure interpretation. The test targets regressions in VM accounting and mapping selection rather than generic performance.

Test signals: Pass means the selected huge mapping behavior is stable; skip indicates missing required hugepage support/configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/hugetlb_vs_thp_test.c -->
