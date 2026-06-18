# Research: sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006785`: lines 1-6982, `Docs/researches/chunks/subset-b-006785_research.md`
- `subset-b-006786`: lines 6983-13550, `Docs/researches/chunks/subset-b-006786_research.md`
- `subset-b-006787`: lines 13551-20029, `Docs/researches/chunks/subset-b-006787_research.md`
- `subset-b-006788`: lines 20030-26503, `Docs/researches/chunks/subset-b-006788_research.md`
- `subset-b-006789`: lines 26504-33623, `Docs/researches/chunks/subset-b-006789_research.md`
- `subset-b-006790`: lines 33624-36517, `Docs/researches/chunks/subset-b-006790_research.md`

## Chunk Research

### subset-b-006785: lines 1-6982

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

### subset-b-006786: lines 6983-13550

# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 6983-13550

## Scope

This chunk is a middle slice of `check_erase2_sets()` in the userspace maple tree test suite. It contains replay data, not normal executable control flow: triples of operation code and inclusive address range that are consumed by `check_erase2_testset()`.

The assigned range starts inside `set10[]`, includes complete definitions of `set11[]` through `set22[]`, and ends partway through `set23[]`. The nearby file comment says these tests were pulled from KVM tree modifications that failed, so the data represents regression reproductions for virtual-memory-map style range updates.

## Purpose

The data drives stress and regression tests for maple tree range insertion, null-storage, and erase behavior. Each tuple has the form:

```c
OPERATION, start_index, end_index,
```

`STORE` inserts a non-null encoded value over the inclusive range, `SNULL` stores a null entry over the range, and `ERASE` removes an existing mapping. The chunk focuses on high, page-like virtual address ranges, repeated fragmentation of large intervals into smaller intervals, and recombination after erases or null stores. It is designed to expose bugs in range overwrite accounting, node splitting, slot coalescing, iteration, and lookup after modifications.

## Important APIs, Types, And Functions

- `STORE`, `SNULL`, and `ERASE` are integer operation tags defined just before the harness.
- `check_erase2_sets(struct maple_tree *mt)` owns the static arrays and calls `check_erase2_testset()` for each array later in the function.
- `check_erase2_testset(struct maple_tree *mt, const unsigned long *set, unsigned long size)` interprets each triple, mutates the maple tree, validates it, and checks the expected entry count after every operation.
- `erase_check_store_range(mt, a, i, ptr)` expands to `mtree_test_store_range(mt, a[i], a[i + 1], ptr)` for `STORE` and `SNULL`.
- `check_erase()` wraps `mtree_test_erase()` and asserts that the removed entry equals `xa_mk_value(start)`.
- `mas_range_load()`, `mas_tree_walk()`, `mas_descend_walk()`, and `mas_node_walk()` inspect the pre-operation start and end ranges so the harness can predict how many entries should remain after splitting or overwriting.
- `mas_ce2_over_count()` counts entries overwritten between two maple states, with different corrections for null stores versus real stores.
- Validation APIs used by the harness include `mt_validate()`, `mt_height()`, `mt_for_each()`, `mas_for_each()`, `mtree_load()`, and `MT_BUG_ON()`.

## Data Shape

Within lines 6983-13550, there are 6,538 operation triples:

- `STORE`: 4,961
- `SNULL`: 634
- `ERASE`: 943
- Single-index ranges: 574
- Exactly 4 KiB ranges: 1,095
- Exactly 8 KiB ranges: 807
- Exactly 16 KiB ranges: 471
- Page-aligned ranges where `start` and `end + 1` are 4 KiB aligned: 5,516
- Largest span in this chunk: `140720422371328..140737488351231`, about 15.9 GiB, at line 11322
- Maximum index: `140737488351231`

The ranges mostly resemble userspace VMAs: high canonical user addresses, page-aligned lower bounds, and inclusive end addresses one less than an aligned boundary. Some deliberate off-boundary ranges are also present, for example `SNULL` endings such as `...455359` or single-entry `STORE` rows, to exercise boundary splits and retry behavior.

## Control Flow

The arrays in this chunk are passive data until `check_erase2_sets()` reaches its execution section later in the file. For each set, the function initializes or reinitializes the maple tree with the desired flags, then calls `check_erase2_testset(mt, setN, ARRAY_SIZE(setN))`.

For every triple, `check_erase2_testset()`:

1. Builds `MA_STATE` cursors at the start and end indexes.
2. Calls `mt_set_non_kernel(127)` before the operation.
3. Loads the current start and end entries/ranges through `mas_range_load()`.
4. Updates an expected `entry_count` based on whether the operation appends, overwrites, splits an existing range, null-stores a subrange, or erases an entry.
5. Executes the operation with `mtree_test_store_range()` for `STORE`/`SNULL`, or `mtree_test_erase()` through `check_erase()` for `ERASE`.
6. Calls `mt_validate()` and verifies that both `mt_for_each()` and `mas_for_each()` see exactly `entry_count` non-zero entries.
7. Asserts that index `0` remains empty with `mtree_load(mas.tree, 0) == NULL`.

The important property is that every operation is followed immediately by structural validation and iterator count validation, so a bug can be localized to the replay row that first breaks the tree.

## State And Persistence Behavior

The chunk does not define persistent storage. Its state is the in-memory `struct maple_tree` passed into `check_erase2_sets()`. Stored values are synthetic `xa_mk_value(start_index)` pointers, so the tree value identifies the beginning of the range that created it. Null stores use a `NULL` value and are distinct from erase: `SNULL` records a null range in the maple tree representation, while `ERASE` removes an entry through `mtree_test_erase()`.

Between sets, `check_erase2_sets()` frequently calls `mtree_destroy(mt)`, sometimes after `rcu_barrier()`, and reinitializes flags such as `MT_FLAGS_ALLOC_RANGE`. That means each static set is intended to be a mostly independent replay. Because this assigned chunk begins and ends inside larger arrays, the merge lane should preserve set boundaries from surrounding chunks when building the final per-file report.

## Dependencies

This file includes the kernel maple tree test implementation through `../../../lib/test_maple_tree.c` and uses local userspace test support from `test.h`. The chunk depends on maple tree and XArray concepts and helpers:

- Maple tree structures and cursors: `struct maple_tree`, `struct ma_state`, `struct maple_node`, `struct maple_enode`, `MA_STATE`.
- Maple traversal and validation helpers: `mas_start()`, `mas_next()`, `mas_for_each()`, `mt_for_each()`, `mt_validate()`, `mt_height()`, `mt_dump()`.
- Tree mutation and lookup helpers: `mtree_test_store_range()`, `mtree_test_erase()`, `mtree_load()`, `mtree_destroy()`.
- XArray encoded values and zero entries: `xa_mk_value()`, `xa_is_zero()`.
- RCU wrappers used around iterator validation: `rcu_read_lock()`, `rcu_read_unlock()`, `rcu_barrier()`.

## Integration Points

The operation traces integrate with the broader maple tree test binary through `check_erase2_sets()`, which is invoked near the end of the file from the main maple test path after a new tree is initialized. These KVM-derived sets are one regression group among many other maple tree tests in the same file.

For Ceph's vendored tree under `sources/distributed-fs/ceph-client`, this file is part of the copied Linux radix-tree/maple userspace test harness. It does not integrate with Ceph runtime code directly; its integration value is as upstream kernel data-structure regression coverage carried in the source tree.

## Risks And Edge Cases

- The arrays use raw `unsigned long` literals and require a 64-bit build path. Truncation on non-64-bit configurations would destroy the workload shape; the surrounding harness gates `check_erase2_testset()` under `CONFIG_64BIT`.
- Inclusive end indexes make off-by-one behavior critical. Many rows end at `page_boundary - 1`, while some use deliberately awkward boundaries to force exact pivot and slot updates.
- `SNULL` is not equivalent to `ERASE`. Treating it as deletion would miss null-entry handling and iterator retry behavior.
- The chunk crosses array declarations. A line-based consumer must not interpret `};` or `static const unsigned long setN[] = {` as operation rows.
- Because the assigned range starts in `set10[]` and ends in `set23[]`, analyzing this chunk alone cannot determine the initial state for its first row or the final state after its last row. The test harness executes full arrays, so final reconciliation should combine adjacent chunks before drawing set-level conclusions.
- The repeated huge-range stores ending at `140737488351231` stress tree height, rightmost pivots, and append paths. Failures here are likely to appear as bad entry counts, corrupted pivots, dead-node retries, or non-empty index zero.

## Test Signals

The expected signal is silent pass. Any failure trips `MT_BUG_ON()`, `BUG_ON()`, or emits debug dumps if `check_erase2_debug` is enabled.

Strong signals covered by this chunk:

- `mt_validate(mt)` succeeds after every operation.
- `mt_height(mt)` remains non-zero whenever `entry_count` is non-zero.
- `mt_for_each()` and `mas_for_each()` count the same number of non-zero entries as the harness's predicted `entry_count`.
- `mas_for_each()` handles `xa_is_zero()` retry entries without repeating the same index indefinitely.
- `mtree_load(mas.tree, 0)` remains `NULL`.
- Additional later assertions in `check_erase2_sets()` validate selected post-set lookup gaps and erase side effects for some complete sets adjacent to this chunk.

### subset-b-006787: lines 13551-20029

# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 13551-20029

## Scope

This chunk is a middle slice of the 64-bit maple-tree erase regression corpus in `maple.c`. It starts inside the large generated `set23` trace, contains the tail of `set23`, all of `set24`, and the first portion of `set25`. The source range is data-heavy rather than algorithm-heavy: it is a sequence of triples encoded as `OPCODE, start, end` and consumed later by the maple-tree erase test harness.

Within this exact range, the visible operation mix is:

- `STORE`: 4,987 range insert/store operations.
- `SNULL`: 972 range stores with a `NULL` value.
- `ERASE`: 516 range erase operations.
- Static array boundaries: `set24` begins at line 13983, closes at line 15144, and `set25` begins at line 15145. The chunk ends at line 20029 before `set25` closes, so the remainder is cross-chunk context.

## Purpose

The purpose of this chunk is to preserve VM/KVM-derived maple-tree crash reproducer traces. The surrounding comment identifies these as "VM Generated Crashes" and states that they use their own tree walk for verification. The trace data stresses range replacement, null insertion, deletion, gap accounting, slot splitting, and high-address virtual-memory-like intervals in `MT_FLAGS_ALLOC_RANGE` trees.

The values look like process address ranges, stack/top-of-userspace sentinels, small low mappings, and page-aligned spans. The repetition is intentional: each trace replays a historical sequence that had exposed bugs in erase, split, null, and gap behavior. The data is not a persisted runtime format; it is compiled into the test binary as static regression input.

## Important APIs, Types, And Constants

- `STORE`, `SNULL`, and `ERASE` are integer constants defined near the erase-test support code. In the arrays, each constant is followed by an inclusive `start` and `end`.
- `static const unsigned long set24[]` and `set25[]` are compile-time test vectors. Each complete vector length must remain a multiple of three because the consumer advances by `i += 3`.
- `check_erase2_testset(struct maple_tree *mt, const unsigned long *set, unsigned long size)` is the key consumer. It replays the triples, performs the matching maple operation, then validates tree shape and iterator counts after every triple.
- `erase_check_store_range(mt, set, i + 1, value)` maps to `mtree_test_store_range(mt, set[i + 1], set[i + 2], value)`. `STORE` uses `xa_mk_value(start)` as the stored value, while `SNULL` uses `NULL`.
- `check_erase(mt, start, xa_mk_value(start))` is used for `ERASE` when the starting range currently has an entry.
- `mas_range_load()`, `mas_ce2_over_count()`, `mt_validate()`, `mt_for_each()`, `mas_for_each()`, `mtree_load()`, and `mtree_destroy()` provide the verification path around these static vectors.

## Control Flow

The trace arrays themselves do not branch. Control flow is supplied by `check_erase2_testset()`:

1. Iterate over the selected `setN` array in three-word records.
2. Build maple states at the requested start and end indices.
3. Load the existing start/end ranges to estimate how many non-null entries should remain after the operation.
4. For `SNULL`, store a `NULL` range and update `entry_count` according to whether existing non-null ranges were overwritten.
5. For `STORE`, store `xa_mk_value(start)` over the inclusive range and account for append, split, replacement, or overwrite behavior.
6. For `ERASE`, erase the starting entry if one exists and decrement the expected entry count.
7. Run `mt_validate()`, verify `mt_height()` when entries exist, count entries using both `mt_for_each()` and `mas_for_each()`, reject unexpected zero entries, and assert that index `0` remains empty.

Later, `check_erase2_sets()` replays `set24` and `set25` with `mt_set_non_kernel(99)` and `mt_init_flags(mt, MT_FLAGS_ALLOC_RANGE)`, then runs `rcu_barrier()`, resets non-kernel allocation behavior, calls `mt_validate()`, and destroys the tree after each set.

## State And Persistence Behavior

The only persistent state in this chunk is static compile-time data in read-only arrays. Runtime state is transient and belongs to the surrounding test harness:

- `struct maple_tree` accumulates intervals while a trace is being replayed.
- `struct ma_state` instances are created per operation to inspect range boundaries and iterator state.
- `entry_count` is a harness-side expected-count model, recalculated incrementally from the static triples and checked against live tree iteration.
- `mt_set_non_kernel(99)` steers the userspace/kernel-test allocation simulation for these sets; it is reset to `0` after replay.
- `rcu_barrier()` drains deferred frees before validation/destruction, which is relevant because maple-tree node replacement and erase paths can retire nodes under RCU.

No disk persistence, external file I/O, or user-visible configuration is introduced by this region.

## Dependencies And Integration Points

This chunk depends on earlier definitions in the same file for opcode constants, maple test wrappers, xarray value encoding, RCU helpers, and the local `mas_range_load()`/`mas_ce2_over_count()` verification logic. It also depends on the userspace maple-tree testing environment under `tools/testing/radix-tree`, which provides Linux-style macros such as `BUG_ON`, `MT_BUG_ON`, `MA_STATE`, `ARRAY_SIZE`, and `xa_mk_value`.

The integration point is `check_erase2_sets()`: it calls `check_erase2_testset(mt, set24, ARRAY_SIZE(set24))` and `check_erase2_testset(mt, set25, ARRAY_SIZE(set25))` during the erase regression suite. Since this chunk starts and ends inside larger arrays, merge/reconciliation with adjacent chunks is required to understand the complete contents of `set23` and `set25`.

## Risks And Maintenance Notes

- The trace data is brittle by structure. Adding, deleting, or reordering a single numeric token can desynchronize the three-word records and turn later opcodes into addresses.
- The ranges are inclusive and often page-aligned. Converting them to half-open intervals or normalizing adjacent values would change the regression semantics.
- Many operations intentionally overwrite existing stores with `NULL`, then split those nulls with new stores or erases. Deduplicating repeated-looking sequences would remove bug coverage.
- The exact high numeric addresses are part of the reproducer shape. They stress upper-bound handling, tree height, slot limits, and gap search near top-of-user address ranges.
- `set25` is incomplete in this chunk. Any final per-file analysis must combine the following chunk before making whole-array conclusions about its closing erases or postconditions.

## Test Signals

Primary pass/fail signals are assertions in `check_erase2_testset()` and follow-up validation in `check_erase2_sets()`:

- `mt_validate(mt)` must succeed after every operation and again after `set24`/`set25` replay.
- `mt_for_each()` and `mas_for_each()` counts must match the modeled `entry_count`.
- `mas_for_each()` must not return an unexpected `xa_is_zero()` entry at the same index.
- `mtree_load(mas.tree, 0)` must stay `NULL`.
- After each set, `rcu_barrier()` and `mtree_destroy()` should complete without exposing dangling-node or deferred-free errors.

This chunk specifically contributes coverage for dense overlapping `STORE`, `SNULL`, and `ERASE` patterns in allocation-range maple trees, including transitions where a null range is split and then partially erased.

### subset-b-006788: lines 20030-26503

# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 20030-26503

## Scope

This chunk is a contiguous slice of the large VM-generated maple tree regression corpus inside `check_erase2_sets()`. It contains operation triples for the static `unsigned long` test arrays consumed by `check_erase2_testset()`, not standalone executable logic. The covered lines start in the tail of `set25`, include all of `set26` through `set33`, and end partway through `set34`.

The requested range has 6,474 source lines. Of those, 6,454 are operation rows:

- `STORE`: 4,403 rows
- `SNULL`: 1,250 rows
- `ERASE`: 801 rows

The remaining rows are array boundaries, braces, and declarations. The operation ranges span from low user-space style addresses such as `4194304` up to high canonical boundary ranges ending at `140737488351231`; no zero start/end ranges appear in this chunk.

## Purpose

These rows preserve previously failing VM/KVM-shaped maple tree update sequences. Each operation triple is replayed by `check_erase2_testset()` to stress range insertion, null replacement, deletion, splitting, merging, gap movement, and tree rebalance behavior under `MT_FLAGS_ALLOC_RANGE`.

The data is intentionally repetitive and address-specific. It exercises patterns that are difficult to cover with small hand-written tests:

- widening stores that repeatedly replace an existing prefix or suffix range
- nulling subranges with `SNULL` to force entry splitting without creating a normal value
- erasing exact, adjacent, and nested ranges after prior split/null operations
- alternating high stack-like ranges with heap/mmap-like ranges
- creating and then removing small 4 KiB, 8 KiB, 12 KiB, 16 KiB, and larger fragments inside much broader spans
- preserving corner cases around inclusive end addresses and adjacent range boundaries

## Important APIs, Types, And Functions

The data in this chunk depends on definitions immediately above the arrays:

- `STORE`, `SNULL`, and `ERASE` are integer operation tags.
- `erase_check_store_range(mt, a, i, ptr)` expands to `mtree_test_store_range(mt, a[i], a[i + 1], ptr)`.
- `check_erase2_testset(struct maple_tree *mt, const unsigned long *set, unsigned long size)` iterates the arrays in triples.
- `mas_range_load()` and the temporary `MA_STATE` instances inspect the range currently covering the operation start and end before applying the update.
- `mas_ce2_over_count()` estimates how many entries are overwritten when an operation spans multiple existing slots or partially overlaps range boundaries.
- `check_erase()` validates erase behavior for `ERASE` rows.
- `mt_validate()`, `mt_for_each()`, `mas_for_each()`, and `mtree_load()` provide post-operation structural and iteration checks.

The important external maple tree types/APIs involved are:

- `struct maple_tree`
- `struct ma_state`
- `MA_STATE`
- `mt_init_flags(..., MT_FLAGS_ALLOC_RANGE)`
- `mtree_test_store_range`
- `mtree_load`
- `mt_height`
- `mas_reset`
- RCU helpers used around iterator validation and after each replayed set

## Covered Arrays And Data Shape

The chunk begins at line 20030 inside `set25`. That tail continues a long regression sequence of high-address ranges with many split/null/store patterns. Near the end of `set25`, lines 21880-21930 repeatedly store progressively lower starts while holding a large common end (`140249710600191`), then split the tail with `SNULL, 140249682087935, 140249710600191` followed by stores for both resulting halves. This stresses repeated widening/replacement and final boundary splitting.

`set26` is small and complete in this chunk. It starts at line 21933 and includes high boundary stores, low ranges around `4194304`, `7159808`, and `30867456`, then repeatedly stores and erases nested ranges around `140109040943104` through `140109040959487`. It is a compact regression for exact erasure after shrinking or restaging a range.

`set27` is complete. It begins at line 21957 with the standard high-address setup, then uses repeated `SNULL` plus `STORE` splits in ranges around `944784...` and `140415...`. Later in the array, broad repeated stores from a stable base (`94478511173632`) extend the end boundary through many increasing values, then a large `SNULL` and erase sequence at `140415535910912` and `140415537422336` checks movement across widened ranges.

`set28` is complete and short. It starts at line 22353, replaying the same general pattern against different addresses: high boundary setup, split/null and erase around `938658...`, deep split/store/erase around `139918...`, and cleanup around adjacent fragments. Its value is address diversification for the same structural operations.

`set29`, `set30`, `set31`, and `set32` are complete and large. They share a generated pattern: a high boundary setup, heap-like ranges near `948804...`, `946307...`, and `944277...`, followed by extensive erase sweeps of many adjacent 4 KiB-leading plus larger trailing ranges. The erase-heavy tails test whether rebalance and gap accounting remain correct when many fragmented entries are removed in sequence.

`set33` is complete. It begins at line 25787 and first follows the split/null/store pattern for `941338...` and `140583...` ranges, then builds broader nested ranges from `140583096004608` through `140583631245311`. It uses `SNULL` and `ERASE` to remove interior spans while preserving surrounding ranges, testing multi-level tree compression and correct iterator-visible entry counts.

`set34` starts at line 25929 and continues beyond this chunk. The covered prefix mirrors the `set33` structure with different addresses: high boundary setup, `946329...` heap-like splits, `140012544...` splits, and then broader nested ranges around `140012...` and `140011...`. The requested line range ends at line 26503 after:

- `SNULL, 140011177484288, 140011185872895`
- `STORE, 140011185872896, 140011202658303`
- `STORE, 140011177484288, 140011185872895`

The continuation after this chunk completes the current nested split/rebuild sequence.

## Control Flow

The control flow is data-driven:

1. `check_erase2_sets()` initializes a maple tree for each static set with `MT_FLAGS_ALLOC_RANGE`.
2. It calls `check_erase2_testset(mt, setN, ARRAY_SIZE(setN))`.
3. `check_erase2_testset()` advances through the array by three elements at a time: operation tag, inclusive start, inclusive end.
4. For `STORE`, it stores `xa_mk_value(start)` across the range and updates expected entry counts based on pre-existing start/end coverage.
5. For `SNULL`, it stores `NULL` across the range, forcing deletion/null replacement behavior while accounting for partial splits.
6. For `ERASE`, it erases the start value if present and decrements expected entry count.
7. After every triple, it validates tree structure and checks iterator-visible entry counts with both `mt_for_each()` and `mas_for_each()`.
8. After each complete set, the harness runs `rcu_barrier()`, performs selected `mtree_load()` or gap checks for some sets, validates the tree, and destroys it.

This chunk supplies only the replay stream for steps 3-6. Its correctness is observed through the validation machinery around every operation.

## State And Persistence Behavior

The state under test is the in-memory `struct maple_tree` built while replaying each set. No durable filesystem or on-disk persistence is involved.

Important state transitions include:

- entries are stored as `xa_mk_value(start)`, making the range start both the key range and value identity for verification
- `SNULL` rows store `NULL`, which can remove or split entries depending on the current tree state
- `ERASE` rows rely on `check_erase()` and expected-value matching
- `entry_count` tracks the expected number of non-null visible entries after each mutation
- `mt_validate()` checks internal maple node consistency after every replayed operation
- iterator passes confirm that logical visible entries match the expected count after splits, null stores, and erases

Because `set34` is cut off by this chunk, the persisted test state for that array is incomplete in this document. The next chunk must describe the rest of the same array before any final per-file synthesis treats `set34` as a complete regression case.

## Dependencies And Integration Points

This chunk integrates with the local maple tree test harness in `tools/testing/radix-tree/maple.c`. The arrays depend on:

- XArray value encoding through `xa_mk_value()` and `xa_is_zero()`
- Maple tree range storage and iteration helpers from the test build
- RCU registration and read-side primitives used by the harness
- assertion macros such as `MT_BUG_ON()` and `BUG_ON()`
- `CONFIG_64BIT`; these VM-generated erase tests are inside the 64-bit-only block

The test data is called from the broader `maple_tree_tests()` path through `check_erase2_sets()`. It is not exported as an API and has no Ceph-specific runtime integration; it is vendored kernel-style test code under the Ceph client source tree.

## Risks And Edge Cases

- The arrays are extremely order-sensitive. Reordering rows, deleting apparent duplicates, or normalizing addresses would invalidate the regression sequence.
- Ranges are inclusive. Off-by-one mistakes around `start`, `end`, split points, and adjacent rows are the main risk these vectors are meant to catch.
- `SNULL` rows are not equivalent to `ERASE` rows in the expected-count logic; they may split an entry, remove a visible value, or preserve surrounding ranges.
- The test relies on `entry_count` matching two independent iterators. A bug in overwrite accounting can make the test fail even if the tree is structurally valid.
- The chunk boundary lands inside `set34`, so analysis of `set34` must be merged with the following chunk before drawing conclusions about that set's final tree state.
- The generated address values resemble VM area addresses. They should be treated as semantic regression fixtures, not arbitrary numeric noise.

## Test Signals

Strong pass/fail signals produced when these rows are replayed include:

- `MT_BUG_ON(mt, check != entry_count)` after `mt_for_each()`
- `MT_BUG_ON(mt, check != entry_count)` after `mas_for_each()`
- detection of unexpected retry/zero entries during `mas_for_each()`
- `MT_BUG_ON(mt, mtree_load(mas.tree, 0) != NULL)` after each operation
- `mt_validate(mt)` after each row and after each set
- selected post-set `mtree_load()` and gap checks in `check_erase2_sets()` for later arrays

For this chunk specifically, useful regression signals are failures during replay of `set25` tail through `set33`, plus failures in the first half of `set34` that involve split/null/store behavior around `140012...` and `140011...` ranges.

### subset-b-006789: lines 26504-33623

# sources/distributed-fs/ceph-client/tools/testing/radix-tree/maple.c lines 26504-33623

## Scope And Purpose

This chunk is a middle-to-late slice of the large `check_erase2_sets()` regression suite in the userspace maple tree test harness. It is not normal library code; it is mostly static replay data captured from previous maple-tree, VM, and KVM failure scenarios. The replay language is a sequence of `unsigned long` triples: operation opcode (`STORE`, `SNULL`, or `ERASE`), range start, and range end.

The chunk begins inside `set34[]`, contains all of `set35[]` through `set42[]`, contains `set43[]`, and then enters the first execution block of `check_erase2_sets()`. The visible data stresses range store, null-range overwrite, point/range erase, top-down empty-area search, gap accounting, reverse traversal, and allocation-range behavior for dense address maps.

## Important APIs, Types, And Data Shapes

- `static const unsigned long setNN[]`: immutable replay traces consumed by `check_erase2_testset()`. In this chunk the visible declarations begin at `set35[]` on line 26810 and run through `set43[]` on line 33474, while lines 26504-26809 continue the tail of `set34[]`.
- `STORE, start, end`: tells the replay helper to store `xa_mk_value(start)` across an inclusive range. These operations create, split, merge, and overwrite maple tree entries.
- `SNULL, start, end`: stores `NULL` across an inclusive range. In the replay helper this exercises gap creation, entry removal, and null-range accounting rather than a real value store.
- `ERASE, start, end`: erases the entry at `start` through `check_erase()`; in these traces `end` records the original covered range boundary for human/debug context.
- `struct maple_tree *mt`: the mutable tree under test. The arrays in this chunk are later replayed into the same pointer after repeated `mt_init_flags()` and `mtree_destroy()` cycles.
- `MA_STATE(mas, mt, 0, 0)`: the local maple-state cursor initialized just after the arrays. Later code resets and reuses it for iteration and `mas_empty_area_rev()` checks.
- `MT_FLAGS_ALLOC_RANGE`: selected for these replay sets to enable allocation-range/gap tracking, the important behavior these regressions target.
- `mt_set_non_kernel(n)`: configures the userspace shim's simulated non-kernel allocation mode and allocation pressure. Several tests in and after this chunk set it to `99` before replay and reset it to `0` after validation.
- `check_erase2_testset(mt, setN, ARRAY_SIZE(setN))`: the common interpreter for these arrays. It validates the tree after each triple, counts expected entries, compares `mt_for_each()` and `mas_for_each()` traversal counts, and checks that index zero remains empty.

## Chunk Data Map

The assigned span contains 5,116 visible `STORE` rows, 1,223 `SNULL` rows, and 622 `ERASE` rows. The rows are intentionally numeric and mostly generated or copied from failure logs; the important semantics are the relative range overlaps, null holes, and repeated boundary splits, not the real-world meaning of the addresses.

- Lines 26504-26809: tail of `set34[]`, continuing a large high-address replay with many split stores, null stores, and erase cleanup rows.
- Lines 26810-27566: complete `set35[]`, a replay that creates empty leaves at the end of parents, then erases many fine-grained fragments.
- Lines 27567-28427: complete `set36[]`, a close variant of `set35[]` with different captured addresses and repeated end-of-parent empty-leaf stress.
- Lines 28428-28553: complete `set37[]`, a shorter replay that sets up a load-at-boundary assertion later.
- Lines 28554-29363: complete `set38[]`, another long address-fragmentation replay paired with the same later boundary load assertion as `set37[]`.
- Lines 29364-29735: complete `set39[]`, a shorter high-address replay with nested stores and erases.
- Lines 29736-30486: complete `set40[]`, a large replay ending in a cleanup erase sequence.
- Lines 30487-30796: complete `set41[]`, notable for a long run of regularly spaced `STORE` rows and a final huge `SNULL` range.
- Lines 30797-33472: complete `set42[]`, a very large 32-bit-address-style replay with many IPv4-sized intervals, repeated nulling/restoring of the same gaps, and an embedded mmap debug comment.
- Lines 33474-33493: complete `set43[]`, a small replay for an off-by-one gap calculation bug.
- Lines 33495-33623: beginning of the executable replay-and-assertion sequence for `check_erase2_sets()`, covering sets `set` through `set17`.

## Control Flow In This Chunk

The array data itself has no runtime control flow until `check_erase2_sets()` reaches the execution block at line 33495. There the function creates local counters and cursor state, then repeatedly initializes the tree, replays one static set, validates postconditions, and destroys the tree before moving to the next set.

The visible execution sequence starts by running early sets outside this chunk: `set`, `set2`, `set3`, and so on. Each call to `check_erase2_testset()` applies every triple in the selected set and validates after each operation. Several paths then add targeted assertions that were not expressible as plain replay rows:

- After `set2`, `mt_find()` is checked over `140735933894656..140735933906943` to ensure no entry remains in that gap.
- After `set4`, `mas_for_each()` is run under `rcu_read_lock()` and skips `xa_is_zero()` retry markers.
- After `set11`, `mas_empty_area_rev()` must find a reverse gap whose `mas.last` is exactly `140014592573439`.
- After `set12`, a full `mas_for_each()` traversal counts non-zero entries and asserts the count does not exceed 12.
- After `set13`, `mtree_erase()` and `mas_empty_area_rev()` reproduce a reverse empty-area scenario.
- After `set16`, a comment records a prior slot-zero limit update bug; the test expects `mas_empty_area_rev()` to end at `139921865547775`.
- After `set17`, the visible comment records a previous reverse-walk bug where trailing nulls were not counted, and the expected `mas.last` is `139953197322239`.

The calls for `set35[]` through `set43[]` are just beyond the requested line range, but they are visible in the immediate following context and are the integration destination for the arrays declared here. Those later calls replay the data in this chunk and then validate special conditions for empty leaves, null boundary loads, reverse gap movement, and off-by-one gap calculations.

## State And Persistence Behavior

All state is in-memory test state. The static arrays persist for the process lifetime as read-only test data, but they are not external storage. The mutable state is the `struct maple_tree`, its allocated maple nodes, per-node gap metadata, root height, and iterator cursor fields in `struct ma_state`.

Every replay group is isolated by `mt_init_flags()` before use and `mtree_destroy()` after validation. `rcu_barrier()` appears after many replays to flush deferred frees before the next tree instance is built. `mt_set_non_kernel()` temporarily changes the shim's allocation mode, which can affect node allocation and rebalance behavior; the code resets it after each targeted test.

`SNULL` rows are particularly important for state transitions. They can delete values, create gaps, split an existing stored range into left/right fragments, and leave empty child nodes that must still maintain correct parent gap metadata. Repeated `STORE` rows over the same ranges then test whether the tree can recover consistent structure after those null holes are refilled.

## Dependencies And Integration Points

This chunk depends on the earlier definitions of the trace opcodes, the `check_erase2_testset()` replay interpreter, xarray value helpers, maple-tree internals, and the userspace RCU/test shim. It is compiled only in the `CONFIG_64BIT` block around `check_erase2_testset()` and `check_erase2_sets()`, which matters because many captured addresses exceed 32-bit range.

The trace data integrates with:

- public-style maple APIs through `mtree_test_store_range()`, `mtree_test_erase()`, `mtree_load()`, `mt_find()`, `mtree_erase()`, and `mtree_destroy()`;
- iterator APIs through `mt_for_each()`, `mas_for_each()`, `mas_find()`, and `mas_prev()`;
- gap search through `mas_empty_area_rev()`;
- structural checking through `mt_validate()` and `MT_BUG_ON()`;
- RCU simulation through `rcu_read_lock()`, `rcu_read_unlock()`, and `rcu_barrier()`.

The comments embedded around the execution block document integration with VM mmap behavior. In particular, `set42[]` carries an mmap debug note about `unmapped_area_topdown`, a found gap, a search window ending at `4052029440 - 4096`, and a mismatch against `rb_find_vma()`. That makes the set a regression fixture for maple-tree gap search compared with historical VMA-tree behavior.

## Risks And Edge Cases

- The chunk starts in the middle of `set34[]`; a parser that treats this span as an independent C unit will see leading rows without their declaration.
- The chunk ends before the calls that execute `set35[]` through `set43[]`; the merge lane must combine this with the following chunk to cover their runtime assertions.
- The static traces are brittle but intentional. Small numeric edits can destroy the reproduced tree shape even if the file still compiles.
- Many operations are inclusive range endpoints. Off-by-one mistakes in `end`, `mas.last`, or `mas_empty_area_rev()` expectations are a primary failure mode.
- `SNULL` ranges can represent real entry removal, partial overwrite, or a no-op over an already-empty gap. Expected entry count accounting must distinguish these cases.
- Empty leaves at the end of a parent are explicitly targeted by `set35[]` and `set36[]`; gap propagation can be wrong even when load/store behavior looks correct.
- Repeated null/store loops over the same large ranges in `set42[]` stress whether gap metadata remains stable after repeated deletion and reinsertion.
- RCU retry markers (`xa_is_zero()`) are skipped by iterator checks; a failure to advance after such a marker would indicate iterator retry/livelock risk.

## Test Signals

Useful success signals for this chunk are:

- The userspace maple/radix-tree test target compiles on a 64-bit configuration so these large arrays are included.
- `check_erase2_testset()` can replay each array without `MT_BUG_ON()` and with `mt_validate()` passing after every triple.
- The entry count inferred by `check_erase2_testset()` matches both `mt_for_each()` and `mas_for_each()` counts after every operation.
- For this chunk's declared arrays, the later execution block should replay `set35[]` through `set43[]` and pass the special checks around empty leaves, `mtree_load()` returning `NULL` at selected boundaries, reverse empty-area search, and off-by-one gap calculation.
- The explicit expectations visible in this span for `set11`, `set16`, and `set17` must hold: the `mas.last` values after reverse gap search are exact regression sentinels.
- No persistent files or external state should change when these tests run; failures are signaled through assertions, debug dumps, or process aborts.

### subset-b-006790: lines 33624-36517

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
