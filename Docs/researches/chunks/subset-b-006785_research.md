# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 1-6982

## Scope And Purpose

This chunk is the opening slice of the userspace maple tree test harness at `tools/testing/radix-tree/maple.c`. It sets up kernel-test compatibility shims, pulls in the shared maple shim and the kernel `test_maple_tree.c` implementation, defines RCU stress-test data structures that are used much later in the same file, and then begins the erase/range-overwrite regression suite.

The executable logic in this chunk focuses on validating maple tree erase behavior, range-store behavior, internal walk semantics, entry-count accounting, and iterator consistency. The large middle and tail of the chunk are generated or captured VM/KVM-style operation traces: triples of `STORE`, `ERASE`, and potential `SNULL` operations encoded as `unsigned long` arrays. Lines 1-6982 include complete arrays `set` through `set9` inside `check_erase2_sets()` and then stop partway through `set10[]`; later chunks contain the rest of that function and the calls that feed these arrays into the common replay routine.

## Important Types, Macros, And APIs

- `module_init`, `module_exit`, `MODULE_*`, and `dump_stack()` are locally stubbed so kernel-oriented test sources can compile in userspace. `dump_stack()` maps to `assert(0)`, making unexpected stack dumps fatal in the harness.
- `test.h`, `../shared/maple-shim.c`, and `../../../lib/test_maple_tree.c` provide the userspace kernel compatibility layer, maple tree implementation hooks, test helpers such as `check_load()` and `check_insert()`, and maple internals such as `struct ma_state`, `mas_start()`, `mas_next()`, `mas_slot()`, `mte_dead_node()`, and validation/debug helpers.
- `RCU_RANGE_COUNT`, `RCU_MT_BUG_ON()`, `struct rcu_test_struct2`, `struct rcu_test_struct3`, and `struct rcu_reader_struct` declare shared state for later threaded RCU tests. They track the tree under test, stop/start flags, reader counts, observation counters, index/last arrays, and reader behavior toggles.
- `check_erase()` is a thin wrapper around `mtree_test_erase()` that asserts the erased pointer is the expected one.
- `erase_check_load`, `erase_check_insert`, and `erase_check_erase` bind the fixed `set[]` array in `check_erase_testset()` to helper calls while alternating between two expected entry pointers.
- `STORE`, `SNULL`, `ERASE`, and `ec_type_str()` define the mini trace language used by `check_erase2_testset()`: range store with a value, range store with `NULL`, and single-index erase.
- `erase_check_store_range()` maps a trace triple to `mtree_test_store_range()`, making the replay path use the same test wrapper as the rest of the harness.

## Erase Test Control Flow

`check_erase_testset()` builds a small deterministic erase workload around a fixed index list containing isolated indexes and clustered ranges such as `6003..6015`, `7002..7015`, and later groups up to `15015`. It registers the current thread with the userspace RCU harness, marks the tree as RCU-enabled, inserts several entries, and repeatedly checks that loads and erases return the expected values.

The early portion tests single-entry erases, missing loads around erased holes, reinsertion after erase, and whether the root node changes as expected under RCU versus non-RCU mode. It explicitly toggles `mt_set_non_kernel()` with small allocation limits to exercise allocation-sensitive paths and verifies that operations which should not split a leaf keep `mt->ma_root` as a leaf.

The middle portion fills enough slots to exercise coalescing. It erases adjacent entries in a controlled order, checking after each erase that deleted indexes are absent while all others still load correctly. This targets leaf compaction, adjacent-slot coalescing, and node rebalance behavior when holes expand.

The final portion of `check_erase_testset()` repopulates the tree and then erases progressively from high indexes downward and low indexes upward. After every erase it scans the full fixed set and asserts the exact present/absent boundary. This stresses tree shrinking and root collapse behavior before unregistering the RCU thread.

## Range Replay And Internal Walk Helpers

`mas_ce2_over_count()` is a local accounting helper for the generated erase2 traces. Given maple states at the start and end of an operation plus the entries/ranges found at those states, it estimates how many existing entries a range operation overwrites. It walks from `mas_start` to `mas_end->last` using `mas_next()`, counts spanned entries, guards against retry loops with `BUG_ON(retry > 50)`, and then adjusts the count for split-start and split-end cases. The `null_entry` branch handles `SNULL`/erase-to-null accounting differently from real value stores.

`mas_node_walk()` and `mas_descend_walk()` duplicate a direct maple-node traversal for verification. `mas_node_walk()` finds the pivot slot containing `mas->index`, updates `mas->offset`, and records either the leaf data range or the child traversal bounds. It handles dense nodes, dead nodes, pivot exhaustion, and leaf versus internal-node state updates. `mas_descend_walk()` repeatedly applies that node walk and descends through child slots until it reaches a leaf or detects a dead node.

`mas_tree_walk()` wraps the direct traversal from the root. It restarts from `ma_start`, handles empty and root-pointer trees, retries if a dead node is observed, and sets `mas->end` from `mas_data_end()`. `mas_range_load()` uses `mas_tree_walk()` to return the entry at a state while also reporting the entry's covered `[range_min, range_max]`; if the active node dies during the read, it resets to the original index and retries. Together these helpers provide an independent oracle for the range replay code instead of relying only on public load APIs.

## `check_erase2_testset()` Behavior

`check_erase2_testset()` exists only under `CONFIG_64BIT`, matching the large address values captured from VM/KVM-style workloads. It consumes an operation array three words at a time: opcode, start index, and end index. Before applying each operation it builds two `MA_STATE`s for the start and end addresses, uses `mas_range_load()` to discover the existing entries and ranges, and updates an expected `entry_count`.

For `SNULL`, it stores a `NULL` range with `mtree_test_store_range()` and adjusts the expected entry count for whole-entry removal, split ranges, or multi-slot overwrite. No `SNULL` rows appear in lines 1-6982, but the code path is part of this chunk.

For `STORE`, it creates `xa_mk_value(start)` and stores that value across the requested range. The expected count logic distinguishes append, overwrite of a single existing range, range split at either end, and multi-entry replacement. For `ERASE`, it erases only the start index through `check_erase()` and decrements the expected count when a start entry existed.

After each operation the function validates the tree with `mt_validate()`, checks that non-empty trees have height, counts entries using `mt_for_each()`, and separately counts entries under `rcu_read_lock()` using `mas_for_each()`. It treats `xa_is_zero()` as a retry marker and asserts that retry handling advances. Finally it asserts that index `0` remains empty. These repeated checks make every trace row a validation point for both tree structure and iterator behavior.

## Generated Operation Trace Data In This Chunk

`check_erase2_sets()` begins at line 726 and declares replay arrays copied from failed KVM/tree modification scenarios. In this chunk the complete arrays are:

- `set` through `set4`: shorter initial traces that store large user-space-like ranges, erase entire ranges, then rebuild them as finer-grained adjacent ranges.
- `set5` through `set8`: larger traces with repeated split, erase, and restore patterns across address bands. They force many boundary cases where a large range is split into left/middle/right fragments and then partially erased.
- `set9`: a very large trace using many single-index erases where `start == end`, followed by range stores that refill the removed subranges. This stresses point erases inside broad ranges and verifies that iterators see the resulting fragments correctly.
- `set10`: starts at line 5232 and continues beyond this chunk. Lines 5232-6982 include only its opening segment, so this chunk alone is not a complete C declaration for `set10[]`.

Counting visible operation rows through line 6982 gives 6,228 replay operations: 4,592 `STORE` rows and 1,636 `ERASE` rows. No `SNULL` rows appear in this slice. The numeric addresses are not meaningful as constants in isolation; they are regression stimuli that recreate prior virtual-memory-map shapes and maple tree fragmentation patterns.

## State And Persistence Behavior

All tree state is in-memory test state. The harness mutates `struct maple_tree` instances through insert, erase, range-store, iterator, and direct traversal APIs, but it does not persist data to disk or expose runtime state outside the test process.

The most important state transitions are maple node allocation/reuse, RCU mode versus non-RCU behavior, root replacement, leaf split/coalesce, tree height growth/shrink, and iterator state in `struct ma_state`. The tests also maintain expected logical state through `entry_count` and the fixed trace arrays. `mt_set_non_kernel()` changes the simulated allocation environment, so some assertions are explicitly tied to whether the tree is operating under RCU and whether node replacement is required.

## Dependencies And Integration Points

This file is a userspace test translation unit that directly includes implementation and test sources instead of linking them as separate objects. It depends on the radix-tree test harness, pthread/RCU shims, xarray value encoding (`xa_mk_value()`, `xa_is_zero()`), maple tree internals, and kernel-style assertion/debug macros provided by `test.h` and the included shim.

The code is intentionally coupled to maple internals: it inspects `mt->ma_root`, node type, pivots, slots, dead-node state, offsets, and `ma_state` fields. That coupling is the point of this userspace file because these cases require internal knowledge that is difficult to assert through black-box kernel tests. It also means internal maple representation changes can require test updates even when public API behavior is unchanged.

The trace replay integrates public-style operations (`mtree_test_store_range()`, `mtree_test_erase()`, `mtree_load()`), iterator APIs (`mt_for_each()`, `mas_for_each()`), RCU read-side locking, and structural validation (`mt_validate()`). Failures therefore identify either external behavior regressions or mismatches between public APIs and internal iterator/traversal assumptions.

## Risks And Edge Cases

- This chunk stops in the middle of `set10[]`; any parser or reviewer must merge later chunks before treating `check_erase2_sets()` as syntactically complete.
- `mas_ce2_over_count()` contains complex expected-count adjustment logic. If the oracle is wrong, the test can either miss a real tree bug or flag correct maple behavior as a failure.
- The direct walk helpers intentionally read internal node pivots and slots. They are valuable as an independent verifier, but they can become stale if maple internals change.
- RCU paths must handle dead nodes and retry entries correctly. The code explicitly checks dead-node retries and `xa_is_zero()` handling because iterator livelock or duplicate counting would invalidate range traversal under concurrent-style conditions.
- Point erases where `start == end` and range overwrites that split both start and end entries are heavily represented in the trace data. These are high-risk cases for off-by-one boundaries and incorrect entry-count maintenance.
- Allocation limiting via `mt_set_non_kernel()` makes root replacement and split/coalesce behavior observable. Tests that are run under a different shim configuration may not exercise the same allocation paths.

## Test Signals

Useful validation signals for this chunk and the later merged per-file report include:

- Build and run the userspace radix-tree/maple test target on a 64-bit configuration so `check_erase2_testset()` and the large trace arrays are compiled.
- Confirm `check_erase_testset()` passes under both RCU-marked and non-kernel allocation-limited modes, including root-node replacement expectations and leaf/no-split assertions.
- During trace replay, every operation should pass `mt_validate()`, the expected `entry_count` should match both `mt_for_each()` and `mas_for_each()`, and `mtree_load(tree, 0)` should remain `NULL`.
- Iterator tests should not loop indefinitely on `xa_is_zero()` retry entries; the test explicitly fails if retry handling does not advance.
- Full-file syntax validation must include chunks after line 6982 because `set10[]` is incomplete in this chunk.
- Regression failures should record the operation array name and triple index, since the numeric trace rows are the primary reproducer for VM/KVM-derived maple tree erase bugs.
