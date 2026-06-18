# sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.h

Purpose: shared interface for radix-tree/XArray userspace tests.

Important APIs/types/functions: defines `struct item` with `rcu_head`, `index`, and `order`; declares item lifecycle/lookup/tag helpers, scan helpers, `tag_tagged_items()`, test-suite entry points (`xarray_tests()`, `tag_check()`, `multiorder_checks()`, `iteration_test()`, `benchmark()`, `idr_checks()`, `ida_tests()`), allocation counter, and normally-private radix-tree internals used for validation.

Control flow: no direct control flow; this is a contract header included by the test programs.

State and persistence: declares external `nr_allocated` and `radix_tree_preloads`; otherwise no state.

Dependencies/integration: includes Linux GFP/types/radix-tree/RCU headers. It is the main coupling point between standalone test files and the userspace kernel-library shims.

Risks and test signals: broad exposure of private radix-tree internals is intentional for tests but tightly couples the suite to implementation layout.
