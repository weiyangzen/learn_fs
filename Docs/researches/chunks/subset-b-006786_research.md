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
