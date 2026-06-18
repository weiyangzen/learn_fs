# sources/distributed-fs/ceph-client/tools/testing/radix-tree/multiorder.c

Purpose: userspace tests for multi-order XArray/radix-tree entries, covering iteration over sibling-covered ranges, marked iteration, RCU deletion races, and `xa_load()`/`xa_find()` behavior while multi-order entries are repeatedly created and removed.

Important APIs/types/functions: `item_insert_order()` wraps `XA_STATE_ORDER`, `xas_store()`, `xas_nomem()`, and `xas_error()` to allocate `struct item` entries with an order; `multiorder_iteration()` and `multiorder_tagged_iteration()` validate `xas_for_each()` and `xas_for_each_marked()` against fixed index/order tables; `creator_func()`, `iterator_func()`, `load_creator()`, and `load_worker()` are pthread race bodies; `multiorder_checks()` is the exported suite entry point; the weak `main()` makes the file standalone.

Control flow: deterministic tests insert fixed multi-order entries, sweep starting indexes 0..255, and assert that iterator indexes, node shifts, item indexes, and marks match the covered ranges. Race tests create one writer and many readers based on CPU count: one inserts/deletes order `RADIX_TREE_MAP_SHIFT - 1` entries with RCU freeing while readers iterate and call `xas_retry()`, then another writer cycles marked sibling entries near chunk boundaries while readers exercise `xa_load()` and marked `xa_find()`.

State and persistence: all state is in an in-memory static `DEFINE_XARRAY(array)` and global `stop_iteration`; entries are heap allocated through `item_create()` and released through `item_kill_tree()` or `item_delete_rcu()`. No persistent files are touched.

Dependencies/integration: depends on the radix-tree userspace harness in `test.h`, pthreads, RCU registration, XArray internals, and `radix_tree_cpu_dead(0)` cleanup. It integrates into the broader radix-tree test runner through `multiorder_checks()`.

Risks and test signals: assertions catch wrong sibling expansion, stale internal-node exposure, mark propagation errors, and RCU iterator/load races. The races are timing-sensitive and CPU-count-dependent; `stop_iteration` is an unsynchronized boolean, acceptable for stress testing but not a portable synchronization primitive.
