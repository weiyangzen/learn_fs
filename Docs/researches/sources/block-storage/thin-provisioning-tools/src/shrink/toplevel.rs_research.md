# File Research: sources/block-storage/thin-provisioning-tools/src/shrink/toplevel.rs

This file implements range-remapping helpers for shrinking or relocating block ranges.

Key elements:
- `BlockRange = Range<u64>` and `range_len()` provide basic block-range utilities.
- `build_remaps(ranges, free)` maps source ranges into available free ranges, splitting source ranges when needed.
- It returns `Err("Insufficient free space")` if the free ranges cannot cover all requested input ranges.
- `find_first()` performs a binary search over sorted remaps to locate the first overlapping remap.
- `remap(r, remaps)` maps an input range through sorted `(from_range, to_start)` remap rules, preserving unmapped gaps as original ranges.

Tests:
- `build_remaps` tests cover one-to-one, one-to-many, many-to-one, many-to-many, empty/noop, exact-fit, insufficient-space, and boundary-value cases.
- `remap_test` covers no remaps, before/after remap ranges, partial overlaps, full overlaps, and multiple remap strides.

Interactions:
- This is a pure helper module with no I/O.
- Remaps must be sorted by `from.start` for `remap()` correctness.

Risks and notes:
- `build_remaps()` assumes callers supply non-overlapping, meaningful ranges. It does not validate ordering or overlap.
- `remap()` relies on sorted remaps and does not enforce that precondition.
