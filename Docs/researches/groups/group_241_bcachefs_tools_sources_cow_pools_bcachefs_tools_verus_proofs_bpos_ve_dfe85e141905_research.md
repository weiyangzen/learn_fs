# Group Research: group_241_bcachefs_tools_sources_cow_pools_bcachefs_tools_verus_proofs_bpos_ve_dfe85e141905

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/bcachefs-tools` is included in subset A. All three listed Verus proof files were read completely: 2,327 lines, 2,492 lines, and 1,252 lines respectively.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/bpos_verify.rs -->
# File Research: sources/cow-pools/bcachefs-tools/verus-proofs/bpos_verify.rs

## Purpose

This Verus file formalizes a large slice of bcachefs key-position reasoning. It starts with pure ordering proofs for `Bpos`, `Bkey`, and `Bversion`, then extends into extent range invariants, btree-node split/merge preservation, linear extent lookup, overwrite trimming, and snapshot-aware overwrite fragment preservation.

The file mirrors several bcachefs implementation concepts from `bch_bindgen/src/bkey.rs`, kernel btree key helpers, and extent update paths. It is both a verification harness and an executable/spec hybrid model for bpos ordering and extent mutation.

## Main Models

- `Bpos { inode: u64, offset: u64, snapshot: u32 }` is ordered lexicographically by inode, offset, then snapshot.
- `Bkey { p: Bpos, size: u32 }` models an extent ending at `p.offset`, with range `[p.offset - size, p.offset)`.
- `Bversion { hi: u32, lo: u64 }` models the two-field version stamp ordered lexicographically.
- Spec predicates define sorted `Seq<Bpos>`, valid/nonempty/nonoverlapping extent sequences, key overlap/adjacency, and overwrite fragment behavior.

## Ordering Verification

The file defines spec and exec versions of:

- `bpos_lt`, `bpos_le`, `bpos_gt`, `bpos_ge`, `bpos_cmp`, `bpos_min`, `bpos_max`
- `bkey_lt`, `bkey_le`, `bkey_cmp`, where snapshot is intentionally ignored
- `bversion_cmp`, `bversion_eq`, zero and max version sentinels

It proves reflexivity, antisymmetry, transitivity, totality, trichotomy, and comparison consistency. It also proves the intended relationship between `bkey` ordering and `bpos` ordering: `bkey` compares only inode/offset, while `bpos` refines equal bkeys by snapshot.

## Position Arithmetic

The file models `POS_MIN`, `SPOS_MAX`, and `POS_MAX`, plus successor/predecessor operations over the conceptual 160-bit tuple `(inode, offset, snapshot)`. It proves:

- minimum and maximum sentinel properties
- successor/predecessor strict ordering
- successor adds one and predecessor subtracts one in the integer interpretation
- successor/predecessor are immediate and inverse where defined
- no-snapshot successor advances in `bkey` ordering

It also verifies the optimized XOR-based equality check with bit-vector lemmas for `u64` and `u32`.

## Extent Invariants

The extent model is centered on half-open ranges. Important predicates and lemmas include:

- `key_start` and `key_end`
- `extents_valid`, `extents_nonempty`, `extents_nonoverlap`
- local non-overlap implies pairwise non-overlap
- a point can lie in at most one extent in a valid sequence
- valid nonoverlapping extents are sorted by start and end

This is the foundation for lookup correctness and btree update reasoning: the proofs establish that extent lookup is unambiguous when the sequence invariant holds.

## Trimming, Splitting, and Btree Node Operations

`cut_front_spec` and `cut_back_spec` model bcachefs extent trimming. The file proves that trimming:

- preserves validity and nonemptiness
- starts or ends exactly at the trim point
- can split an extent into adjacent non-overlapping pieces
- clears overlap on the front or back side of an inserted extent

For btree node operations, the file proves that splitting and merging preserve sorted bpos sequences and valid nonoverlapping extent sequences when pivot/boundary preconditions hold.

## Executable Verification Targets

The file includes several exec-level functions with Verus postconditions:

- `find_extent` linearly scans a vector and returns the unique extent containing a target offset, or proves no extent contains it.
- `extent_overwrite_exec` computes surviving fragments of an old extent after same-snapshot overwrite.
- `extent_insert_nonoverlap` inserts into a nonoverlapping gap while maintaining sequence invariants.
- `extent_insert` sketches the full insert/update loop that copies pre-overlap extents, trims overlaps, inserts the new extent, and copies post-overlap extents.

These functions bridge the pure proof layer to concrete vector-processing algorithms.

## Snapshot-Aware Overwrite

The later section models the snapshot-sensitive behavior of `bch2_trans_update_extent_overwrite`. Same-snapshot overwrite deletes the overlapped part of the old extent; cross-snapshot overwrite may preserve a middle fragment in the old snapshot.

Key facts proved:

- same-snapshot snapshot-aware overwrite reduces to the original overwrite model
- cross-snapshot containment produces three fragments
- cross-snapshot single-sided overlap produces two fragments
- cross-snapshot full cover produces no data fragments, with a comment noting whiteout handling is separate
- the middle fragment covers exactly the overlap region
- all snapshot fragments are valid, nonempty, within the old range, and collectively preserve coverage of the old range together with the new extent

## Important Limitations and Notes

- This is a verification model, not production code. It mirrors selected bcachefs logic rather than importing the real implementation.
- Some proof bodies are intentionally lightweight or rely on solver automation and explanatory comments.
- The model focuses on pure ordering, range arithmetic, and sequence invariants. It does not model allocation, journaling, concurrency, IO, actual btree nodes, or real snapshot whiteout records.
- The file has two `main` functions only as Verus entry points within the proof module style; no runtime behavior is intended.

## Role in the Repository

This is the largest and broadest proof file in the group. It provides core correctness facts for bcachefs key ordering and extent mutation, which are foundational for btree search, insertion, overwrite, and snapshot-aware copy-on-write behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/bpos_verify.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/eytzinger_verify.rs -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/eytzinger_verify.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/snapshot_verify.rs -->
# File Research: sources/cow-pools/bcachefs-tools/verus-proofs/snapshot_verify.rs

## Purpose

This Verus file models and verifies bcachefs snapshot ancestry invariants and the accelerated ancestor-checking algorithm. It mirrors logic from `fs/bcachefs/snapshots/snapshot.c` and `snapshot.h`, especially parent-link walking, skiplist acceleration, bitmap-range checks, and the combined `__bch2_snapshot_is_ancestor` structure.

The central structural rule is that parent snapshot IDs are greater than child IDs, so walking toward the root strictly increases IDs and terminates.

## Snapshot Model

`SnapshotEntry` contains:

- `parent: u32`
- `children: (u32, u32)`, normalized so `.0 >= .1`
- `depth: u32`
- `skip: (u32, u32, u32)`, sorted ascending

The snapshot table is modeled as `Map<u32, SnapshotEntry>`, so most of the file is spec/proof-level rather than exec-level code.

## Well-Formedness Invariants

The combined `well_formed(table)` predicate requires:

- `parent_gt_child`: non-root parent IDs are greater than child IDs
- `children_lt_self`: children have lower IDs than their parent node
- `children_normalized`: children are stored in descending order
- `no_duplicate_children`: nonzero child IDs are not duplicated
- `skiplist_sorted`: skip entries are sorted ascending
- `skiplist_ge_parent`: nonzero skip entries are at least the parent
- `skiplist_are_ancestors`: nonzero skip entries are real ancestors
- `parent_links_closed`: nonzero parents exist in the table

These invariants support termination, no-cycle reasoning, and correctness of accelerated traversal.

## Ancestor Relation

`is_ancestor(table, id, ancestor)` is recursively defined by following parent links. It is reflexive when `id == ancestor`, false for invalid direction or missing nodes, and otherwise requires `parent > id` before recursing.

The file proves:

- parent is an ancestor in one step
- ancestor transitivity
- ancestor antisymmetry
- non-self ancestry implies `id < ancestor`
- any ancestor of a node in the table is also in the table
- root nodes cannot reach any non-self target

## Index, Children, and Depth Arithmetic

The file verifies supporting arithmetic and structural facts:

- `snapshot_index(id) = U32_MAX - id` is bounded, injective, and order-reversing
- ancestors have lower reverse indices than descendants
- `normalize_children` returns a descending pair and preserves the child set
- normalization is idempotent
- depth consistency implies parents have lower depth
- depth-zero roots have no parent

## Skiplist Acceleration

`get_ancestor_below_spec(table, id, ancestor)` selects the highest skip entry not exceeding `ancestor`, falling back to the parent. The file proves the result:

- makes progress when possible
- stays bounded by `ancestor` when the parent is bounded
- is itself an ancestor of `id`

`is_ancestor_skiplist` is then proved equivalent to the linear `is_ancestor` relation through `skiplist_walk_equiv` and `ancestor_step_equiv`.

The file also proves that the kernel-style skiplist construction pattern, where a new node's skip entries are derived from its parent's parent/skip entries, preserves the "skip entries are ancestors" and "skip entries are at least parent" properties.

## Bitmap and Combined Algorithm

The constant `IS_ANCESTOR_BITMAP` is 128. The file proves bitmap index arithmetic:

- `bitmap_index(id, ancestor) = ancestor - id - 1`
- index is bounded for ancestors within 128 IDs
- distinct ancestors get distinct bitmap indices
- closer ancestors get lower indices

`bitmap_correct(table)` abstracts the runtime bitmap population invariant. The actual bit contents are not modeled; `bitmap_lookup_correct` is effectively a proof-level placeholder/axiom that the bitmap test matches `is_ancestor` when the table was built correctly.

The combined algorithm is modeled as:

1. `skiplist_phase` repeatedly applies `get_ancestor_below_spec` until the ID is close to `ancestor`, reaches zero, or passes the target.
2. `combined_is_ancestor` then uses a close-range bitmap-equivalent check or equality.

The main theorem, `combined_algorithm_correct`, proves `combined_is_ancestor(table, id, ancestor) == is_ancestor(table, id, ancestor)` under `well_formed(table)` and `bitmap_correct(table)`.

## Important Limitations and Notes

- The table is a spec `Map`, so there is no exec-level verified snapshot-table implementation.
- Bitmap bits are abstracted rather than represented concretely. Bitmap correctness is assumed through the invariant rather than derived from a modeled bit array.
- Skiplist and ancestry proofs depend on the strong invariant that nonzero skip entries are genuine ancestors.
- The proof focuses on ancestry query correctness, not snapshot mutation, persistence, locking, or reclamation.

## Role in the Repository

This file verifies the logic behind bcachefs snapshot ancestry checks. It is the group counterpart to `bpos_verify.rs`: while `bpos_verify.rs` handles key and extent ordering, this file handles the snapshot tree relation that determines copy-on-write ancestry semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/verus-proofs/snapshot_verify.rs -->