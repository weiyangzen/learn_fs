# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/buckets_types.h

This header defines compact bucket and usage data structures.

Bucket lock note:
- `struct bucket` must stay small because fsck/recovery can need one in-memory entry per bucket on every device.
- The lock is packed into one byte, with endian-dependent `BUCKET_LOCK_BITNR` ensuring bit operations affect that byte portably.

Structures:
- `struct bucket`
  - Packed GC/recovery bucket state: lock, generation-valid flag, data type, generation, dirty sectors, cached sectors, stripe sectors.
- `struct bucket_gens`
  - RCU-managed per-device bucket generation array, including first usable bucket and sizing metadata.
- `struct bch_dev_usage`
  - Bucket counts by `BCH_DATA_*` type.
- `struct bch_dev_usage_full`
  - Per-data-type buckets, sectors, and fragmented sectors.
- `struct bch_fs_usage_base`
  - Aggregate hidden, btree, data, cached, and reserved sectors.
- `struct bch_fs_usage_short`
  - User-facing capacity, used, and free values.
- `struct disk_reservation`
  - Reservation sectors, generation field, and replica count.

Role:
- These structures are shared by allocation triggers, GC, capacity accounting, and user-visible filesystem/device usage reporting.
