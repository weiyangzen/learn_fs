# sources/distributed-fs/ceph-client/tools/testing/rbtree/interval_tree_test.c

Purpose: userspace wrapper for the kernel interval-tree test suite.

Important APIs/types/functions: includes shared shims and `../../../lib/interval_tree_test.c`; `usage()` documents runtime tunables; `interval_tree_tests()` calls imported init/exit functions; `main()` parses `-n`, `-p`, `-q`, `-s`, `-a`, `-m`, and `-r` into imported globals such as `nnodes`, `perf_loops`, `nsearches`, `search_loops`, `search_all`, `max_endpoint`, and `seed`.

Control flow: parse options, initialize maple-tree support with `maple_tree_init()`, then run the interval-tree tests.

State and persistence: imported test globals hold configuration; no persistent files are written.

Dependencies/integration: links with interval-tree kernel library and maple-tree shared support. It is built by the local rbtree Makefile.

Risks and test signals: invalid options call `usage()` and exit `-1`; functional and performance results are produced by the imported test body.
