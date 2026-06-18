# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.c

This file implements allocator consistency checks and repairs for alloc, freespace, need-discard, bucket-gens, LRU, and stripe references.

Hole synthesis:
- `bch2_get_key_or_hole()` returns either an actual btree key or a synthesized deleted key covering a hole.
- `bch2_get_key_or_real_bucket_hole()` skips invalid device ranges and clips holes to real bucket ranges.
- `next_bucket()` advances through member devices and valid bucket ranges.

Error reporting:
- `bch2_need_discard_or_freespace_err()` reports incorrect presence/absence in the need-discard or freespace btree and can mark errors fixable depending on caller context.

Alloc key checking:
- `bch2_check_alloc_key()` validates one alloc key against:
  - valid device/bucket existence
  - need-discard index presence and journal sequence
  - freespace index presence and generation bits
  - bucket-gens packed generation value
  - stripe refcount from actual stripe references
- It repairs indexes and alloc key fields when fsck policy allows.

Alloc holes:
- `bch2_check_alloc_hole_freespace()` ensures holes in the alloc btree are represented in the freespace btree.
- `bch2_check_alloc_hole_bucket_gens()` ensures bucket-gens entries for alloc holes are zero.

Freespace and discard key checking:
- `__bch2_check_freespace_key()` validates a freespace entry against the corresponding alloc key and generation bits. In async allocator context it queues repair work instead of committing recursively.
- `bch2_check_discard_key()` validates need-discard entries against alloc key data type and `journal_seq_empty`.
- `delete_freespace_key()` supports synchronous or async deletion/repair.
- `check_discard_freespace_key_work()` runs async repair work.

Bucket-gens checking:
- `bch2_check_bucket_gens_key()` removes bucket-gens keys for invalid devices/ranges and zeros generation bytes for invalid buckets outside the usable member range.

Full alloc-info pass:
- `check_btree_alloc()` walks alloc keys and synthesized holes with companion iterators for need-discard, freespace, and bucket-gens.
- `bch2_check_alloc_info()` runs alloc/hole checking, then scans need-discard, freespace, and bucket-gens btrees directly.

LRU and stripe checks:
- `bch2_check_alloc_to_lru_ref()` ensures alloc keys that should have fragmentation or cached-read LRU entries do have them. It repairs cached buckets with zero read time.
- `bch2_check_alloc_to_lru_refs()` walks the alloc btree, checks LRU references, and then calls `bch2_check_stripe_refs()`.

Freespace initialization:
- `dev_freespace_init_iter()` initializes freespace entries from alloc keys or alloc holes.
- `bch2_dev_freespace_init()` scans a device’s bucket range, populates freespace, and marks the member’s freespace initialized flag.
- `bch2_fs_freespace_init()` initializes any member device lacking freespace initialization during mount, except for small-image filesystems, and writes the superblock after completion.

Key invariants:
- Free alloc buckets must appear in the freespace btree with matching generation bits.
- Need-discard alloc buckets must appear in the need-discard btree at a key derived from `journal_seq_empty` and bucket id.
- `bucket_gens` must match alloc key generations for real buckets and be zero for alloc holes/invalid buckets.
- Alloc stripe refcounts must match stripe-tree references.
- Online allocator-path repair avoids recursive allocation commits by using async work.
