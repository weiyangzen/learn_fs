# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/background.c

This file implements persistent allocation-key handling, bucket state transitions, derived allocation indexes, device capacity bookkeeping, and allocator membership changes. It also contains extensive design documentation for buckets, foreground/background allocation, watermarks, accounting, replicas, backpointers, disk groups, and recovery passes.

Alloc key format handling:
- Converts legacy alloc key versions v1-v3 into `struct bch_alloc_v4`.
- Validates alloc v1-v4 keys, including value size, backpointer layout, derived data type, IO times, and sector/type consistency.
- Provides text formatting and byte-swapping for alloc v4.
- Provides mutable conversion helpers used when updating alloc keys inside transactions.

Bucket generation support:
- `bch2_bucket_gens_init()` builds packed `bucket_gens` btree keys from alloc keys.
- `bch2_alloc_read()` reads either `bucket_gens` or alloc keys at mount to populate each device’s in-memory generation array.

Derived index maintenance:
- `bch2_bucket_do_freespace_index()` inserts/removes free-bucket entries in the freespace btree.
- `bch2_bucket_do_discard_index()` maintains the need-discard btree through the write buffer.
- `bch2_bucket_gen_update()` updates packed bucket generation records.
- `bch2_alloc_key_to_dev_counters()` emits `dev_data_type` accounting deltas when bucket data type, sectors, or fragmentation changes.

Main trigger:
- `bch2_trigger_alloc()` is the central alloc-key trigger. In transactional mode it normalizes data type, handles nonempty-to-empty transitions, sets need-discard/need-inc-gen state, validates free transitions, repairs dirty free bookkeeping, updates freespace/need-discard/LRU/bucket-gens indexes, and updates device counters.
- In atomic mode it records journal sequence transitions, updates in-memory bucket generation arrays, wakes allocators on new free buckets, queues fast discard, triggers invalidation/copygc-related work, and schedules async GC-gens handling.
- In GC insert mode it seeds GC bucket state.

Device/capacity lifecycle:
- `bch2_dev_remove_alloc()` clears LRU, need-discard, freespace, backpointer, bucket-gens, alloc, and usage data for a removed device.
- `bch2_bucket_io_time_reset()` updates read/write IO time for a bucket.
- `bch2_recalc_capacity()` computes usable filesystem capacity from RW durable devices after reserves.
- `bch2_dev_allocator_set_rw()`, `bch2_dev_allocator_remove()`, and `bch2_dev_allocator_add()` maintain per-data-type RW device bitmaps and wake blocked allocators.
- `bch2_fs_capacity_init()` / `bch2_fs_capacity_exit()` manage capacity percpu state and the mark lock.

Correctness notes:
- Alloc state is derived from counters and flags; `alloc_data_type_set()` is called to normalize potentially stale stored values.
- Need-discard indexing depends on journal sequence assignment, so part of the work is deferred to the atomic trigger phase.
- Free buckets with stale discard/journal bookkeeping are repaired by walking them back to need-discard or clearing stale sequence fields.
