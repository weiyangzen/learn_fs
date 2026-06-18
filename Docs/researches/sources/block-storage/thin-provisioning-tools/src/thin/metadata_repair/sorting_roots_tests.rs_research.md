# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair/sorting_roots_tests.rs

This file tests `compare_time_counts()` from metadata repair.

Covered cases:
- Empty left versus non-empty right sorts after right.
- Non-empty left versus empty right sorts before right.
- Two empty maps compare equal.
- Greater newest time on left sorts before right.
- Greater newest time on right sorts after right.
- Equal time but greater count on left sorts before right.
- Equal time but greater count on right sorts after right.

Interactions:
- Uses `super::*` to test private sorting behavior.
- Supports candidate ordering in `find_root_pairs()`.

Risks and notes:
- Tests are focused on ordering only; they do not cover full root-pair selection.
