# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.c

This file implements persistent alloc-key handling, derived indexes, alloc triggers, capacity calculation, and allocator device state transitions. It also contains extensive documentation for buckets, watermarks, accounting, replicas, backpointers, and allocator consistency.

Alloc format handling:
- Supports legacy alloc v1/v2/v3 unpacking and conversion to `bch_alloc_v4`.
- `bch2_alloc_v1_validate()`, `bch2_alloc_v2_validate()`, `bch2_alloc_v3_validate()`, and `bch2_alloc_v4_validate()` validate alloc key encodings and logical state.
- `bch2_alloc_v4_validate()` checks value size, backpointer layout, data type derivation, io time bounds, and consistency between `data_type` and sector/refcount fields.
- `bch2_alloc_to_v4()` and `bch2_alloc_to_v4_mut()` normalize alloc keys to the current fixed-layout v4 format.

Alloc update helpers:
- `bch2_trans_start_alloc_update_noupdate()` opens an alloc iterator and returns a mutable v4 key without updating it.
- `bch2_trans_start_alloc_update()` opens, mutates, and submits an alloc update in one path.

Bucket generation support:
- `bch2_bucket_gens_validate()` validates packed bucket generation keys.
- `bch2_bucket_gens_to_text()` renders generation arrays.
- `bch2_bucket_gens_init()` builds `BTREE_ID_bucket_gens` from the alloc btree.
- `bch2_alloc_read()` initializes in-memory device bucket generation arrays from `bucket_gens`, or from alloc keys for older metadata versions.

Derived indexes:
- `bch2_bucket_do_freespace_index()` maintains `BTREE_ID_freespace` entries for free buckets.
- `bch2_bucket_do_discard_index()` maintains `BTREE_ID_need_discard` entries through the write buffer.
- `bch2_bucket_gen_update()` updates a packed `bucket_gens` key when an alloc key generation changes.

Device accounting:
- `bch2_dev_data_type_accounting_mod()` submits `dev_data_type` accounting deltas.
- `bch2_alloc_key_to_dev_counters()` compares old/new alloc state and updates per-device bucket, sector, fragmentation, and unstriped counters.

Central trigger:
- `bch2_trigger_alloc()` is the alloc bkey trigger. In transactional mode it normalizes data type, handles nonempty-to-empty transitions as `need_discard`, sets io times, schedules generation increments, repairs suspicious free-state discard bookkeeping, updates freespace/LRU/bucket-gens indexes, reserves journal space for discard index updates, and updates device accounting.
- In atomic mode it records journal sequence transitions, updates in-memory bucket generation arrays, wakes allocators when buckets become free, performs fast discard when safe, updates the need-discard index, starts invalidation for cached buckets under pressure, and schedules async GC-gens work.
- In GC mode it marks GC bucket generation state.

Device removal:
- `bch2_dev_remove_need_discard()` removes need-discard keys for a device.
- `bch2_dev_remove_alloc()` deletes LRU, need-discard, freespace, backpointer, bucket-gens, alloc, and device usage accounting for a removed device.

I/O time and capacity:
- `bch2_bucket_io_time_reset()` updates bucket read/write LRU timestamps.
- `bch2_fs_ra_pages()` computes readahead from online block devices.
- `bch2_recalc_capacity()` computes filesystem capacity, reserved sectors, max bucket size, and wakes allocators.
- `bch2_min_rw_member_capacity()` returns the smallest rw member capacity.

Allocator device state:
- `bch2_dev_allocator_set_rw()` updates allocator device bitmaps by data type, respecting allowed data types and durability.
- `bch2_dev_allocator_remove()` removes a device from allocation, recalculates capacity, stops open buckets, wakes waiters, and waits for in-flight write points.
- `bch2_dev_allocator_add()` adds a device to allocation sets.
- `bch2_fs_allocator_background_init()`, `bch2_fs_capacity_init()`, and `bch2_fs_capacity_exit()` initialize and tear down allocator/capacity state.

Key invariants:
- Alloc `data_type` is derived from sector counts, stripe refcount, discard state, and generation gap.
- Free buckets must be represented in the freespace btree with encoded generation bits.
- Need-discard buckets are indexed by journal sequence and bucket identity.
- Device accounting is derived from alloc key transitions.
- Generation changes must update both persistent `bucket_gens` and in-memory bucket generation arrays.
