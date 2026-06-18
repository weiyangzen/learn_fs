# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/run_vmtests.sh

Purpose: top-level shell orchestrator for mm selftests, providing category selection, TAP output, hugepage preparation/restoration, optional destructive testing, and sequential execution of C binaries and wrapper scripts.

Important APIs and functions: `usage()` documents categories; `test_selected()` filters categories; `run_gup_matrix()` expands GUP combinations; `run_test()` prints banners, performs THP/hugetlb cleanup/compaction, captures status, counts pass/skip/fail, and emits TAP lines.

Control flow: parses options, computes hugepage needs from `/proc/meminfo`, tries to reserve hugetlb pages, detects 64-bit address support, then runs selected categories in fixed order. It can create temporary XFS loopback storage for `split_huge_page_test`.

State and dependencies: writes `/proc/sys/vm/nr_hugepages`, `drop_caches`, `compact_memory`, `shmmax`, `shmall`, Yama ptrace scope, optional hwpoison module state, and temporary mounts/images. Depends on root, compiled binaries, module tools, xfs utilities, and TAP skip semantics.

Risks and test signals: summary counts and TAP output are primary signals. Risk is high because it mutates global kernel knobs and appears to omit `d` from the `getopts` option string despite documenting destructive mode.
