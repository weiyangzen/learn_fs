# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.h

This header defines bucket addressing, locking, generation access, pointer mapping, usage/reservation helpers, and trigger declarations.

Addressing:
- `sector_to_bucket()`, `bucket_to_sector()`, `bucket_remainder()`, and `sector_to_bucket_and_offset()` convert between sectors and bucket numbers.
- `for_each_bucket` iterates device bucket arrays.

Locking:
- `bucket_lock()` and `bucket_unlock()` implement a compact bit lock on `struct bucket`.
- `DEFINE_GUARD(bucket_lock, ...)` provides scoped locking.

GC bucket and generation access:
- `gc_bucket()` returns an in-memory GC bucket if valid.
- `bucket_gens()`, `bucket_gen()`, `bucket_gen_get_rcu()`, and `bucket_gen_get()` access packed generation arrays.
- `gen_cmp()` and `gen_after()` compare wrapping 8-bit generations.

Pointer mapping:
- `PTR_BUCKET_NR()`, `PTR_BUCKET_POS()`, `PTR_BUCKET_POS_OFFSET()`, and `PTR_GC_BUCKET()` map extent pointers to bucket state.
- `alloc_to_bucket()`, `__bucket_m_to_alloc()`, and `bucket_m_to_alloc()` convert between GC bucket state and alloc v4 state.
- `ptr_data_type()` and `ptr_disk_sectors()` classify pointers and compute compressed on-disk sectors.

Usage and capacity:
- Declares fast/full device usage reads and text rendering.
- `bch2_dev_buckets_reserved()`, `__dev_buckets_free()`, `dev_buckets_free()`, `__dev_buckets_available()`, and `dev_buckets_available()` implement watermark-based availability.
- Declares `bch2_fs_usage_read_short()`.

Trigger and marking declarations:
- Declares `bch2_bucket_ref_update()`, `bch2_check_fix_ptrs()`, extent/reservation triggers, metadata bucket marking, superblock marking, and disk usage accounting.

Disk reservations:
- `bch2_disk_reservation_put()` releases online reserved sectors.
- `bch2_disk_reservation_add()` uses a fast per-CPU path in kernel builds and falls back to the slow path when needed.
- `bch2_disk_reservation_init()` and `bch2_disk_reservation_get()` initialize and acquire reservations.
- A cleanup class releases reservations automatically.
- `RESERVE_FACTOR` and `avail_factor()` account for reservation overhead.

Lifecycle declarations include no-use bitmap management and device bucket allocation/resizing/freeing.
