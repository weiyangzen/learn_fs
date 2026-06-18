# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/create.c

Implements background erasure-code stripe creation, reuse, widening, extent-pointer updates, and degraded-stripe repair.

Key responsibilities:
- Documents EC model: foreground writes replicated normally, background work groups immutable buckets into stripes, writes parity, and atomically updates extent pointers.
- Maintains per-disk-label `ec_dev_stripe_state` for allocator striping state.
- Deletes empty stripes via stripe-fragmentation LRU and `stripe_delete_work`.
- Creates stripe keys with reconcile marking and insertion into `BTREE_ID_stripes`.
- Updates extents pointing to old data buckets:
  - Finds backpointers.
  - Verifies pointer/stripe match.
  - Drops stale stripe pointers.
  - Rewrites the data pointer to the new stripe block.
  - Inserts the new stripe pointer.
  - Drops excess replicas while preserving target durability.
  - Commits changes under no-ENOSPC/no-check-RW flags.
- Uses logged operation `logged_op_stripe_update` so extent updates can resume after interruption.
- Finalizes stripe creation by validating old stripe data, reusing old blocks if applicable, generating parity/checksums, writing moved data/parity blocks, committing stripe key/logged op, then updating extents.
- Holds device write iorefs while committing stripes to avoid racing device removal.
- Allocates EC devices by disk label/target, bucket size, durability, and active RW devices.
- Computes and caches stripe widening eligibility (`can_widen`) from RW member counts.
- Allocates new stripe structures and bucket sets, including parity/data bucket allocation and shrink/fallback behavior when allocation is blocked.
- Reuses old fragmented stripes when full-stripe allocation is unavailable.
- Manages stripe indices, open stripe handles, pending creation lists, and stripe heads keyed by disk label/algo/redundancy/watermark.
- Provides `bch2_ec_stripe_head_get()` for allocator integration.
- Repairs degraded stripes by evacuating blocks if necessary or creating a replacement stripe, reading old data, allocating new buckets, and queueing creation.

Important interactions:
- Central to EC write integration with allocator, copygc, moving context, btree logged ops, backpointers, reconcile state, and EC I/O.
- Uses `bch2_ec_generate_ec()`, `bch2_ec_generate_checksums()`, `bch2_ec_block_io()`, and `bch2_stripe_buf_read()` from `io.c`.
- Uses trigger-side open-stripe/bucket tracking to prevent deletion/rebalance races.
- Uses `bch2_bkey_set_needs_reconcile()` to keep reconcile subsystem aware of stripe and extent changes.

Notable concerns:
- Stripe creation carefully handles device removal races; stale copied pointers to removing devices are rejected before commit.
- Reuse path cannot yet repair invalid blocks directly during reuse; comments note needed backpointer-update codepath.
- If insufficient devices remain, allocator is expected to fall back to replication.
- Stripe index allocation scans slots and has a comment noting need for a future free-stripe bitrange btree.
