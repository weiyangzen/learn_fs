# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.c

Implements stripe bkey validation/text formatting, transactional/GC triggers, stripe bucket accounting, open-stripe tracking, and new-stripe bucket tracking.

Key entry points:
- `bch2_stripe_validate()` validates stripe bkey positions, value size, checksum granularity, sectors, and pointers.
- `bch2_stripe_to_text()` prints stripe geometry, label, flags, pointers, and block counts.
- `bch2_trigger_stripe()` updates LRU entries, reconcile bits/accounting, replica accounting, bucket refs, and GC stripe state.
- `bch2_ec_stripe_mem_alloc()` allocates GC stripe memory when needed.
- `bch2_stripe_handle_tryget()` / `put()` track open stripes to prevent deletion races.

Important details:
- Parity bucket marking asserts parity buckets do not already contain data and keeps dirty sectors/stripe refcount consistent.
- Transactional triggers maintain `bucket_to_stripe` btree bits and bucket backpointers.
- Empty stripes are converted to deleted keys when not open, or queued for delete work.
- `can_widen` is refreshed transactionally from current RW-member device counts.
- Hash tables track buckets participating in new stripes to avoid rebalance races.

Dependencies and interactions:
- Works with alloc accounting, LRU, replicas, backpointers, reconcile work, EC create/init structures, and recovery/fsck passes.
