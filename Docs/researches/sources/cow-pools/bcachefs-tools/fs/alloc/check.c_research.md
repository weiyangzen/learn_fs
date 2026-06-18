# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/check.c

This file implements allocation-index consistency checking and initialization for the alloc, freespace, need-discard, bucket-gens, LRU, and stripe-ref derived indexes.

Alloc btree scanning:
- `bch2_get_key_or_hole()` synthesizes deleted extent-like holes for non-extent btrees so alloc holes can be checked as ranges.
- `next_bucket()` and `bch2_get_key_or_real_bucket_hole()` walk only real device bucket ranges.
- `check_btree_alloc()` iterates alloc keys and holes, committing repairs incrementally.

Alloc key checks:
- `bch2_check_alloc_key()` validates that an alloc key points to an existing device bucket.
- Verifies need-discard btree entries for `BCH_DATA_need_discard`.
- Verifies freespace btree presence/absence and generation bits for `BCH_DATA_free`.
- Verifies packed bucket-gens entries match alloc key generations.
- Recomputes stripe refcount via `bch2_bucket_nr_stripes()` and repairs mismatches.
- Invalid alloc keys for nonexistent device buckets can be deleted.

Hole checks:
- `bch2_check_alloc_hole_freespace()` ensures alloc holes for initialized devices are represented as freespace.
- `bch2_check_alloc_hole_bucket_gens()` ensures holes have zero generation values in bucket-gens.

Freespace/need-discard checks:
- `bch2_need_discard_or_freespace_err()` emits fsck errors for incorrect derived-index state.
- `__bch2_check_freespace_key()` validates a freespace entry against the alloc key, including device existence, free state, and encoded genbits.
- `delete_freespace_key()` supports synchronous repair and allocator-path asynchronous repair to avoid recursive allocation/commit.
- `bch2_check_discard_key()` verifies need-discard entries match alloc keys and `journal_seq_empty`.

Bucket-gens checks:
- `bch2_check_bucket_gens_key()` deletes keys for invalid devices/ranges and clears nonzero generations for invalid bucket slots.

Top-level passes:
- `bch2_check_alloc_info()` checks alloc-derived indexes in this order: alloc scan, need-discard btree, freespace btree, bucket-gens btree.
- `bch2_check_alloc_to_lru_refs()` ensures alloc keys with fragmentation or cached state have corresponding LRU entries, repairs cached buckets with zero read time, then checks stripe references.

Freespace initialization:
- `bch2_dev_freespace_init()` scans alloc state for a device and populates freespace/derived indexes for a bucket range, then marks the member’s freespace initialized bit.
- `bch2_fs_freespace_init()` runs initialization for any device missing that bit and writes the superblock afterward.

Correctness notes:
- Write-buffer flush tracking is used before declaring derived-index mismatches, reducing false positives from buffered updates.
- Async freespace repair returns a positive value to tell the allocator not to allocate the suspect bucket.
- The small-image feature skips filesystem freespace initialization.
