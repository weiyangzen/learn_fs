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
