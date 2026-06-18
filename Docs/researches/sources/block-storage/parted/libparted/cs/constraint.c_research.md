# File Research: sources/block-storage/parted/libparted/cs/constraint.c

This file implements libparted’s `PedConstraint` solver, combining geometry ranges with start/end alignment requirements and size bounds.

Core model:
- A constraint has:
  - start alignment
  - end alignment
  - allowed start geometry range
  - allowed end geometry range
  - minimum size
  - maximum size
- The introductory comments connect the implementation to intersection closure and the Chinese Remainder Theorem through the alignment layer in `natmath.c`.

Construction and lifetime:
- `ped_constraint_init()` duplicates alignment and geometry inputs into a preallocated constraint.
- `ped_constraint_new()` allocates and initializes a constraint.
- `ped_constraint_new_from_min_max()` creates a constraint requiring a resulting geometry to contain `min` and fit inside `max`.
- `ped_constraint_new_from_min()` uses the whole device as maximum.
- `ped_constraint_new_from_max()` constrains only containment inside `max`.
- `ped_constraint_duplicate()`, `ped_constraint_done()`, and `ped_constraint_destroy()` manage copies and allocated state.

Intersection:
- `ped_constraint_intersect()` intersects start alignments, end alignments, start ranges, end ranges, and size bounds.
- Any empty alignment/range intersection returns `NULL`, representing no solution.
- The resulting size bounds are `max(min_size)` and `min(max_size)`.

Solving:
- `_constraint_get_canonical_start_range()` computes where starts can lie such that at least one valid end can exist.
- `_constraint_get_nearest_start_soln()` aligns the requested start into that canonical range.
- `_constraint_get_end_range()` computes valid ends for a chosen start.
- `_constraint_get_nearest_end_soln()` aligns the requested end into that valid end range.
- `ped_constraint_solve_nearest()` returns a geometry near a requested geometry and asserts it satisfies the constraint.
- `ped_constraint_solve_max()` asks for the nearest solution to the whole-device geometry.

Validation and helpers:
- `ped_constraint_is_solution()` checks start/end alignment, start/end range membership, and min/max size.
- `ped_constraint_any()` creates a permissive whole-device constraint.
- `ped_constraint_exact()` creates a constraint matching a geometry’s exact start and end using zero-grain alignments.

Research notes:
- `NULL` is used both as “no alignment” in lower layers and “no constraint/no solution” in this solver, so callers must follow the documented conventions carefully.
- This file is central to partition placement and resize decisions above the raw device layer.
