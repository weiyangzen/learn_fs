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
