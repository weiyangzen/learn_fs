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
