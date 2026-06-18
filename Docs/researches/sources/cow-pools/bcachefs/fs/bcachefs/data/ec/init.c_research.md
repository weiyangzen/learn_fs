# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.c

Handles EC startup/shutdown, device removal invalidation, stripe flushing, and stripe-reference consistency checks.

Key entry points:
- `bch2_invalidate_stripe_to_dev()` marks a removed device pointer invalid in stripe keys and adjusts replica accounting.
- `bch2_dev_remove_stripes()` walks bucket-to-stripe refs for a device.
- `bch2_fs_ec_stop()` and `bch2_ec_stop_dev()` cancel in-flight stripes.
- `bch2_fs_ec_flush()` and `bch2_fs_ec_flush_outstanding()` wait for committed/in-flight stripe work.
- `bch2_check_stripe_refs()` repairs/checks stripes-to-buckets and bucket-to-stripe references.

Important details:
- Device invalidation refuses operations that would degrade or lose data unless force flags allow it.
- Teardown frees stripe heads, dev stripe state, workqueue, and EC bioset, asserting no pending stripe_new entries.
- Flush-outstanding waits only for stripe_new entries that already reached commit-ready sequence numbers.
- Reference checking repairs missing `bucket_to_stripe` bits and removes refs to missing or mismatched stripes.

Dependencies and interactions:
- Works with alloc accounting, LRU, replicas, write buffer, EC create/trigger helpers, and reconcile triggers.
