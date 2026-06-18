# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.h

This header exposes bucket addressing, locking, generation, usage, trigger, reservation, and lifecycle helpers.

Bucket addressing:
- `sector_to_bucket()`, `bucket_to_sector()`, `bucket_remainder()`, and `sector_to_bucket_and_offset()` convert between sectors and bucket numbers.
- Pointer helpers map extent pointers to bucket numbers/positions and GC bucket entries.

Locking and GC:
- Provides byte-sized bucket lock helpers and a `bucket_lock` guard.
- `gc_bucket()` returns the in-memory GC bucket state for a valid bucket.
- Conversion helpers copy between `struct bucket` GC state and `struct bch_alloc_v4`.

Generation:
- `bucket_gens()`, `bucket_gen()`, `bucket_gen_get_rcu()`, `bucket_gen_get()`, `gen_cmp()`, and `gen_after()` manage stale-pointer generation comparisons.

Pointer helpers:
- `ptr_data_type()` maps btree pointers to btree and extent pointers to cached/user.
- `ptr_disk_sectors()` accounts for compressed extents by scaling logical sectors to compressed disk sectors.
- `dev_ptr_stale_rcu()` / `dev_ptr_stale()` detect stale pointers by comparing pointer generation against current bucket generation.

Usage and watermarks:
- Declares device usage read/print APIs.
- `bch2_dev_buckets_reserved()` defines per-watermark bucket reserves.
- `dev_buckets_free()` and `dev_buckets_available()` compute free/available buckets after open buckets and reserves.

Triggers and marking:
- Declares pointer repair, extent trigger, reservation trigger, metadata bucket marking, superblock marking, and disk-usage application APIs.
- `trigger_run_overwrite_then_insert()` is a helper for triggers that process old and new keys separately.

Disk reservation API:
- Provides `bch2_disk_reservation_put()`, reservation flags, fast inline `bch2_disk_reservation_add()`, initialization, and get helpers.
- Defines RAII-style `disk_reservation` cleanup class.
- `avail_factor()` leaves a reserve margin when calculating available reservation space.

Lifecycle:
- Declares `bch2_buckets_nouse_alloc/free()`, `bch2_bucket_nouse()`, and per-device bucket allocation/resize/free functions.
