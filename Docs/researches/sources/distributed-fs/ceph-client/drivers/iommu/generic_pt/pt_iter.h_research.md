# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/pt_iter.h

## Purpose

`pt_iter.h` implements Generic PT range construction, range validation, table index math, entry iteration, recursive walking, top/upper/all range helpers, page-size selection, and macro-generated inlined level walkers.

## Important APIs, Types, and Functions

- Range validation and conversion: `pt_check_range`, `pt_index_to_va`, `pt_range_to_index`, `pt_range_to_end_index`.
- Iteration primitives: `_pt_iter_first`, `_pt_iter_load`, `pt_next_entry`, `for_each_pt_level_entry`, `pt_load_single_entry`.
- Range constructors: `pt_top_range`, `pt_all_range`, `pt_upper_range`, `pt_make_range`, `pt_make_child_range`, `pt_range_slice`.
- Walker helpers: `pt_init`, `pt_init_top`, `pt_descend`, `pt_walk_range`, `pt_walk_descend`, `pt_walk_descend_all`.
- Geometry helpers: `pt_top_memsize_lg2`, `pt_compute_best_pgsize`, `pt_pgsz_count`.
- `PT_MAKE_LEVELS`: generates unrolled per-level walkers for performance.

## Control Flow

Callers build a `pt_range`, validate it, initialize a `pt_state`, then iterate entries in the current table level. Walkers recurse through `pt_descend` or `pt_walk_descend` and use `PT_MAKE_LEVELS` to let the compiler specialize each level as a constant. The map path uses page-size helpers to choose the largest valid leaf size constrained by VA/OA alignment, range length, and format page-size bitmap.

## State and Persistence Behavior

The file does not allocate or persist state. It mutates stack `pt_range` and `pt_state` objects during traversal, including lazily updating `range->va` to reflect current indexes.

## Dependencies and Integration Points

It depends on `pt_common.h` callback APIs and is used by `iommu_pt.h` and both KUnit headers. It is central to every generated format instance.

## Risks and Edge Cases

- Sign-extended formats require special lower/upper range handling; using `range->va` from `pt_all_range` during iteration is explicitly unsafe.
- Full-VA cases need `fvalog2_*` helpers to avoid undefined shifts.
- `pt_next_entry` must skip all items in contiguous leaves or walkers can double-count/clear entries.
- Generated level walkers produce larger code and require `PT_MAX_TOP_LEVEL <= 5`.

## Test Signals

KUnit validates range indexes, radix coverage, upper/lower sign-extended ranges, best page-size selection, page-size counts, contiguous iteration, and all generated walker levels.
