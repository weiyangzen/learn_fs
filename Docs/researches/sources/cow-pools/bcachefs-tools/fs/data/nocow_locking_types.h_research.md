# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking_types.h

## Purpose
Defines the no-COW lock table layout.

## Main Interfaces
- `BUCKET_NOCOW_LOCKS_BITS` is 10, so the table has 1024 hash buckets.
- Each `nocow_lock_bucket` has a waitlist, spinlock, six bucket ids, and six atomic counts, cacheline-aligned.
- `struct bucket_nocow_lock_table` embeds the fixed array.

## Notes
The six-entry per-hash-bucket limit is handled at runtime by waiting for an empty bucket when full.
