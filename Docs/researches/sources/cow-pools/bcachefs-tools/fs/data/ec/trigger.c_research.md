# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.c

Implements stripe bkey validation/text output, stripe triggers, bucket/accounting updates, open-stripe tracking, and new-stripe bucket tracking.

Key responsibilities:
- Validates stripe key position, value size, checksum granularity, nonzero sector count, and pointer validity.
- Formats stripe keys, including algorithm, sectors, data/redundancy geometry, checksum type/granularity, disk label, `needs_reconcile`, `can_widen`, pointers, and block counts.
- Marks/unmarks stripe buckets:
  - Distinguishes data stripe buckets from parity buckets.
  - Checks parity buckets are not already dirty on insertion.
  - Validates stripe refcount/data type/sector state on deletion.
  - Updates bucket refs, `bucket_to_stripe` btree bit, stripe refcount, alloc data type, and dev counters.
- Maintains stripe backpointers for stripe pointers.
- `bch2_trigger_stripe()`:
  - Schedules stripe delete work for empty stripes.
  - Refreshes `can_widen`.
  - Deletes empty unopened stripes transactionally.
  - Updates stripe fragmentation LRU.
  - Updates reconcile high-priority work bits and reconcile accounting.
  - Updates disk accounting for parity sectors.
  - Updates bucket marks/backpointers.
  - Creates GC stripe mirror state during GC triggers.
- Allocates GC stripe memory.
- Tracks buckets involved in in-flight new stripes to avoid rebalance races.
- Tracks open stripe indices with hash tables so deletion/invalidation can skip stripes being created or rewritten.

Important interactions:
- Hooks into btree update trigger system via `bch2_bkey_ops_stripe` in `trigger.h`.
- Coordinates with `create.c` stripe handles and bucket tracking.
- Coordinates with `init.c` reference checking and device-removal safety.

Notable concerns:
- Contains comments about runtime GC assumptions needing revision if runtime GC returns.
- Correctness depends on trigger flags: transactional vs GC vs atomic paths perform different side effects.
