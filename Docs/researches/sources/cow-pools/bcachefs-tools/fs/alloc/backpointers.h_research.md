# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.h

This header defines backpointer APIs and inline conversion helpers.

Position mapping:
- `bp_pos_to_bucket()` maps a backpointer btree position to its alloc-btree bucket.
- `bp_pos_to_bucket_and_offset()` also returns the offset within the bucket.
- `bucket_pos_to_bp_noerror()` and `bucket_pos_to_bp()` map an alloc bucket plus offset into backpointer btree position space.
- `bucket_pos_to_bp_start()` and `bucket_pos_to_bp_end()` produce the scan range for a bucket’s backpointers.

Backpointer construction:
- `backpointer_btree()` selects `BTREE_ID_backpointers` or `BTREE_ID_stripe_backpointers`.
- `bch2_bkey_ptr_data_type()` maps extent/btree/stripe pointers to accounting data types.
- `bch2_extent_ptr_to_bp_pos()` computes the physical backpointer key position. Erasure-coded removed-device pointers are encoded with `bp_dev_for_ec_removed_dev()`, and stripe backpointers are positioned to avoid colliding with extent backpointers.
- `bch2_extent_ptr_to_bp()` constructs a complete `struct bkey_i_backpointer`, including owner btree, level, data type, bucket generation, bucket length, owner position, erasure-coded flag, stripe-pointer flag, and optional physical reconcile marker.

Update API:
- `bch2_bucket_backpointer_mod()` optionally updates reconcile work btrees, chooses direct or write-buffered update mode, and converts deletions into `KEY_TYPE_deleted` updates.

Scan API:
- Defines `struct bp_scan_iter`, its cleanup class, `bch2_bp_scan_iter_peek()`, `bch2_bp_scan_iter_advance()`, and the `backpointer_scan_for_each()` macro.
- The scanner supports restart-aware iteration and write-buffer flush tracking.

Other declarations:
- Backpointer bkey ops.
- Target lookup APIs.
- Bucket mismatch checking and full consistency passes.
- Bucket bitmap helpers for mismatch/empty tracking.

Role:
- This header is the shared contract between extent triggers, copygc/scrub/recovery, reconcile, and allocation checking for reverse physical-to-logical references.
