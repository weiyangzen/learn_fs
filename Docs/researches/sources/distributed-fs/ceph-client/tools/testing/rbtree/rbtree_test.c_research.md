# sources/distributed-fs/ceph-client/tools/testing/rbtree/rbtree_test.c

Purpose: userspace wrapper for the kernel red-black tree test suite.

Important APIs/types/functions: includes `../../../lib/rbtree_test.c`; `usage()` explains `-n`, `-p`, `-c`, `-r`; `rbtree_tests()` calls imported `rbtree_test_init()` and `rbtree_test_exit()`; `main()` populates imported globals `nnodes`, `perf_loops`, `check_loops`, and `seed`.

Control flow: command-line parsing is followed by a single `rbtree_tests()` run.

State and persistence: runtime configuration is kept in imported globals; no persistent state.

Dependencies/integration: depends on shared userspace kernel shims and the kernel `lib/rbtree_test.c` implementation. Built by `tools/testing/rbtree/Makefile`.

Risks and test signals: only thin-wrapper logic is local; behavioral pass/fail comes from imported tests and their assertions/output.
