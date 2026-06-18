# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.h

This header defines traversal, index conversion, search, and sort declarations for arrays in Eytzinger layout.

Concept:
- Eytzinger layout stores a binary search tree in array order.
- It improves branch prediction and prefetching relative to classic binary search over sorted arrays.
- Both one-based and zero-based variants are provided.

One-based helpers:
- Child/left/right child calculation.
- First/last inorder node.
- Next/previous inorder traversal.
- Conversion between inorder index and Eytzinger index.
- `eytzinger1_for_each`.
- Exact find with `eytzinger1_find()` and `_find_r()`.

Zero-based helpers:
- Equivalent child/traversal/conversion wrappers.
- `eytzinger0_for_each` and reverse iteration.
- Range-style searches:
  - find greatest `<=`
  - find smallest `>`
  - find smallest `>=`
- Exact find with `eytzinger0_find()` and `_find_r()`.

Sort declarations:
- `eytzinger1_sort_r()`
- `eytzinger1_sort()`
- `eytzinger0_sort_r()`
- `eytzinger0_sort()`

Important invariants:
- Debug checks are active only under `EYTZINGER_DEBUG`.
- One-based find returns `0` for not found.
- Zero-based find returns `-1` for not found.
- One-based layout can have better cacheline alignment because levels start at powers of two.

Research notes:
- This is a reusable low-level performance utility, not bcachefs-specific in concept.
