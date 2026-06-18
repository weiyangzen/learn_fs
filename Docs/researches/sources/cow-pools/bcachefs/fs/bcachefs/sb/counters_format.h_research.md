# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_format.h

This header defines the persistent counter catalog and on-disk counter field format.

Key responsibilities:
- Defines counter flag types: event counters and sector amount counters.
- Lists all persistent counters with stable numeric IDs, type flags, and help text.
- Generates runtime enum `bch_persistent_counters`.
- Generates stable on-disk enum `bch_persistent_counters_stable`.
- Defines `struct bch_sb_field_counters` as a variable-length superblock field of little-endian counter values.
- Provides a compile-time uniqueness check pattern for stable counter IDs.

Counter categories include:
- Sync/fsync and data read/write/update/promotion behavior.
- Reconcile, copygc, stripe, bucket allocation/discard, and cached pointer operations.
- B-tree cache/node operations.
- Journal reservation/write/reclaim events.
- Transaction restarts and commits.
- Write buffer flushing and accounting paths.
- Error throws.

Important invariant:
- Stable IDs are explicit and sparse so new counters can be added without changing existing on-disk positions.
