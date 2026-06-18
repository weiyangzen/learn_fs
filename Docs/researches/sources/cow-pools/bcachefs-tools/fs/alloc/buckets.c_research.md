# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.c

This file implements bucket usage reads, pointer validation/repair, extent/reservation triggers, metadata bucket marking, disk reservations, and per-device bucket memory lifecycle.

Usage APIs:
- `bch2_dev_usage_read_fast()` sums only bucket counts across per-cpu usage arrays.
- `bch2_dev_usage_full_read_fast()` sums full per-device usage.
- `bch2_fs_usage_read_short()` computes capacity/used/free from base usage plus online reservations.
- `bch2_dev_usage_to_text()` prints per-data-type bucket, sector, and fragmentation counters.

Pointer checking and repair:
- `bch2_check_fix_ptr()` validates device existence, bucket validity, alloc key presence, pointer generation, stale dirty/cached pointer rules, bucket data-type compatibility, and erasure-code stripe consistency.
- Repairs can drop invalid pointers, drop EC stripe references, reset pointer generations, or mark bkeys as errors.
- `bch2_no_valid_pointers_repair()` can promote a good cached pointer to dirty during allocation repair, otherwise replaces the extent with a no-valid-pointers error key.
- `bch2_check_fix_ptrs()` applies these repairs for a bkey during recovery.

Bucket reference accounting:
- `bch2_bucket_ref_update()` validates generation and type compatibility, handles stale cached pointers, detects sector count overflow, and updates bucket sector counters.
- `bch2_trans_account_disk_usage_change()` applies accumulated filesystem usage deltas to percpu capacity state and enforces that positive usage growth was backed by disk reservation.

Extent trigger:
- `bch2_trigger_pointer()` updates alloc bucket counters and backpointers for each physical pointer, with separate transactional and GC paths.
- `bch2_trigger_stripe_ptr()` updates stripe block counts and replicas accounting for erasure-coded data.
- `__trigger_extent()` emits replicas, snapshot, compression, btree, and inum accounting deltas while invoking pointer/stripe triggers.
- `bch2_trigger_extent()` handles overwrite-then-insert semantics, avoids work when pointers are unchanged, and integrates reconcile triggers.

Reservation trigger:
- `bch2_trigger_reservation()` updates `persistent_reserved` accounting for `KEY_TYPE_reservation`.

Metadata marking:
- Marks superblock and journal buckets in alloc state during transactional or GC paths.
- Detects conflicting metadata/data bucket types.
- `bch2_trans_mark_dev_sbs_flags()` initializes devices and marks all superblock/journal buckets.

Disk reservations:
- Fast percpu reservation path in `bch2_disk_reservation_add()`, with slow-path recalculation through `__bch2_disk_reservation_add()` and `disk_reservation_recalc_sectors_available()`.
- Maintains `sectors_available` and `online_reserved`.

Lifecycle:
- Allocates/frees `buckets_nouse`, per-device usage percpu arrays, bucket generation arrays, and resizes bucket generation/mismatch bitmaps on device resize.
