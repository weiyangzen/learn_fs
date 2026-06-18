# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 33624-36517

## Scope

This chunk covers lines 33624-36517 of `sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c`. The file is a userspace Maple Tree test harness that pulls in `../shared/maple-shim.c` and `../../../lib/test_maple_tree.c`, then drives internal Maple Tree APIs that are difficult to cover from normal kernel tests. This range starts near the end of the VM-captured erase/gap regression set and continues through RCU stress tests, DFS traversal checks, preallocation accounting, spanning-write regressions, no-memory behavior, tree duplication, and the final test entry points.

The range is not a standalone C translation unit. It depends on earlier definitions such as `RCU_RANGE_COUNT`, `RCU_MT_BUG_ON()`, `struct rcu_test_struct2`, `struct rcu_test_struct3`, `struct rcu_reader_struct`, `check_erase2_testset()`, and the VM test arrays `set18` through `set43`. It also calls Maple Tree helpers and assertions supplied by the included test shim and kernel test file.

## Purpose

The code in this chunk is regression-heavy validation for Maple Tree corner cases. It is intended to reproduce prior bugs in deletion, gap search, node rebalance, spanning stores, RCU-visible updates, allocation failure recovery, and structural duplication. The harness uses `MT_BUG_ON()`, `MAS_BUG_ON()`, `BUG_ON()`, validation walks, and targeted load checks so that any invariant violation aborts the test run.

The opening block finishes the 64-bit VM capture suite for `check_erase2_sets()`. Each test initializes a tree with `MT_FLAGS_ALLOC_RANGE`, loads one of the captured erase datasets, forces RCU callback drainage with `rcu_barrier()`, and checks historical failure points. The captured cases verify reverse empty-area search (`mas_empty_area_rev()`), `mas_prev()` behavior, gap metadata after deletes and NULL splits, parent pivot repairs after rebalance retries, preservation of entries around empty nodes, off-by-one gap calculations, and exact loads at specific high virtual-address-style indices.

The middle of the chunk stress-tests concurrent readers against writers in RCU mode. It creates forward and reverse readers that walk ranges with `mas_for_each()` or `mas_prev()`, while writer loops modify, toggle, delete, and add ranges. It also has a separate RCU harness where `mtree_load()` readers and `mas_for_each()` readers observe range updates made by `mtree_store_range()` and `mtree_store()`.

The tail contains targeted structural tests: DFS preorder traversal, preallocation node-count accounting, spanning writes across siblings/cousins/root levels, NULL range expansion coalescing, simulated allocation failures, lock/RCU-sensitive paths, deep tree duplication, erase rebalance shape construction, low-memory writer races, VMA-like expansion/shrink behavior, and final orchestration through `farmer_tests()`, `regression_tests()`, `maple_tree_tests()`, and `main()`.

## Important APIs, Types, and Functions

The VM regression tail uses:

- `check_erase2_testset(mt, setN, ARRAY_SIZE(setN))` to replay captured erase workloads.
- `mt_init_flags()`, `mtree_destroy()`, `mt_set_non_kernel()`, and `rcu_barrier()` to reset test trees and simulated allocation behavior between cases.
- `mas_empty_area_rev()`, `mas_find()`, `mas_prev()`, `mtree_load()`, `check_load()`, and `mt_validate()` as the observable checks for gap search, reverse iteration, and tree integrity.

The RCU stress helpers use:

- `rcu_reader_register()` and `rcu_reader_setup()` to register userspace RCU threads, synchronize start, and assign per-reader roles: modified slot, deleted slot, toggled slot, added slot, and next slot.
- `rcu_reader_fwd()` and `rcu_reader_rev()` as reader thread functions. Forward readers iterate with `mas_for_each()`, reverse readers walk with `mas_prev()`. Both allow expected values to change when a writer has modified, toggled, deleted, or added an entry.
- `rcu_stress_fwd()`, `rcu_stress_rev()`, and `rcu_stress()` to seed 1000 ranges, spawn two readers per ten entries, remove add-target entries before the run, enable RCU mode, perform 10,000 writer iterations, join readers, and validate the final tree.
- `struct rcu_test_struct` plus `eval_rcu_entry()`, `rcu_val()`, `rcu_loop()`, `run_check_rcu()`, `run_check_rcu_slot_store()`, `run_check_rcu_slowread()`, `check_rcu_simulated()`, and `check_rcu_threaded()` for a second RCU test family covering regular `mtree_load()` readers, advanced-API range readers, slow overlapping writes, and slot-store expansion.

The structural and allocation tests use:

- `mas_dfs_preorder()` and `check_dfs_preorder()` to traverse the internal node tree in preorder and assert expected node counts for sequential and reverse-sequential populations.
- `get_vacant_height()`, `mas_allocated()`, and `check_prealloc()` to verify `mas_preallocate()`, `mas_wr_preallocate()`, `mas_store_prealloc()`, `mas_pop_node()`, and `mas_destroy()` allocate and release exactly the expected number of nodes across spanning stores, splits, slot stores, failed `GFP_NOWAIT` paths, and chained preallocations.
- `check_spanning_write()` and `check_spanning_store_height()` to exercise stores or erases spanning multiple nodes and levels, including sibling/cousin rebalances, root-level rebalance, full-node endings, node-boundary NULL coalescing, and height collapse.
- `check_null_expand()` to verify writes of `NULL` adjacent to existing NULL areas coalesce without unexpected slot-count changes.
- `check_nomem()` and `check_nomem_writer_race()` to force allocation failures and verify `mas_nomem()` retry/reset behavior, leaked-node prevention, and preservation of a second writer's update.
- `compare_node()`, `compare_tree()`, `mas_subtree_max_range()`, `build_full_tree()`, and `check_mtree_dup()` to build deep/full trees, duplicate them, compare copied nodes while ignoring physical addresses, reject invalid dup inputs, and exercise duplication under deterministic allocation failures.
- `check_erase_rebalance()`, `check_collapsing_rebalance()`, `writer2()`, `check_vma_modification()`, `get_last_index()`, and `test_spanning_store_regression()` as focused regression reproductions for rebalance depth, collapse after right-to-left deletes, no-memory writer interleaving, VMA expansion/shrink sequences, and spanning stores that consume an entire right leaf.

## Control Flow

The VM regression tail is a straight-line sequence inside `check_erase2_sets()` guarded by 64-bit build conditions. Each case creates or resets a Maple Tree, replays one captured dataset, optionally performs one extra operation, checks a previously broken outcome, restores normal allocation simulation with `mt_set_non_kernel(0)`, validates where useful, and destroys the tree. Cases `set18` through `set43` cover reverse gap search, `mas_prev()` infinite-loop and slot bugs, `mas_may_move_gap()` state loss, NULL split/delete gaps, alignment after reverse area search, retry rebalance parent-pivot updates, empty-node gap movement, and off-by-one calculations.

The first RCU stress path starts in `rcu_stress()`. It seeds non-overlapping ranges based on `time(NULL)` and `rand()`, assigns each reader a ten-entry window, launches alternating forward and reverse reader threads, removes entries that will later be added, then marks the tree as RCU-managed. Depending on the `forward` parameter, writer mutations are applied in increasing or decreasing reader order. Readers treat several outcomes as valid only when they correspond to a known concurrent operation: a deleted entry can skip forward, an added entry can appear or be absent, a toggled entry can alternate between two values, and a modified entry can be either old or new.

The second RCU path starts from `check_rcu_threaded()`. It builds predictable ranges, configures a shared `struct rcu_test_struct`, and calls `run_check_rcu()` for concurrent `mtree_load()` and range-iteration readers while a range update is installed. It then repeats against an allocation-range tree, expands one middle slot under active readers in `run_check_rcu_slot_store()`, runs the randomized forward and reverse stress paths, and finishes with `run_check_rcu_slowread()` where writer updates are deliberately slowed so readers should observe both replacement values.

The structural test flow is orchestrated by `farmer_tests()`. It creates a local `DEFINE_MTREE(tree)`, repeatedly initializes it with the flags each test needs, invokes one focused checker, then destroys the tree. It also tests tree dumping for an empty tree, a value root, and a manually allocated leaf node, calls `test_kmem_cache_bulk()`, conditionally runs threaded RCU tests when not on 32-bit Maple mode, conditionally runs VM erase captures on 64-bit builds, and ends with no-memory checks.

`maple_tree_tests()` is the exported test runner for this file. Unless `BENCH` is defined, it runs `regression_tests()` and `farmer_tests()`, then always runs `maple_tree_seed()` and `maple_tree_harvest()`. The weak `main()` initializes Maple Tree support, runs the tests, drains RCU callbacks, reports nonzero `nr_allocated`, and returns success unless an assertion aborted earlier.

## State and Persistence Behavior

This code does not persist data outside the process. Its state is in-memory Maple Tree topology, Maple state cursors, simulated allocation counters, RCU callbacks, pthread reader state, and debug counters. Every test either uses a local `DEFINE_MTREE()` or receives a tree pointer that is repeatedly initialized and destroyed.

Tree state is mutated aggressively. Tests insert and erase ranges, overwrite values, split and coalesce NULL areas, create full trees, manually construct a leaf root, and intentionally leave readers looking at old nodes while writers update RCU-visible trees. `mt_set_in_rcu()` and `mt_clear_in_rcu()` switch the tree into RCU semantics, and `rcu_barrier()` is used between cases or at program end to flush deferred frees before leak checks.

Allocation state is part of the test surface. `mt_set_non_kernel()` simulates constrained allocation, `GFP_NOWAIT` paths are expected to fail, `mas_preallocate()` and `mas_destroy()` are checked for exact accounting via `mas_allocated()`, and `check_nomem()` relies on `nr_allocated` or sanitizer behavior to catch leaked nodes after retry races. `mt_set_private()` and `mt_set_callback()` are used to trigger a second writer during low-memory retry handling.

Thread state is transient but central to the RCU tests. Reader threads call `rcu_register_thread()`/`rcu_unregister_thread()`, synchronize with `test.start`, observe `test.stop`, increment atomic observation counters, and use a mutex to avoid multiple diagnostic dumps. Successful runs require not just absence of crashes, but proof that readers observed at least one expected update in selected paths.

## Dependencies and Integration Points

This chunk depends on the Maple Tree userspace shim and kernel test code included near the top of the file. Important external or earlier-file symbols include `maple_tree_init()`, `maple_tree_seed()`, `maple_tree_harvest()`, `mtree_*()` APIs, `mas_*()` APIs, `ma_*()` node helpers, `mt_dump()`, `mt_validate()`, `check_seq()`, `check_rev_seq()`, `mtree_test_store_range()`, `check_load()`, `test_kmem_cache_bulk()`, and the VM-captured `setN` arrays.

It integrates with userspace threading and userspace RCU facilities through `pthread_create()`, `pthread_join()`, `pthread_mutex_*()`, `rcu_register_thread()`, `rcu_unregister_thread()`, `rcu_read_lock()`, `rcu_read_unlock()`, and `uatomic_inc()`. Timing interleavings are induced with `usleep()`.

Build-time integration is conditional. Some VM capture tests and VMA-address tests run only under `CONFIG_64BIT`; RCU threaded tests are skipped for `MAPLE_32BIT`; and the main farmer/regression tests are skipped when `BENCH` is defined. The weak `main()` lets another test harness override the executable entry point while preserving standalone execution.

Repository-wise, this code lives under a Ceph client source snapshot but is Linux Maple Tree test infrastructure rather than CephFS runtime logic. It validates data-structure behavior used by kernel subsystems, including VMA-like range updates, allocation-range gap search, and RCU-safe lookups.

## Risks and Edge Cases

The highest test risk is nondeterministic RCU timing. The stress tests use sleeps, time-seeded random ranges, and concurrent readers; a real bug may be timing-sensitive, while an overly strict expectation can create sporadic failures. The code mitigates this by accepting both old and new values for known concurrent mutation windows and by checking observation counters only where updates should be seen.

The VM capture cases are brittle by design. They use specific large numeric indices, exact `mas.index`/`mas.last` expectations, and architecture guards. A legitimate Maple Tree layout change can require updating expectations even if external semantics remain correct. Conversely, removing these exact checks would weaken coverage for previously fixed regressions in reverse gap walking, parent pivot updates, and empty-node handling.

Allocation-failure paths are a major edge surface. `mas_nomem()` can drop and regain locks, so tests explicitly simulate a second writer changing the same region. Incorrect retry state can leak nodes, overwrite another writer's value, or leave `ma_state` in an error/status combination that later operations mishandle.

Spanning writes are another high-risk area. The chunk covers writes that cross leaf boundaries, parent boundaries, sibling and cousin rebalances, root-level collapse, full-node endings, NULL coalescing, and 32-bit vs 64-bit branching-factor differences. Bugs here tend to corrupt pivots, gaps, parent pointers, or height metadata rather than simply returning an error.

Tree duplication comparisons must ignore addresses while still catching structural differences. `compare_node()` masks parent and child-slot pointer bits before `memcmp()`, so failures can indicate copied metadata, pivots, gaps, or slot contents changed, not merely different allocation addresses. This is sensitive to encoded pointer/tag layout assumptions.

## Test Signals

High-signal pass conditions from this chunk include:

- All `set18` through `set43` erase/gap VM capture tests complete without `MT_BUG_ON()`, and the checked reverse-gap `mas.last`, aligned `mas.index`, `mtree_load()`, and `mas_prev()` results match the hard-coded expectations.
- `mt_validate()` succeeds after VM capture replays, RCU stress runs, spanning writes, duplication, and slot-store expansion.
- RCU threaded tests observe at least one replacement value in `run_check_rcu()`, both replacement values and a mixed observation in `run_check_rcu_slowread()`, and symmetric range growth in `rcu_slot_store_reader()`.
- `check_dfs_preorder()` counts the expected preorder visits for normal, allocation-range, and reverse-sequence trees, with architecture-specific expected counts.
- `check_prealloc()` sees exact allocation counts for spanning stores and splits, zero allocations for slot stores, expected failures under simulated `GFP_NOWAIT`, and zero remaining preallocated nodes after destroy or store-prealloc paths.
- `check_null_expand()` verifies that NULL writes merge adjacent NULL areas and, on 64-bit builds, reduce data-end counts as expected.
- `check_nomem()` returns `-ENOMEM` when allocation is forced to fail, then successfully retries without leaked nodes after another insert intervenes.
- `check_mtree_dup()` rejects incompatible inputs with `-EINVAL`, duplicates full and normal trees under both flag modes, compares original and duplicate trees successfully, and sees at least one deterministic `-ENOMEM` during simulated allocation failures.
- `test_spanning_store_regression()` can build a three-level tree, choose a sibling-spanning range, store across it, and pass `mt_validate()`.

## Cross-Chunk Notes

This is a chunk-level artifact only. It should be merged later into the final source-tree-aligned research document for `sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c` after all chunks for that source file are ready.

Adjacent earlier chunks are needed for the definitions of the VM datasets, core erase helpers, Maple Tree macros, and the beginning of `check_erase2_sets()`. This chunk starts in the middle of that function after the `set17` case and therefore cannot independently explain every captured dataset. No later chunk is needed for function closure after line 36517; this range reaches the file's weak `main()` entry point.
