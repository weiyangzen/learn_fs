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
