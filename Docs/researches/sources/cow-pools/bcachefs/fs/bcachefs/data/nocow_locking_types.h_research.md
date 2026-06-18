# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking_types.h

## Role

`nocow_locking_types.h` defines the no-COW bucket lock table layout.

## Constants

- `BUCKET_NOCOW_LOCKS_BITS = 10`
- `BUCKET_NOCOW_LOCKS = 1024`
- `NOCOW_LOCK_BUCKET_SIZE = 6`

## Structures

- `struct nocow_lock_bucket`: waitlist, spinlock, six bucket identifiers, and six atomic lock counts; aligned to cache line size.
- `struct bucket_nocow_lock_table`: fixed array of hashed lock buckets.

## Design

This is a compact hash table rather than one lock per physical bucket. Collision handling is bounded by six slots per hash bucket.
