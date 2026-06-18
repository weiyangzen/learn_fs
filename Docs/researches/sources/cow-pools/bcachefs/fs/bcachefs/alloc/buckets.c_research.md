# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.c

This file implements bucket usage reads, pointer marking, extent/reservation triggers, metadata bucket marking, disk reservations, and bucket memory allocation.

Usage reads:
- `bch2_dev_usage_read_fast()` reads per-data-type bucket counts.
- `bch2_dev_usage_full_read_fast()` reads full per-device per-CPU usage counters.
- `bch2_fs_usage_read_short()` returns capacity, used, and free sectors after hidden usage and reserved-space factors.
- `bch2_dev_usage_to_text()` renders bucket/sectors/fragmented tables.

Pointer validation and repair:
- `bch2_check_fix_ptr()` validates an extent pointer against device existence, bucket validity, GC bucket generation, data type compatibility, and EC stripe metadata. It can mark pointers to drop, stripe metadata to drop, or generations to reset.
- `bch2_no_valid_pointers_repair()` handles extents without valid dirty pointers, converting a good cached pointer to dirty when possible or marking the key with an error.
- `bch2_check_fix_ptrs()` applies pointer repairs to extents during offline/recovery checking. It updates btree roots specially and avoids running on a read-write filesystem.

Bucket reference updates:
- `bch2_bucket_ref_update()` checks pointer generation ordering, stale cached/dirty pointers, data type mismatch, and sector count overflow, then adjusts bucket sector counters. Serious inconsistencies schedule `check_allocations`.

Transaction usage accounting:
- `bch2_trans_account_disk_usage_change()` applies a transaction’s aggregate filesystem usage delta to per-CPU usage counters and consumes disk reservations. It warns if disk usage increased beyond reserved sectors.

Extent triggers:
- `bch2_trigger_pointer()` handles a single decoded extent pointer. In transactional mode it updates the alloc key and backpointer btree; in GC mode it updates GC bucket state and device counters. It handles EC removed-device sentinel pointers and stripe backpointers separately.
- `bch2_trigger_stripe_ptr()` updates stripe block counts and replicas accounting for erasure-coded pointers in both transactional and GC modes.
- `__trigger_extent()` drives all pointers in an extent or btree pointer, updates replicas accounting, snapshot accounting, compression accounting, btree metadata accounting, and per-inode fragmentation accounting.
- `bch2_trigger_extent()` skips work when pointer payloads are unchanged, runs repair mode when requested, sets reconcile needs for new extent inserts, applies overwrite/insert triggers, and invokes reconcile triggers.

Reservation trigger:
- `bch2_trigger_reservation()` accounts `KEY_TYPE_reservation` sectors in `persistent_reserved`, keyed by replica count.

Metadata marking:
- `bch2_trans_mark_metadata_bucket()` marks superblock and journal buckets either transactionally or during GC.
- `bch2_trans_mark_dev_sb()` and `bch2_trans_mark_dev_sbs_flags()` mark all superblock and journal buckets for devices.
- `bch2_is_superblock_bucket()` checks whether a bucket overlaps primary/backup superblock regions or journal buckets.

Disk reservations:
- `__bch2_disk_reservation_add()` and `disk_reservation_recalc_sectors_available()` maintain fast per-CPU reservation caches backed by an atomic global available-sector count.
- Reservation flags support nofail and partial reservations.

Bucket memory lifecycle:
- `bch2_buckets_nouse_alloc()` and `bch2_buckets_nouse_free()` manage bitmaps of buckets unavailable for allocation.
- `bch2_dev_buckets_resize()` allocates/resizes per-device `bucket_gens`, copies old generations, resizes backpointer mismatch bitmaps, and publishes through RCU.
- `bch2_dev_buckets_alloc()` allocates per-device usage counters and bucket generation storage.
- `bch2_dev_buckets_free()` frees bucket generation, no-use bitmap, and usage counters.

Key invariants:
- Extent triggers are the bridge from logical extent changes to alloc counters, backpointers, replicas accounting, compression stats, and inode stats.
- Bucket sector counters must not overflow and must match pointer generation/data type rules.
- Metadata buckets may only be free, superblock, or journal type.
- Disk usage increases must be covered by reservations except for forced correction paths.
