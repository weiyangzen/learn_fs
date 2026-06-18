# subset-b-006110 Research

Grouped source research for Ceph-client kernel `lib/test_*.c` modules. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_maple_tree.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_maple_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_memcat_p.c -->
# sources/distributed-fs/ceph-client/lib/test_memcat_p.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_memcat_p.c` is a small module self-test for `memcat_p()`, the helper that concatenates two NULL-terminated arrays of pointers. The source was read as a complete 116-line file.

## Important APIs, Types, and Functions

The file defines `struct test_struct` with `num` and `magic`, constants `MAGIC`, `INPUT_MAX`, and `EXPECT`, and the module entry `test_memcat_p_init`. It uses `kzalloc_objs`, `kmalloc_obj`, `memcat_p`, `kfree`, `pr_err`, and `pr_info`. `test_memcat_p_exit` is intentionally empty.

## Control Flow

On module load, the test allocates two pointer arrays, fills `INPUT_MAX - 1` objects in each, assigns paired pseudo-random positive and negative `num` values plus a magic marker, terminates both input arrays with `NULL`, then calls `memcat_p(in0, in1)`. It walks the output until NULL or the maximum expected length, checks that every pointed-to object still has the magic value, checks that summed positive and negative values cancel to zero, verifies `EXPECT` output elements, and verifies order: all `in0` elements followed by all `in1` elements. All allocations are unwound through labeled error paths.

## State and Persistence Behavior

All state is heap memory allocated during module initialization and freed before init returns. The output array owns only the pointer list returned by `memcat_p`; the pointed objects remain the input allocations and are freed separately. No state remains after load succeeds or fails.

## Dependencies and Integration Points

Direct includes are `<linux/string.h>`, `<linux/slab.h>`, and `<linux/module.h>`. The integration point is `lib/memcat_p.c` behavior and the kernel slab allocation helpers. The module is only useful when explicitly loaded or built as a test module.

## Risks and Edge Cases

The test checks ordering and termination but uses a fixed 128-entry input size. Its cleanup path depends on `i` reflecting the highest successfully allocated index; a regression in partial allocation handling would risk leaks or double frees. It does not test empty inputs, one empty input, or very large pointer arrays.

## Test Signals

Passing output is `test passed` and an init return of `0`. Failures return `-ENOMEM` or `-EINVAL` and emit a specific size, order, total, or magic mismatch message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_memcat_p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_meminit.c -->
# sources/distributed-fs/ceph-client/lib/test_meminit.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_meminit.c` validates allocator initialization and cleanup behavior for page allocator, `kmalloc`, `vmalloc`, `kmem_cache`, bulk slab allocation, and `SLAB_TYPESAFE_BY_RCU` caches. It is aimed at detecting stale data exposure after allocation/free cycles. The source was read as a complete 440-line file.

## Important APIs, Types, and Functions

Core helpers are `count_nonzero_bytes`, `fill_with_garbage_skip`, `fill_with_garbage`, `do_alloc_pages_order`, `test_pages`, `do_kmalloc_size`, `do_vmalloc_size`, `test_kvmalloc`, `test_ctor`, `check_buf`, `do_kmem_cache_size`, `do_kmem_cache_rcu_persistent`, `do_kmem_cache_size_bulk`, `test_kmemcache`, `test_rcu_persistent`, and `test_meminit_init`. Constants include `GARBAGE_INT`, `GARBAGE_BYTE`, `CTOR_BYTES`, `CTOR_PATTERN`, and `BULK_SIZE`.

## Control Flow

`test_meminit_init` runs four groups: page allocations for every `NR_PAGE_ORDERS` order, `kmalloc`/`vmalloc` sizes from `1` through `1 << 19`, slab cache combinations across size, constructor, RCU, and `__GFP_ZERO`, and RCU persistence checks. Each test usually allocates, fills freed memory with garbage, frees it, reallocates, and counts whether bytes are zero when zeroing is expected. Slab tests also exercise `kmem_cache_alloc_bulk` and `kmem_cache_free_bulk`. RCU cache tests compare freed object contents under `rcu_read_lock()` and reallocation behavior.

## State and Persistence Behavior

The module has no persistent state beyond static `bulk_array`. It creates temporary slab caches named `test_cache`, temporary heap buffers, page allocations, and vmalloc mappings, then frees/destroys them in each helper. The tests intentionally write recognizable garbage patterns to memory before freeing so subsequent allocation behavior can be checked.

## Dependencies and Integration Points

Direct includes cover init, kernel, mm, module, slab, string, and vmalloc headers. Integration points are page allocator initialization policy, slab cache constructors, `SLAB_TYPESAFE_BY_RCU`, `__GFP_ZERO`, bulk slab operations, `kmalloc`, `vmalloc`, `rcu_read_lock`, and allocator debug/hardening options that control memory initialization on alloc/free.

## Risks and Edge Cases

This test is sensitive to kernel configuration: if allocator zero-on-alloc/free policy is disabled or differs by cache type, failures may indicate configuration mismatch rather than a code bug. Large orders may fail due to memory pressure and are counted as failures. Constructor and `__GFP_ZERO` combinations are intentionally skipped when incompatible. RCU-type-safe cache behavior differs from normal cache zeroing and is handled specially.

## Test Signals

Each test group logs either all tests passed or failures out of total. Module init returns `0` only when the aggregate failure count is zero; otherwise it logs the failure count and returns `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_meminit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_module.c -->
# sources/distributed-fs/ceph-client/lib/test_module.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_module.c` is a minimal module-loading smoke test. It exists to validate that the kernel can load, initialize, and unload a module, including module signing or verification paths. The source was read as a complete 35-line file.

## Important APIs, Types, and Functions

The module defines `test_module_init` and `test_module_exit`, wired through `module_init` and `module_exit`. It uses `pr_warn` and standard module metadata macros.

## Control Flow

On load, `test_module_init` logs `Hello, world` and returns success. On unload, `test_module_exit` logs `Goodbye`. There are no branches or external resources.

## State and Persistence Behavior

The file owns no runtime state and performs no allocation or persistence. Its only observable behavior is kernel log output and module lifecycle registration.

## Dependencies and Integration Points

Direct includes are `<linux/init.h>`, `<linux/module.h>`, and `<linux/printk.h>`. It integrates with the kernel module loader and is useful for basic module infrastructure validation.

## Risks and Edge Cases

Risk is intentionally low. Because it always loads successfully, it validates only the module framework path, not subsystem behavior. It can still fail externally if module loading, signing, lockdown, or symbol policy rejects it.

## Test Signals

Expected signals are successful insertion/removal and the two warning log lines. Any load failure points to module infrastructure, policy, or build/signing issues rather than this file's logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_objagg.c -->
# sources/distributed-fs/ceph-client/lib/test_objagg.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_objagg.c` tests the object aggregation library. It verifies root-only aggregation, delta aggregation, reference counting, statistics reporting, and hints generation/consumption. The source was read as a complete 1036-line file.

## Important APIs, Types, and Functions

Local model types are `struct tokey`, `struct world`, `struct root`, `struct delta`, `struct expect_stats_info`, `struct expect_stats`, `struct action_item`, and `struct hints_case`. Important callbacks are `delta_check`, `delta_create`, `delta_destroy`, `root_create`, and `root_destroy`, grouped into `nodelta_ops` and `delta_ops`. Test helpers include `world_obj_get`, `world_obj_put`, `test_nodelta_obj_get`, `test_nodelta_obj_put`, `check_stats_zero`, `check_stats_nodelta`, `check_expect`, `obj_to_key_id`, `check_expect_stats`, `test_delta_action_item`, `test_delta`, `test_hints_case`, and `test_hints`. Module entry is `test_objagg_init`.

## Control Flow

Module load runs `test_nodelta`, `test_delta`, then `test_hints`. `test_nodelta` creates an `objagg` with dummy delta support, gets each of 32 keys twice, verifies roots are created only on first acquisition, validates stats, releases references in reverse order, and confirms stats return to zero. `test_delta` replays a fixed table of `ACTION_GET` and `ACTION_PUT` operations with expected root/delta count changes and expected stats after each action. `test_hints` builds an initial aggregation, asks for simple-greedy hints, creates a second aggregation with those hints, and verifies the expected hinted layout.

## State and Persistence Behavior

State is local to each test's `struct world`: root count, delta count, object references by key, and the expected root buffer. `objagg` objects, roots, deltas, stats snapshots, and hints are allocated and released during test execution. There is no file or cross-load persistence.

## Dependencies and Integration Points

Direct includes are `<linux/kernel.h>`, `<linux/module.h>`, `<linux/slab.h>`, `<linux/random.h>`, and `<linux/objagg.h>`. Integration points are `objagg_create`, `objagg_destroy`, `objagg_obj_get`, `objagg_obj_put`, `objagg_obj_root_priv`, `objagg_obj_delta_priv`, `objagg_stats_get`, `objagg_stats_put`, `objagg_hints_get`, `objagg_hints_put`, and `objagg_hints_stats_get`.

## Risks and Edge Cases

The test is strong on deterministic root/delta topology and stats, but it assumes `NUM_KEYS` 32 and a fixed delta rule of nonnegative key distance up to 5. Error cleanup in the hints path calls `world_obj_put(&world2, objagg, ...)` while tearing down objects created from `objagg2`, which is suspicious and would be worth auditing if that error path becomes reachable. Stats order can vary for items with the same counters, so the checker allows neighbor substitution.

## Test Signals

Init returns `0` only if all three test groups succeed. Failures emit key-specific root, delta, stats, or allocation messages and return an errno such as `-EINVAL`, `-ENOMEM`, or an `objagg` error pointer value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_objagg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_objpool.c -->
# sources/distributed-fs/ceph-client/lib/test_objpool.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_objpool.c` is a stress and performance test module for the lockless object pool API. It runs synchronous and asynchronous per-CPU pool scenarios with normal thread users and optional hrtimer users. The source was read as a complete 681-line file.

## Important APIs, Types, and Functions

Key structures are `struct ot_mem_stat`, `struct ot_obj_stat`, `struct ot_data`, `struct ot_test`, `struct ot_item`, `struct ot_node`, and `struct ot_context`. Important routines include `ot_init_data`, `ot_init_node`, `ot_hrtimer_handler`, `ot_init_cpu_item`, `ot_thread_worker`, `ot_perf_report`, `ot_init_sync_m0`, `ot_fini_sync`, `ot_bulk_sync`, `ot_start_sync`, `ot_fini_async_rcu`, `ot_fini_async`, `ot_objpool_release`, `ot_init_async_m0`, `ot_nod_recycle`, `ot_bulk_async`, `ot_start_async`, and `ot_mod_init`. Test scenarios are in `g_testcases`.

## Control Flow

On load, `ot_mod_init` iterates predefined scenarios. Each scenario initializes per-test control state, creates an object pool sized at `num_possible_cpus() << 3`, starts one worker per online CPU, releases them from an rwsem start gate, lets them run for the configured duration, sets a stop flag, waits for completion, finalizes the pool, and reports per-CPU hit/miss counts plus memory accounting. Synchronous tests recycle objects with `objpool_push`; asynchronous tests use `objpool_drop` under stop conditions and an RCU callback to finalize pool lifetime.

## State and Persistence Behavior

State lives in the global per-CPU `ot_pcup_items` and in `g_testcases` result fields during module load. Pool contexts and backing allocations are created per scenario and released. Memory counters track `kmalloc` allocations and frees for leak reporting. The module deliberately returns `-EAGAIN` after printing summaries so it does not remain loaded.

## Dependencies and Integration Points

Direct dependencies include module parameters, completions, kthreads, slab/vmalloc, delay, hrtimer, and `<linux/objpool.h>`. Integration points are `objpool_init`, `objpool_fini`, `objpool_pop`, `objpool_push`, `objpool_drop`, per-CPU workers, high-resolution timers, RCU callbacks, and atomic release/acquire stop signaling.

## Risks and Edge Cases

The module is stress-oriented and can consume CPU for one second per scenario across all online CPUs. It mixes thread and hrtimer contexts, so lockless pool correctness under interrupt-like timing is central. Async teardown is subtle: stop visibility, RCU callback ordering, and pool ref drops must align or use-after-free/leak issues can appear. Error returns from individual scenario starts are not propagated by `ot_mod_init`, which always finishes with `-EAGAIN`.

## Test Signals

Useful signals are per-case hit/miss summaries, memory allocation summaries with zero deltas, absence of WARNs, and successful completion of all scenarios. The expected final module init return is `-EAGAIN`, used to unload after benchmark completion rather than to indicate failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_objpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_parman.c -->
# sources/distributed-fs/ceph-client/lib/test_parman.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_parman.c` tests the priority array manager (`parman`) using the `PARMAN_ALGO_TYPE_LSORT` algorithm. It randomly adds and removes items across many priorities, then checks array ordering, indexing, gap policy, and resize behavior. The source was read as a complete 395-line file.

## Important APIs, Types, and Functions

Local types are `struct test_parman_prio`, `struct test_parman_item`, and `struct test_parman`. The operation callbacks are `test_parman_resize` and `test_parman_move`, exposed through `test_parman_lsort_ops`. Flow helpers include `test_parman_rnd_init`, `test_parman_priority_gen`, `test_parman_prios_init`, `test_parman_items_init`, `test_parman_create`, `test_parman_destroy`, `test_parman_run_check_budgets`, `test_parman_run`, `test_parman_check_array`, `test_parman_lsort`, and `test_parman_init`.

## Control Flow

Module load calls `test_parman_lsort`, which creates a `parman` instance with a backing pointer array, seeds a deterministic pseudo-random generator, initializes 128 unique priorities, assigns 8192 items to random priorities, and then runs up to `TEST_PARMAN_RUN_BUDGET` add/remove attempts. Random bulk budgets create no-op stretches and operation bursts. After the run, `test_parman_check_array` scans the backing array to ensure no forbidden gaps, monotonically increasing priorities, correct `parman_item.index` values, matching used-item counts, and reasonable trailing unused capacity.

## State and Persistence Behavior

All state is allocated in one `struct test_parman` and freed in `test_parman_destroy`. The backing priority array is resized with `krealloc` through parman callbacks and zeroed for new capacity. Priorities and items are in fixed arrays inside the test object; no state persists after module load.

## Dependencies and Integration Points

Direct includes cover kernel, module, slab, bitops, err, prandom, and `<linux/parman.h>`. Integration points are `parman_create`, `parman_destroy`, `parman_prio_init`, `parman_prio_fini`, `parman_item_add`, `parman_item_remove`, callback-driven resize/move semantics, and deterministic `prandom` state.

## Risks and Edge Cases

The test exercises resizing and item movement heavily, but only covers the lsort algorithm. It depends on deterministic randomness, so accidental seed changes alter coverage. `test_parman_resize` calls `krealloc` before checking `new_count == 0`; this matches kernel `krealloc(ptr, 0, ...)` semantics but is an area where allocator semantics matter. Memory pressure can fail creation or insertion and becomes a test failure.

## Test Signals

Success logs `Priority array check successful` and module init returns `0`. Failures identify gaps, bad priority order, bad index values, used count mismatches, too much trailing slack, or allocation/add errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_parman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ref_tracker.c -->
# sources/distributed-fs/ceph-client/lib/test_ref_tracker.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_ref_tracker.c` is a targeted self-test for the reference tracker infrastructure. It intentionally leaves references outstanding and attempts a double free to exercise diagnostic reporting. The source was read as a complete 116-line file.

## Important APIs, Types, and Functions

The file owns static `struct ref_tracker_dir ref_dir`, `tracker[20]`, a timer, and `test_ref_timer_done`. Macro `TRT_ALLOC` generates 19 noinline allocation wrapper functions so stack traces are distinct. Important routines are `alloctest_ref_tracker_free`, `test_ref_tracker_timer_func`, `test_ref_tracker_init`, and `test_ref_tracker_exit`.

## Control Flow

On load, the module initializes a tracker directory, starts a timer that allocates `tracker[0]` with `GFP_ATOMIC`, allocates `tracker[1]` through `tracker[19]` with distinct wrappers, frees trackers 2 through 19, attempts to free tracker 2 again, waits until the timer allocation completes, then exits the tracker directory while tracker 0 and tracker 1 remain allocated. This is expected to trigger ref-tracker warnings.

## State and Persistence Behavior

All tracker state is module-static and exists only during initialization. The test deliberately does not cleanly free all refs before `ref_tracker_dir_exit` because leak reporting is the behavior under test. The timer uses an atomic flag to synchronize completion with init.

## Dependencies and Integration Points

Direct includes are init, module, delay, ref_tracker, slab, and timer headers. Integration points are `ref_tracker_dir_init`, `ref_tracker_alloc`, `ref_tracker_free`, `ref_tracker_dir_exit`, timer callback context, `GFP_KERNEL`, and `GFP_ATOMIC`.

## Risks and Edge Cases

This module is designed to produce warnings, so a noisy load is expected. It depends on timer execution and uses polling with `msleep(1)`. Because it intentionally leaks tracked references into `ref_tracker_dir_exit`, it should not be treated like a normal pass/fail leak-free test.

## Test Signals

Expected signals are diagnostic warnings for the double free and for unfreed tracker 0 and 1. Module init returns `0`; the pass condition is that ref-tracker diagnostics appear and the module does not crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ref_tracker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_rhashtable.c -->
# sources/distributed-fs/ceph-client/lib/test_rhashtable.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_rhashtable.c` is a self-test and stress test for resizable hash tables and rhlist tables. It validates insertion, lookup, deletion, max-size enforcement, duplicate-list insertion, concurrent access, and random add/delete rhlist behavior. The source was read as a complete 815-line file.

## Important APIs, Types, and Functions

Module parameters include `parm_entries`, `runs`, `max_size`, `shrinking`, `size`, `tcount`, and `enomem_retry`. Types are `struct test_obj_val`, `struct test_obj`, `struct test_obj_rhl`, and `struct thread_data`. Key functions include `my_hashfn`, `my_cmpfn`, `insert_retry`, `test_rht_lookup`, `test_bucket_stats`, `test_rhashtable`, `test_rhltable`, `test_rhashtable_max`, `print_ht`, `test_insert_dup`, `test_insert_duplicates_run`, `thread_lookup_test`, `threadfunc`, and `test_rht_init`.

## Control Flow

On load, `test_rht_init` clamps entry count, configures `test_rht_params`, allocates object arrays, then runs the basic rhashtable insertion/lookup/deletion test `runs` times. It separately checks that exceeding `max_size` fails with `-E2BIG`, tests duplicate rhlist insertion through fast and slow paths, and if `tcount` is nonzero, starts synchronized worker threads. Each worker inserts per-thread keys, validates lookups, removes entries in decreasing stride patterns, and revalidates after each phase. Finally it runs a smaller rhltable add/delete and random operation test.

## State and Persistence Behavior

The global `ht` and `rhlt` tables are initialized and destroyed per test phase. Object arrays are `vzalloc`ed and freed. Worker synchronization uses `startup_count` and `startup_wait`. There is no persistent state after module initialization completes.

## Dependencies and Integration Points

Direct dependencies include jhash, kthreads, RCU, rhashtable/rhltable, random, vmalloc, wait queues, and slab. Integration points are `rhashtable_init`, `rhashtable_insert_fast`, `rhashtable_insert_slow`, `rhashtable_lookup_fast`, `rhashtable_remove_fast`, `rhashtable_walk_*`, `rhashtable_destroy`, `rhltable_init`, `rhltable_insert`, `rhltable_lookup`, `rhltable_remove`, `rhltable_destroy`, `rhl_for_each_entry_rcu`, and RCU read-side traversal.

## Risks and Edge Cases

Large defaults can be expensive; comments note `rhltable_remove` can otherwise take minutes, so the rhltable phase uses `entries / 16`. Memory pressure can produce `-ENOMEM`; optional `enomem_retry` converts those into retry loops. The test stresses resize races and duplicate keys, but several warnings do not always propagate into a final failure code, so logs matter. Thread names contain a typo (`rhashtable_thrad`) but behavior is unaffected.

## Test Signals

Signals include per-run duration, traversal count matching `nelems` and expected entries, successful max-size rejection, duplicate insertion count matching, no worker thread errors, and final rhltable return `0`. Init returns `-EINVAL` for core basic-test failures, but some later WARN-based diagnostics require log inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_rhashtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_static_key_base.c -->
# sources/distributed-fs/ceph-client/lib/test_static_key_base.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_static_key_base.c` is a support module for static key testing. It exports old-style and new-style static keys in known initial and inverted states so another module can verify external static branch behavior. The source was read as a complete 61-line file.

## Important APIs, Types, and Functions

The file defines and exports `base_old_true_key`, `base_inv_old_true_key`, `base_old_false_key`, `base_inv_old_false_key`, `base_true_key`, `base_inv_true_key`, `base_false_key`, and `base_inv_false_key`. It uses `STATIC_KEY_INIT_TRUE`, `STATIC_KEY_INIT_FALSE`, `DEFINE_STATIC_KEY_TRUE`, `DEFINE_STATIC_KEY_FALSE`, `EXPORT_SYMBOL_GPL`, `static_key_enabled`, `static_key_disable`, and `static_key_enable`. Functions are `invert_key`, `test_static_key_base_init`, and `test_static_key_base_exit`.

## Control Flow

On load, `test_static_key_base_init` flips the four `base_inv_*` keys from their declared state. The normal `base_*` keys remain in their initial state. Exit does nothing.

## State and Persistence Behavior

The static keys are global exported module state while the module is loaded. They are modified once at initialization and then serve as external test fixtures. No file persistence exists.

## Dependencies and Integration Points

Direct includes are `<linux/module.h>` and `<linux/jump_label.h>`. Integration is with the jump-label/static-key subsystem and with `test_static_keys.c`, which declares these symbols as `extern`.

## Risks and Edge Cases

This module must be loaded before the consumer test module resolves the exported symbols. Static key enable/disable operations patch branch sites and must be used in contexts allowed by the jump-label subsystem. The support module does not restore inverted keys on exit, relying on module unload cleanup.

## Test Signals

The module itself returns `0` if loaded. Its real signal is that `test_static_keys.c` can link against the exported symbols and observe expected initial/inverted states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_static_key_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_static_keys.c -->
# sources/distributed-fs/ceph-client/lib/test_static_keys.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_static_keys.c` verifies old and new static key APIs, including internal keys and external keys exported by `test_static_key_base.c`. It checks that static key enabled state matches branch macro results before and after toggling. The source was read as a complete 240-line file.

## Important APIs, Types, and Functions

Local keys are `old_true_key`, `old_false_key`, `true_key`, and `false_key`. External keys are the eight `base_*` symbols from the base module. `struct test_key` binds an expected initial state, `struct static_key *`, and a function pointer that evaluates a branch. `test_key_func` generates branch-testing functions for `static_key_true`, `static_key_false`, `static_branch_likely`, and `static_branch_unlikely`. Helpers are `invert_key`, `invert_keys`, `verify_keys`, and `test_static_key_init`.

## Control Flow

On load, `test_static_key_init` builds a table covering internal old/new keys and external old/new keys, including both likely and unlikely branch forms for new-style keys. It first verifies all keys match expected initial states, then toggles each unique key once with `invert_keys` and verifies every state and branch result is inverted, then toggles back and verifies the original state again. It returns the first `-EINVAL` failure or `0`.

## State and Persistence Behavior

Internal static keys are module globals. External static keys are owned by `test_static_key_base`. The test temporarily mutates all unique keys twice and is intended to leave them in their initial expected states when successful. There is no storage persistence.

## Dependencies and Integration Points

Direct includes are `<linux/module.h>` and `<linux/jump_label.h>`. Integration points include static key old APIs, static branch likely/unlikely APIs, generated jump-label patching, and exported symbols from `test_static_key_base.c`.

## Risks and Edge Cases

The test depends on the base module being present and initialized so inverted external keys have the expected states. `invert_keys` assumes duplicate key entries are adjacent, which is true for the local table and avoids toggling likely/unlikely variants twice. A reordered table could break that assumption. Static branch behavior can be architecture-sensitive because jump labels patch code.

## Test Signals

Successful module load returns `0`. Failures return `-EINVAL` from `verify_keys` when either `static_key_enabled()` or the generated branch predicate disagrees with the expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_static_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_sysctl.c -->
# sources/distributed-fs/ceph-client/lib/test_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_sysctl.c` is a proc sysctl test driver. It creates a set of `/proc/sys/debug/test_sysctl/` entries for integer, unsigned integer, string, bitmap, boot-time bounded integer, mount-point, empty-directory, unregister, and u8 min/max validation tests. The source was read as a complete 335-line file.

## Important APIs, Types, and Functions

State includes `i_zero`, `i_one_hundred`, `match_int_ok`, `ctl_headers`, and `struct test_sysctl_data test_data`. Sysctl tables are `test_table`, `test_table_unregister`, `test_table_empty`, `table_u8_over`, `table_u8_under`, and `table_u8_valid`. Important routines are `test_sysctl_calc_match_int_ok`, `test_sysctl_setup_node_tests`, `test_sysctl_run_unregister_nested`, `test_sysctl_run_register_mount_point`, `test_sysctl_run_register_empty`, `test_sysctl_register_u8_extra`, `test_sysctl_init`, and `test_sysctl_exit`.

## Control Flow

On load, `test_sysctl_init` runs setup functions in order until one fails. It checks predefined `SYSCTL_*` integer constants, allocates a large bitmap, registers the main debug/test_sysctl table, registers and unregisters a nested table to test directory removal, registers a sysctl mount point and tries to register under it, creates empty directories, and verifies invalid u8 extra bounds are rejected while valid bounds are accepted. On unload, it frees the bitmap and unregisters all stored table headers.

## State and Persistence Behavior

The module persists registered proc sysctl entries and a bitmap allocation while loaded. Values in `test_data` are mutable through proc handlers according to their modes. All registered headers are tracked in `ctl_headers` for cleanup. No state persists after unload.

## Dependencies and Integration Points

Direct includes include list, module, printk, fs, miscdevice, slab, uaccess, async, delay, and vmalloc headers. Integration points are `register_sysctl`, `register_sysctl_mount_point`, `unregister_sysctl_table`, `proc_dointvec_minmax`, `proc_dointvec`, `proc_douintvec`, `proc_dostring`, `proc_do_large_bitmap`, `proc_dou8vec_minmax`, and predefined `SYSCTL_*` extra bound pointers.

## Risks and Edge Cases

The driver requires `CONFIG_PROC_SYSCTL` and a writable proc sysctl environment. The u8-bound checks intentionally expect invalid registrations to fail; if they succeed the test returns an error-like `-ENOMEM` value. The mount-point negative case deliberately does not fail init if registration under the mount point fails as expected. Cleanup order unregisters any stored header regardless of partial init.

## Test Signals

Module load success means all required registrations and validation checks passed. Userspace or kselftest scripts can then read/write the debug sysctls. Unload should remove the proc tree and free `bitmap_0001` without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ubsan.c -->
# sources/distributed-fs/ceph-client/lib/test_ubsan.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_ubsan.c` deliberately triggers undefined-behavior sanitizer checks in kernel context. It covers integer overflows, truncation, invalid shifts, out-of-bounds array access, invalid bool/enum values, and misaligned access. The source was read as a complete 174-line file.

## Important APIs, Types, and Functions

The file defines `test_ubsan_fp`, macro `UBSAN_TEST`, individual trigger functions `test_ubsan_add_overflow`, `test_ubsan_sub_overflow`, `test_ubsan_mul_overflow`, `test_ubsan_negate_overflow`, `test_ubsan_divrem_overflow`, `test_ubsan_truncate_signed`, `test_ubsan_shift_out_of_bounds`, `test_ubsan_out_of_bounds`, `test_ubsan_load_invalid_value`, and `test_ubsan_misaligned_access`, plus arrays `test_ubsan_array` and `skip_ubsan_array`.

## Control Flow

On module load, `test_ubsan_init` iterates `test_ubsan_array` and calls each trigger. Every trigger logs which UBSAN config controls detection and then performs the undefined operation using `volatile` values or `OPTIMIZER_HIDE_VAR` to avoid compile-time elimination. Division by zero is placed in `skip_ubsan_array` because it can oops the module.

## State and Persistence Behavior

The module owns no persistent state. All variables are local to trigger functions. Its primary output is sanitizer diagnostics and kernel log messages.

## Dependencies and Integration Points

Direct includes are init, kernel, and module headers. Integration points are UBSAN instrumentation controlled by `CONFIG_UBSAN_INTEGER_WRAP`, `CONFIG_UBSAN_DIV_ZERO`, `CONFIG_UBSAN_SHIFT`, `CONFIG_UBSAN_BOUNDS`, `CONFIG_UBSAN_BOOL`, `CONFIG_UBSAN_ENUM`, and `CONFIG_UBSAN_ALIGNMENT`.

## Risks and Edge Cases

This module intentionally executes undefined behavior; it should be used only in controlled test kernels. Some cases depend on compiler instrumentation and architecture alignment behavior. The skipped divide-by-zero case documents a known oops risk. Optimizer changes may affect whether a trigger is preserved unless guarded by volatile or optimizer hiding.

## Test Signals

Expected signals are `pr_info` lines naming each UBSAN config and matching UBSAN reports when the relevant config is enabled. Module init returns `0`; absence of a report for a disabled config is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_ubsan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_vmalloc.c -->
# sources/distributed-fs/ceph-client/lib/test_vmalloc.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_vmalloc.c` is a concurrent stress and performance test module for `vmalloc`, aligned vmalloc, per-cpu allocation, `kvfree_rcu`, `vm_map_ram`, huge vmalloc, and nonblocking vmalloc paths. The source was read as a complete 644-line file.

## Important APIs, Types, and Functions

Module parameters are generated by `__param`: `nr_threads`, `sequential_test_order`, `test_repeat_count`, `test_loop_count`, `nr_pages`, `use_huge`, `run_test_mask`, and `nr_pcpu_objects`. Test functions include `random_size_align_alloc_test`, `align_shift_alloc_test`, `fix_align_alloc_test`, `random_size_alloc_test`, `long_busy_list_alloc_test`, `full_fit_alloc_test`, `fix_size_alloc_test`, `no_block_alloc_test`, `pcpu_alloc_test`, `kvfree_rcu_1_arg_vmalloc_test`, `kvfree_rcu_2_arg_vmalloc_test`, and `vm_map_ram_test`. Driver structures are `struct test_case_desc`, `struct test_case_data`, and `struct test_driver`.

## Control Flow

`vmalloc_test_init` calls `do_concurrent_test`. Configuration clamps thread and loop counts, allocates one `test_driver` per thread, blocks workers during setup with SRCU, starts kthreads, releases the SRCU gate, waits for all workers to report completion, stops the kthreads, prints per-worker summaries for each enabled test case, and frees the driver array. Each worker optionally shuffles test order, applies `run_test_mask`, repeats selected tests, records pass/fail/xfail counts, and averages elapsed time.

## State and Persistence Behavior

Global state includes `prepare_for_test_srcu`, completion `test_all_done_comp`, atomic `test_n_undone`, and the heap/vmalloc-backed `tdriver` array while running. Test allocations are created and freed inside each test loop. The module returns `-EAGAIN` when built as a module so it unloads after the run; built-in mode uses `late_initcall` and returns `0`.

## Dependencies and Integration Points

Direct includes cover vmalloc, random, kthread, module parameters, completion, delay, mm, RCU, SRCU, and slab. Integration points are `vmalloc`, `vmalloc_huge`, `vfree`, `__vmalloc_node`, `__vmalloc`, `__alloc_percpu`, `free_percpu`, `kvfree_rcu_mightsleep`, `kvfree_rcu`, `alloc_pages_bulk`, `vm_map_ram`, `vm_unmap_ram`, completions, kthreads, and SRCU synchronization.

## Risks and Edge Cases

Defaults can be heavy: one million loops per test and potentially many threads. `align_shift_alloc_test` and `no_block_alloc_test` are marked expected-fail, so failures there are recorded as xfail. Nonblocking allocation runs with preemption disabled around `__vmalloc`, exercising sensitive context constraints. Memory fragmentation and pressure can change outcomes, especially for full-fit and long-busy-list tests.

## Test Signals

Per-worker summary lines report passed, failed, xfailed, repeat, loops, and average microseconds per enabled test. A clean stress run should show zero unexpected failures. The expected module return is `-EAGAIN` for module builds and `0` for built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_vmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_workqueue.c -->
# sources/distributed-fs/ceph-client/lib/test_workqueue.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_workqueue.c` is a stress/performance benchmark for unbound workqueues. It measures `queue_work()` throughput and enqueue latency across workqueue affinity scopes. The source was read as a complete 294-line file.

## Important APIs, Types, and Functions

Module parameters are `nr_threads` and `wq_items`. Static state includes `bench_wq`, `threads_done`, `start_comp`, and `all_done_comp`. `struct thread_ctx` carries per-thread completion, work item, latency array, CPU, and item count. Important routines are `bench_work_fn`, `bench_kthread_fn`, `cmp_u64`, `set_affn_scope`, `run_bench`, and `test_workqueue_init`. The tested scopes are `cpu`, `smt`, `cache_shard`, `cache`, `numa`, and `system`.

## Control Flow

On load, `test_workqueue_init` validates `wq_items`, allocates an unbound sysfs-visible workqueue named `bench_wq`, chooses the thread count as the module parameter or online CPU count capped to online CPUs, and calls `run_bench` once per affinity scope. Each run writes the desired scope to the workqueue sysfs `affinity_scope` file, allocates contexts/tasks/latency storage, starts kthreads bound to online CPUs, releases them with `start_comp`, waits for `all_done_comp`, flushes the workqueue, stops kthreads, merges and sorts latency samples, and logs throughput plus p50/p90/p95 enqueue latency. The module then destroys the workqueue and returns `-EAGAIN` to avoid staying loaded.

## State and Persistence Behavior

The workqueue exists only during module initialization. Per-run state is heap or kvmalloc memory and is freed before the next scope. The benchmark mutates the workqueue's sysfs affinity scope during execution but destroys the workqueue afterward.

## Dependencies and Integration Points

Direct includes cover workqueue, kthread, module parameters, completions, atomics, slab, ktime, cpumask, scheduler, sort, and fs APIs. Integration points are `alloc_workqueue` with `WQ_UNBOUND | WQ_SYSFS`, `queue_work`, `flush_workqueue`, `destroy_workqueue`, `kthread_create`, `kthread_bind`, `kthread_stop`, completions, `filp_open`, `kernel_write`, and `sort`.

## Risks and Edge Cases

The benchmark depends on `/sys/bus/workqueue/devices/bench_wq/affinity_scope` being writable from kernel context. If scope writes fail, that run returns an error but `test_workqueue_init` does not stop or propagate per-scope failures. Very large `nr_threads * wq_items` can consume significant memory for latency arrays. The measured latency is enqueue-call duration, not work completion latency.

## Test Signals

Useful signals are per-scope log lines showing items/sec and p50/p90/p95 nanosecond enqueue latencies. Expected module init return is `-EAGAIN` after benchmark completion. Errors are logged for invalid item count, workqueue allocation failure, sysfs write failure, task creation failure, or allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/test_workqueue.c -->
