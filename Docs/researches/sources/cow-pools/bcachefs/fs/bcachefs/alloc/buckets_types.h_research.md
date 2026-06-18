# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets_types.h

This header defines compact bucket and usage data structures.

`BUCKET_LOCK_BITNR` is chosen by byte order so a bit lock fits in the first byte of `struct bucket`. The comments explain this is an intentional space optimization: fsck needs in-memory state for every bucket on every device, and not all architectures support byte-sized `xchg`.

`struct bucket` stores GC/in-memory bucket state:
- one-byte lock
- `gen_valid`
- 7-bit `data_type`
- generation
- dirty, cached, and stripe sector counters

`struct bucket_gens` stores packed per-device generation numbers under RCU, with first bucket, bucket count, and a flexible byte array.

Usage structures:
- `struct bch_dev_usage` stores bucket counts by data type.
- `struct bch_dev_usage_full` stores buckets, compressed sectors, and fragmented sectors for each data type.
- `struct bch_fs_usage_base` stores hidden, btree, data, cached, and reserved filesystem usage.
- `struct bch_fs_usage_short` stores capacity, used, and free.

`struct disk_reservation` records reserved sectors, a generation field, and replica count. These types are consumed by `buckets.c`, `background.c`, and accounting code.
