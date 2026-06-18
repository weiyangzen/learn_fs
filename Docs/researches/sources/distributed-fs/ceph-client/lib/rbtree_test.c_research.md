## sources/distributed-fs/ceph-client/lib/rbtree_test.c

Purpose: kernel module self-test and microbenchmark for regular, cached, and augmented rbtrees.

Important APIs/types: module parameters `nnodes`, `perf_loops`, `check_loops`, and `seed` control size and randomness. `struct test_node` embeds `struct rb_node` plus key/value/augmented fields. Functions cover insertion/erasure variants, invariant checking, postorder checking, augmented callback validation, and timing.

Control flow: module init allocates test nodes, seeds `rnd`, runs `basic_check()` and `augmented_check()`, frees nodes, then returns `-EAGAIN` so the test module unloads immediately. Basic testing measures insert/delete, cached insert/delete, inorder traversal, first-node fetch, then repeatedly inserts and erases while checking invariants at each step. Augmented testing repeats with `RB_DECLARE_CALLBACKS_MAX` and verifies each node's augmented maximum equals its subtree maximum.

State and persistence: static globals hold the cached root, node array, and pseudo-random state during the test only. No state persists after module unload.

Dependencies/integration: depends on module infrastructure, `rbtree_augmented.h`, `prandom`, slab allocation, and cycle counters.

Risks/test signals: duplicate keys are allowed on the right side, so checks validate nondecreasing order rather than strict uniqueness. The test warns with `WARN_ON_ONCE()` on invariant violations and logs timing, making it a direct signal for rbtree regressions.
