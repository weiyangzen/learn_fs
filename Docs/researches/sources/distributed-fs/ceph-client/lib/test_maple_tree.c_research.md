# sources/distributed-fs/ceph-client/lib/test_maple_tree.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_maple_tree.c` is a comprehensive kernel module self-test for the maple tree API. It validates indexed and ranged storage, lookup, iteration, empty-area allocation, cyclic allocation, node splitting/rebalancing, state-machine transitions, fork-style tree duplication, RCU-aware traversal, and historical fuzzer regressions. The source was read as a complete 4026-line file for this report.

## Important APIs, Types, and Functions

The helper layer wraps public maple APIs through `mtree_insert_index`, `mtree_erase_index`, `mtree_test_insert`, `mtree_test_store_range`, `mtree_test_insert_range`, `mtree_test_load`, and `mtree_test_erase`. Assertion and accounting are through `MT_BUG_ON`, `maple_tree_tests_run`, and `maple_tree_tests_passed` when `CONFIG_DEBUG_MAPLE_TREE` is not enabled. Important test routines include `check_seq`, `check_rev_seq`, `check_find`, `check_find_2`, `check_rev_find`, `check_ranges`, `check_alloc_range`, `check_alloc_rev_range`, `check_store_null`, `check_root_expand`, `check_gap_combining`, `check_node_overwrite`, `check_forking`, `check_iteration`, `check_mas_store_gfp`, `next_prev_test`, `check_fuzzer`, `check_empty_area_window`, `check_empty_area_fill`, `check_state_handling`, and `alloc_cyclic_testing`. The main module entry is `maple_tree_seed`; exit is `maple_tree_harvest`.

## Control Flow

Loading the module calls `maple_tree_seed`, initializes the global `DEFINE_MTREE(tree)` under different flag combinations, runs a long ordered suite of checks, destroys/reinitializes the tree between scenarios, waits for pending RCU callbacks with `rcu_barrier`, prints pass/run counts, and returns `0` only if every `MT_BUG_ON` check passed. Optional benchmark blocks are compiled only when local `BENCH_*` macros are enabled; otherwise they are dead code. The normal suite first exercises basic storage and range operations, then allocation-range behavior on 64-bit builds, then iterator/search behavior, node rebalance cases, fuzzer-minimized regressions, empty area search, maple state transitions, and cyclic allocation.

## State and Persistence Behavior

The persistent module state is limited to the static maple tree object and test counters while the module is loaded. Test data entries are pointer values, `xa_mk_value()` encoded integers, `XA_ZERO_ENTRY`, and `NULL`. Most routines explicitly call `mtree_destroy()` and often reinitialize with `mt_init_flags()` to isolate cases. The file does not persist data outside memory; it does stress internal maple node allocation, RCU freeing, external lock mode through `struct rw_semaphore`, and allocation-range gap metadata.

## Dependencies and Integration Points

Direct dependencies are `<linux/maple_tree.h>`, `<linux/module.h>`, and `<linux/rwsem.h>`. It integrates with the xarray value encoding model through `xa_mk_value()` and `XA_ZERO_ENTRY`, maple state APIs such as `MA_STATE`, `mas_lock`, `mas_store_gfp`, `mas_find`, `mas_find_rev`, `mas_next`, `mas_prev`, `mas_empty_area`, `mas_empty_area_rev`, `mas_alloc_cyclic`, `mtree_alloc_range`, `mtree_alloc_rrange`, `mtree_alloc_cyclic`, and internal duplication/destruction helpers `__mt_dup` and `__mt_destroy`. Build-time behavior changes with `CONFIG_DEBUG_MAPLE_TREE`, `CONFIG_64BIT`, and slot geometry through `MAPLE_NODE_SLOTS`.

## Risks and Edge Cases

The test intentionally covers high-risk maple behavior: off-by-one range endpoints, `ULONG_MAX` and huge 64-bit ranges, empty tree versus single-entry root versus multi-node trees, RCU traversal state, external-lock duplication, gap merging after erase/store, forward and reverse empty-area windows, `ma_none`/`ma_overflow`/`ma_underflow` transitions, zero entries, NULL range stores, and wraparound in cyclic allocation. Since many checks use pointer-encoded constants, incorrect low-bit handling can look like valid entries. The suite is expensive and kernel-only; running it on production kernels could perturb memory pressure and logs.

## Test Signals

Primary signal is module load success and the log line reporting equal passed/run counts. Failures print function/line through `MT_BUG_ON` and cause `maple_tree_seed` to return `-EINVAL`. Strong coverage signals include clean runs on both 32-bit-shaped and 64-bit-shaped maple configurations, with and without `CONFIG_DEBUG_MAPLE_TREE`, and with RCU callbacks drained. Optional benchmark macros are performance probes, not normal correctness gates.
