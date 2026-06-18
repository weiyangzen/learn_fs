# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/cow.c

Purpose: extensive Copy-On-Write correctness tests across anonymous memory, THP, hugetlb, zeropage, memfd/tmpfile-backed private mappings, vmsplice, GUP pins, and optional io_uring fixed buffers.

Important APIs/types/functions: uses pagemap helpers, THP helpers, hugetlb size detection, `fork`, `pipe`, `vmsplice`, `mprotect`, `madvise(MADV_PAGEOUT|MADV_COLLAPSE|MADV_DONTFORK|MADV_DOFORK)`, `mremap`, `memfd_create`, `fallocate`, `ioctl` on `/sys/kernel/debug/gup_test`, optional liburing buffer registration/write-fixed, and kselftest logging helpers.

Control flow: test helpers create synchronized parent/child scenarios to detect leaks across COW boundaries. Anonymous tests cover parent writes, mprotect optimization, vmsplice pins in parent/child, optional io_uring long-term pins, and read-only long-term GUP/GUP-fast pins under shared/previously-shared/exclusive page states. Runners execute each case on base pages, swapped pages, PMD/PTE/single-PTE/partial THP forms, and hugetlb sizes. Additional THP collapse tests verify COW after `MADV_COLLAPSE` on fully or partially shared THPs. Non-anonymous tests cover shared zeropage, huge zeropage, memfd, tmpfile, and memfd-hugetlb mappings.

State and persistence: temporarily changes THP settings and restores them at the end, reads pagemap, opens debugfs `gup_test`, creates mappings/files, and may use swap/pageout.

Dependencies and integration points: mm helper files, `gup_test` debugfs for pin tests, optional liburing, THP/hugetlb/swap availability, pagemap access.

Risks: environment-sensitive skips are common. Some hugetlb vmsplice cases are marked expected failure. Correct THP restoration depends on normal process exit.

Test signals: dynamic kselftest plan from detected sizes/features; failures are content mismatches indicating COW isolation or pin reliability bugs.
