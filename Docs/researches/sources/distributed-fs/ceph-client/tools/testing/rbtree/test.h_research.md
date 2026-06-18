# sources/distributed-fs/ceph-client/tools/testing/rbtree/test.h

Purpose: declares rbtree userspace test-suite entry points.

Important APIs/types/functions: `rbtree_tests()` and `interval_tree_tests()`.

Control flow: no direct flow; allows wrappers or aggregate runners to call either suite.

State and persistence: none.

Dependencies/integration: coordinates the rbtree and interval-tree wrapper C files.

Risks and test signals: only risk is declaration drift; compile/link failures expose mismatch.
