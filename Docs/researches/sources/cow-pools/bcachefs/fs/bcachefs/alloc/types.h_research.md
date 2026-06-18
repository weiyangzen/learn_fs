# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/types.h

Core allocator/discard type declarations.

Defines:
- `enum bch_watermark` and watermark bit constants.
- Open bucket limits: `OPEN_BUCKETS_COUNT`, write point hash/count constants.
- `open_bucket_idx_t`, with index 0 reserved as invalid/sentinel.
- `struct open_bucket`, tracking one active allocation bucket, pin count, hash/freelist links, data type, EC attachment, sectors free, generation, and fast-discard flag.
- `struct open_buckets`, a small array of open bucket indices.
- `struct dev_stripe_state`, per-write-point weighted allocation clocks and cached device mask.
- Write point state enum and `struct write_point`, including allocation state, open buckets, per-device stripe allocation state, write lists, state timing, and index update work.
- `struct write_point_specifier`.
- Filesystem capacity structures with atomic/percpu usage and mark lock.
- `struct bch_fs_allocator`, containing RW device masks, freelists, waitlists, open buckets, partial buckets, write points, and special btree/reconcile write points.
- `discard_in_flight`, `discard_release`, `discard_state`, and `struct bch_fs_discards`.

Purpose:
- Central shared type layer for foreground allocation, discard processing, capacity accounting, and write point management.

Notable invariants:
- Open bucket index 0 is sentinel.
- `dev_stripe_state` comments describe weighted fair allocation by virtual clock increments inverse to free space.
- `discard_in_flight` stores `struct bch_dev *ca` so completion/removal races do not need to recover the device from `c->devs`.
