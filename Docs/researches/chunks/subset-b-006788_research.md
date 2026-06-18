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
