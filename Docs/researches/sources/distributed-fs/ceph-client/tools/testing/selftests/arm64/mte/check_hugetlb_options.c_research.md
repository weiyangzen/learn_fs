<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c

Purpose: tests MTE behavior on hugetlb mappings, including tag insertion, tag checking with TCO on/off, clearing PROT_MTE, and child tag inheritance.

Important APIs and functions: `default_huge_page_size`, `is_hugetlb_allocated`, `allocate_hugetlb`, `free_hugetlb`, `check_child_tag_inheritance`, `check_mte_memory`, `check_hugetlb_memory_mapping`, `check_clear_prot_mte_flag`, and `check_child_hugetlb_memory_mapping`.

Control flow: main sets up MTE and signal handlers, writes `/proc/sys/vm/nr_hugepages` to allocate two huge pages, verifies `MAP_HUGETLB | PROT_MTE` support, plans 12 tests, toggles PSTATE.TCO, runs hugetlb mapping and child inheritance tests across sync/async/no-error and mmap/mprotect modes, restores MTE setup, frees hugepages, and reports counts.

State and persistence: mutates global hugetlb pool via `/proc/sys/vm/nr_hugepages`; maps/unmaps huge pages; forks children. It attempts to free huge pages at the end.

Dependencies and integration: requires root or suitable privileges for hugepage allocation, hugetlb support, MTE support on huge pages, and shared MTE utilities.

Risks: early failure after `allocate_hugetlb` may skip `free_hugetlb`, leaving system hugepage count changed. System-wide hugepage pool mutation can disrupt other workloads. `tag_check` parameter is not meaningfully used in `check_mte_memory`.

Test signals: skips if PROT_MTE is unsupported with hugetlb; otherwise reports 12 kselftest cases with memory/tag/child inheritance diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_hugetlb_options.c -->
