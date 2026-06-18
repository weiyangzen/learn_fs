# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/init.c

Implements EC startup/shutdown, device-removal invalidation, flush/wait logic, and stripe-reference fsck checks.

Key responsibilities:
- `bch2_invalidate_stripe_to_dev()` invalidates stripe pointers to a removed device, marks stripe `needs_reconcile`, updates disk accounting before/after mutation, and checks force flags for degraded/lost data.
- Skips open stripes during device removal because EC creation owns their migration; callers flush outstanding creates and retry.
- `bch2_dev_remove_stripes()` scans `bucket_to_stripe` refs for a device and invalidates referenced stripes, retrying open-stripe cases up to a fixed iteration limit.
- Stops EC creation globally or per device by canceling in-progress stripe heads that reference the stopped device.
- Flushes all pending stripes or only those commit-ready at call time using `stripe_new_seq`.
- Initializes and exits EC locks, lists, waitqueues, stripe delete work, stripe create workqueue, and block bioset.
- Checks and repairs stripe reference consistency:
  - Ensures stripe fragmentation LRU entries exist.
  - Ensures each stripe block has `bucket_to_stripe` refs.
  - Ensures each `bucket_to_stripe` ref points to an existing matching stripe.
  - Updates alloc stripe refcounts via `bucket_stripe_ref_mod()`.
- Provides `bch2_bucket_nr_stripes()`.

Important interactions:
- Works closely with EC create/open-stripe tracking to avoid invalidating stripes mid-creation.
- Uses allocation accounting, LRUs, btree bitsets, write-buffer flush coordination, and fsck repair paths.

Notable concerns:
- `bch2_stripes_read()` is currently a stub returning 0.
- Device-removal retry has a finite 10-iteration guard and reports `remove_stripes_did_not_terminate` if open stripes persist.
