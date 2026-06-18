# File Research: sources/cow-pools/bcachefs-tools/verus-proofs/eytzinger_verify.rs

## Purpose

This Verus file verifies properties of the Eytzinger array-tree layout used by bcachefs utilities. The modeled C source is `fs/bcachefs/util/eytzinger.h`. It proves navigation facts, subtree/inorder properties, correctness of the `find_le` search backtracking trick, and bijections between Eytzinger indices and inorder positions.

The file uses 1-based tree indexing for specs and relates that to the C helpers that operate on Eytzinger layout arrays.

## Basic Tree Model

The core navigation specs are:

- `left_child(i) = 2 * i`
- `right_child(i) = 2 * i + 1`
- `parent(i) = i / 2`
- `level(i) = floor(log2(i))`, defined recursively
- `valid_node(i, size)` for `1 <= i <= size`
- `is_leaf(i, size)` when the left child is out of bounds

The file proves child parity, parent/child roundtrips, child progress, root level, valid parent relationships, and power-of-two level ranges.

## Subtree and Inorder Reasoning

`subtree_size(i, n)` recursively counts valid descendants, and `inorder_seq(i, n)` models inorder traversal as left subtree, root, right subtree. The file proves:

- leaf subtree size is one
- valid-node subtree size is positive
- small complete tree sizes for `n = 1, 2, 3`
- subtree-size additivity
- inorder sequence length equals subtree size
- root position inside the inorder sequence is after the left subtree

This establishes the conceptual bridge from the flat array layout to sorted traversal order.

## Search Path and Backtracking

The file models `eytzinger0_find_le` with:

- `search_loop(nd, n, a, search)` for the downward tree walk
- `best_right_turn(nd, n, a, search)` for the deepest node where `a[node] <= search`
- `backtrack_le(n)` for the bit trick that strips the lowest set bit, equivalent to the C `n >>= __ffs(n) + 1` recovery

It proves that:

- the search loop terminates past the tree
- `backtrack_le(search_loop(...))` equals `best_right_turn(...)`
- a nonzero best-right-turn node is valid and its value is `<= search`

## BST Semantics

The file models sorted Eytzinger data with `subtree_in_range(a, n, i, lo, hi)`, where every node in a subtree lies inside a strict `(lo, hi)` interval and recursive child bounds narrow around the current node value.

Using descendant proofs, it verifies:

- descendants stay within inherited bounds
- left/right subtree bounds narrow correctly
- search semantics in a bounded subtree
- `search_greatest`: for any descendant with value `<= search`, the best-right-turn result has value at least that descendant's value
- `find_le_correct`: the recovered search result is valid and `<= search`, or indicates no match under the modeled conditions

## Index Conversion and Bijection

The second half verifies the Eytzinger/inorder conversion helpers:

- `pow2`, `ctz`, `nsub`, and `strip_lowest_bit`
- `eytzinger1_extra(size)` for incomplete tree adjustment
- `to_inorder_raw(i, size)`
- `to_inorder(i, size)`, matching `__eytzinger1_to_inorder`
- `from_inorder(pos, size)`, matching `__inorder_to_eytzinger1`

Concrete evaluations are proved for tree sizes 1, 3, 5, and 7. The full proof then establishes:

- raw child ordering around a parent
- forward roundtrip: `from_inorder(to_inorder(i, size), size) == i`
- reverse roundtrip: `to_inorder(from_inorder(pos, size), size) == pos`
- validity of conversion results in both directions
- monotonicity of the incomplete-tree adjustment
- children remain ordered after the adjustment

## Important Limitations and Notes

- The file proves pure mathematical properties of the layout and search algorithm, not cache behavior or actual memory safety of the C implementation.
- Several early lemmas are intentionally lightweight or contain comments describing proof gaps or placeholders before later, stronger lemmas handle the real properties.
- `find_le_correct` states a compact whole-tree postcondition; the more complete greatest-element reasoning is in `search_greatest`.
- Data values are modeled as `Seq<int>` with strict BST range bounds, not as real bcachefs key objects.

## Role in the Repository

This proof file validates the nontrivial bit arithmetic behind bcachefs Eytzinger search and index conversion helpers. It is significant because the C algorithm depends on compact array indexing and bit-level backtracking that are easy to get subtly wrong.
