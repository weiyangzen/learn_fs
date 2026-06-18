# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.h

This header defines backpointer helpers, bkey ops, physical/logical position mapping, and scan support.

Bkey operations:
- Declares validation, text, and swab functions.
- `bch2_bkey_ops_backpointer` sets validation, rendering, byte-swap, and minimum value size.

Position conversion:
- `bp_pos_to_bucket()` and `bp_pos_to_bucket_and_offset()` map a backpointer btree position to an alloc bucket and bucket offset.
- `bucket_pos_to_bp_noerror()`, `bucket_pos_to_bp()`, `bucket_pos_to_bp_start()`, and `bucket_pos_to_bp_end()` map a bucket and offset range to backpointer btree positions.
- These conversions use `extent_bp_shift`, so backpointer positions can include a sub-sector discriminator.

Mutation:
- `backpointer_btree()` chooses `BTREE_ID_stripe_backpointers` for stripe pointers and `BTREE_ID_backpointers` otherwise.
- `bch2_bucket_backpointer_mod()` updates reconcile-work bits when needed, optionally bypasses the write buffer, and otherwise inserts/deletes through the buffered update path.

Pointer-to-backpointer construction:
- `bch2_bkey_ptr_data_type()` classifies btree pointers, extents, cached pointers, EC stripe pointers, and stripe data/parity.
- `bch2_extent_ptr_to_bp_pos()` computes the physical backpointer key, including special handling for removed EC devices and stripe backpointers.
- `bch2_extent_ptr_to_bp()` builds a `struct bkey_i_backpointer` from a logical key pointer, filling owner btree, level, data type, generation, physical length, and logical position; it also marks reconcile/EC/stripe flags.

Lookup/check declarations expose functions for resolving backpointers and running integrity checks.

Scan support:
- `struct bp_scan_iter` tracks btree id, current position, flush generation, progress, and a dynamic array of buffered backpointers.
- `DEFINE_CLASS(backpointer_scan_iter)` provides cleanup for scan arrays.
- `backpointer_scan_for_each` is a restart-aware macro that repeatedly peeks, processes, verifies transaction restart count, and advances.

The header also exposes bucket bitmap helpers used by backpointer mismatch recovery.
