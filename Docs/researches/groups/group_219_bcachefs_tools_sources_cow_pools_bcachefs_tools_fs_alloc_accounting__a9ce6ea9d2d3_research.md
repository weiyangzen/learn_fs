# Group Research: group_219_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_alloc_accounting__a9ce6ea9d2d3

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.c

This file implements bcachefs disk accounting: persistent accounting keys in the accounting btree plus fast in-memory percpu counters indexed by sorted/Eytzinger `struct bpos` accounting positions.

Core responsibilities:
- Defines accounting type strings and expected counter counts from `BCH_DISK_ACCOUNTING_TYPES()`.
- Builds accounting btree keys from `struct disk_accounting_pos` and counter deltas.
- Implements `bch2_disk_accounting_mod()`, which queues normal accounting updates in `trans->accounting` and applies GC-mode updates directly to in-memory accounting.
- Maintains superblock replica entries for accounting keys that represent replicas, via `bch2_accounting_update_sb()`.
- Validates, byte-swaps, and prints `KEY_TYPE_accounting` keys.
- Owns the in-memory accounting table lifecycle, insertion, GC shadow counters, cleanup, and readout APIs.
- Reconstructs accounting from the accounting btree plus journal overlay during mount/recovery.

Important mechanisms:
- Persistent accounting updates are deltas, not replacement values. The btree write buffer or journal replay later accumulates them into the accounting btree.
- Every accounting delta gets a unique `bversion` derived from journal sequence and offset; replay uses this to avoid applying stale deltas.
- In-memory counters use `struct accounting_mem_entry`, with `v[0]` for live counters and `v[1]` for GC verification counters.
- `bch2_accounting_read()` merges btree accounting keys and journal accounting keys in key order, drops overwritten journal entries, accumulates same-position deltas, sorts the in-memory table, then runs fixups.
- `accounting_read_mem_fixups()` removes zero/invalid entries, validates device references, populates filesystem usage and per-device usage percpu counters, and schedules allocation checking if counter underflow is detected.
- `bch2_gc_accounting_start()` allocates GC counter arrays and `bch2_gc_accounting_done()` compares rebuilt GC accounting against live counters, optionally committing correction deltas.

External interfaces:
- `bch2_disk_accounting_mod()`
- `bch2_mod_dev_cached_sectors()`
- `bch2_accounting_update_sb()`
- `bch2_fs_replicas_usage_read()`
- `bch2_fs_accounting_read()`
- `bch2_fs_accounting_read_key()`
- `bch2_gc_accounting_start()` / `bch2_gc_accounting_done()`
- `bch2_accounting_read()`
- `bch2_dev_usage_remove()` / `bch2_dev_usage_init()`
- `bch2_verify_accounting_clean()`
- `bch2_accounting_gc_free()` / `bch2_fs_accounting_exit()`

Correctness notes:
- Replica accounting keys are normalized by sorting device IDs.
- In-memory accounting insertion may request `btree_insert_need_mark_replicas` if a replicas entry is not yet marked in the superblock.
- Zero replicas accounting entries can remove now-unused replica entries from the superblock, gated by metadata-version compatibility.
- Invalid device accounting can be repaired by negating the current counters and committing a removal delta.
- Startup accounting intentionally resets prior in-memory state because recovery can rewind and rerun with different repaired topology.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.h

This header provides the inline API and public declarations for disk accounting.

Key inline helpers:
- `bch2_u64s_neg()` negates an array of counters in place.
- `bch2_accounting_counters()` derives the counter count from the accounting key value size.
- `bch2_accounting_key_is_zero()` checks whether all counters are zero.
- `bch2_accounting_accumulate()` adds one accounting value into another and preserves the newer `bversion`.
- `fs_usage_data_type_to_base()` maps data-type usage into aggregate filesystem usage buckets: btree, data, cached.
- `bpos_to_disk_accounting_pos()` and `disk_accounting_pos_to_bpos()` map between the structured accounting key and the opaque btree position, with endian handling.
- `disk_accounting_key_init()` and `bch2_disk_accounting_mod2()` are convenience macros for constructing typed accounting positions and submitting deltas.

In-memory accounting:
- `bch2_accounting_is_mem()` excludes accounting types that are not maintained in the fast in-memory table, currently `snapshot` and `inum`.
- `bch2_accounting_mem_mod_locked()` is the central commit-path in-memory updater. For normal updates it also accumulates `trans->fs_usage_delta` and per-device percpu usage.
- `bch2_accounting_mem_add()` wraps the updater under `capacity.mark_lock`.
- `bch2_accounting_mem_read_counters()` and `bch2_accounting_mem_read()` provide indexed and position-based reads.

Transaction integration:
- `journal_pos_to_bversion()` converts a transaction journal reservation plus accounting-buffer offset into the unique accounting version.
- `bch2_accounting_trans_commit_hook()` assigns that version and applies the accounting delta to memory unless `BCH_TRANS_COMMIT_skip_accounting_apply` is set.
- `bch2_accounting_trans_commit_revert()` negates and reapplies an accounting update to undo in-memory effects on commit failure.

Declared operations cover validation/printing, superblock updates, accounting readout, GC verification, device usage initialization/removal, clean verification, and shutdown.

Correctness notes:
- `bch2_accounting_mem_mod_locked()` loops until the accounting position exists, inserting if necessary.
- GC-mode accounting updates are ignored when `gc_running` is false.
- Per-device hidden usage is increased for `BCH_DATA_sb` and `BCH_DATA_journal` by bucket size, not by live sectors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_format.h

This header defines the on-disk format for `KEY_TYPE_accounting` values and accounting key positions.

Format model:
- The accounting btree key position is a `struct disk_accounting_pos`, a type-tagged union overlaid on `struct bpos`.
- The value is `struct bch_accounting`, a flexible array of `__u64 d[]` counters.
- Updates stored through the write buffer are deltas. The persistent btree value becomes the accumulated counter value after write-buffer flush or journal replay.
- Accounting key `bversion` is a replay ordering marker derived from journal position, allowing journal replay to determine which deltas are newer than the btree value.

Data types:
- `BCH_DATA_TYPES()` defines bucket/data categories: free, superblock, journal, btree, user, cached, parity, stripe, need-gc-gens, need-discard, unstriped.
- `data_type_is_empty()` treats free, need-gc-gens, and need-discard as empty bucket states.
- `data_type_is_hidden()` marks superblock and journal as hidden usage.

Accounting types:
- `nr_inodes`: one counter, total filesystem inode count.
- `persistent_reserved`: one counter, reservation sectors by replica count.
- `replicas`: one counter, usage by replicas entry.
- `dev_data_type`: three counters, per-device bucket count, sectors, and fragmentation.
- `compression`: three counters, extent count, uncompressed size, compressed size.
- `snapshot`: one counter, per-snapshot on-disk usage.
- `btree`: three counters, btree sectors, node count, non-leaf node count.
- `rebalance_work`: one counter.
- `inum`: three counters, extent count, logical extent sectors, on-disk sectors.
- `reconcile_work`: two counters.
- `dev_leaving`: one counter.

Important constraints:
- `BCH_ACCOUNTING_MAX_COUNTERS` is 3, and all accounting types must fit that limit.
- The `disk_accounting_pos` layout is packed and must remain exactly the size of `struct bpos`.
- Adding accounting types extends the type-tagged key space without changing the btree schema.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_types.h

This small header defines the in-memory accounting structures.

Structures:
- `struct accounting_mem_entry`
  - `pos`: accounting key position, matching `disk_accounting_pos_to_bpos()`.
  - `bversion`: latest version seen for the accounting key.
  - `nr_counters`: number of counters for this entry.
  - `v[2]`: percpu counter arrays. `v[0]` is live accounting; `v[1]` is used during GC accounting verification.
- `struct bch_accounting_mem`
  - `k`: dynamic array of `accounting_mem_entry`.
  - `gc_running`: whether GC shadow counters are currently allocated/active.

Role:
- This is the backing storage for the fast in-memory accounting table managed by `accounting.c`.
- Entries are sorted with Eytzinger layout for fast lookup by accounting position.
- Counter arrays are percpu, enabling low-contention commit-path updates and cheap aggregate reads.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/background.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/background.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/background.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/background.h

This header exposes allocator background helpers, alloc key operations, and bucket-state derivation logic.

Bucket position helpers:
- `bch2_dev_bucket_exists()` checks whether a `(dev,bucket)` position maps to an existing bucket.
- `bucket_to_u64()` and `u64_to_bucket()` encode/decode bucket positions for auxiliary indexes.

Generation and data-type helpers:
- `BUCKET_GC_GEN_MAX` is the allowed generation gap before a bucket needs GC-gens.
- `alloc_gc_gen()` computes `gen - oldest_gen`.
- `bucket_data_type()` normalizes cached and stripe to user for bucket-type compatibility.
- `bucket_data_type_mismatch()` detects incompatible live data types in the same bucket.
- `data_type_movable()` marks btree, user, and stripe as movable data types.

Sector helpers:
- `bch2_bucket_sectors_total()`, `bch2_bucket_sectors_dirty()`, `bch2_bucket_sectors()`, `bch2_bucket_sectors_fragmented()`, and `bch2_bucket_sectors_unstriped()` derive accounting quantities from `bch_alloc_v4`.

State derivation:
- `alloc_data_type()` derives bucket state from stripe refcount, dirty/stripe sectors, cached sectors, sticky need-discard, and generation gap.
- `alloc_data_type_set()` writes the derived state back to the alloc key.

Auxiliary btree helpers:
- `alloc_lru_idx_read()` and `alloc_lru_idx_fragmentation()` compute LRU keys.
- `alloc_freespace_genbits()` and `alloc_freespace_pos()` encode generation bits into freespace positions.
- `alloc_gens_pos()` and `bucket_gens_pos_to_alloc()` map alloc buckets to packed bucket-gens keys.

Alloc v4 helpers:
- `alloc_v4_u64s_noerror()`, `alloc_v4_u64s()`, `set_alloc_v4_u64s()`, and `alloc_v4_backpointers()` describe alloc v4 value sizing and inline backpointer location.
- Declares bkey ops for alloc v1-v4 and bucket-gens.

Role:
- This is the shared inline contract for allocation triggers, freespace checking, bucket generation maintenance, LRU updates, and capacity/device allocator state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/background.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.c

This file implements backpointer validation, lookup, update, bidirectional consistency checking, and repair.

Basic operations:
- Validates `KEY_TYPE_backpointer` values for legal btree level and non-invalid device.
- Formats backpointers with bucket, offset, owner btree/level, data type, length, generation, and flags.
- Byte-swaps backpointer values.
- `extent_matches_bp()` regenerates expected backpointers for all decoded pointers in a target key and compares them with a stored backpointer.

Backpointer updates:
- `bch2_bucket_backpointer_mod_nowritebuffer()` performs direct insert/delete with consistency checks.
- Normal updates go through the write-buffer path defined in `backpointers.h`.
- Insert/delete anomalies schedule `check_extents_to_backpointers` unless that recovery pass is already planned.

Lookup:
- `bch2_backpointer_get_key()` and `bch2_backpointer_get_node()` resolve a backpointer to the extent or btree node it references.
- Missing or mismatched targets are handled by `backpointer_target_not_found()`, which can delete stale backpointers and accounts for write-buffer races.

Recovery passes:
- `bch2_check_btree_backpointers()` verifies every backpointer has a valid device and alloc key.
- `bch2_check_extents_to_backpointers()` first compares bucket sector totals from backpointers with alloc counters, marks mismatching buckets, then scans relevant extent/btree data to recreate or fix missing backpointers.
- `bch2_check_backpointers_to_extents()` scans backpointers and verifies each resolves to a matching extent or btree node, pinning chunks of btree nodes when the full set cannot fit in memory.

Repair behavior:
- Missing backpointers can be inserted.
- Stale backpointers can be deleted.
- Duplicate backpointers are analyzed by resolving the other owner. If one owner has a stale device pointer, it is dropped.
- If two leaf extents reference overlapping physical space and both checksums verify, the overlapping region can be converted to a shared reflink representation instead of discarding data.
- If checksum verification shows one duplicate physical reference is bad, that replica is dropped.
- Some duplicate non-leaf or otherwise unhandled cases return `fsck_repair_unimplemented`.

Performance and memory:
- Bucket mismatch bitmaps avoid full bidirectional scans when backpointer sector counts match alloc counters.
- The scanner batches backpointers into memory, sorts by owner position in reverse order, and refreshes buffered entries after write-buffer flushes.
- Multi-pass scans are used when the btree nodes needed for verification exceed the configured fsck memory budget.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.h

This header defines backpointer APIs and inline conversion helpers.

Position mapping:
- `bp_pos_to_bucket()` maps a backpointer btree position to its alloc-btree bucket.
- `bp_pos_to_bucket_and_offset()` also returns the offset within the bucket.
- `bucket_pos_to_bp_noerror()` and `bucket_pos_to_bp()` map an alloc bucket plus offset into backpointer btree position space.
- `bucket_pos_to_bp_start()` and `bucket_pos_to_bp_end()` produce the scan range for a bucket’s backpointers.

Backpointer construction:
- `backpointer_btree()` selects `BTREE_ID_backpointers` or `BTREE_ID_stripe_backpointers`.
- `bch2_bkey_ptr_data_type()` maps extent/btree/stripe pointers to accounting data types.
- `bch2_extent_ptr_to_bp_pos()` computes the physical backpointer key position. Erasure-coded removed-device pointers are encoded with `bp_dev_for_ec_removed_dev()`, and stripe backpointers are positioned to avoid colliding with extent backpointers.
- `bch2_extent_ptr_to_bp()` constructs a complete `struct bkey_i_backpointer`, including owner btree, level, data type, bucket generation, bucket length, owner position, erasure-coded flag, stripe-pointer flag, and optional physical reconcile marker.

Update API:
- `bch2_bucket_backpointer_mod()` optionally updates reconcile work btrees, chooses direct or write-buffered update mode, and converts deletions into `KEY_TYPE_deleted` updates.

Scan API:
- Defines `struct bp_scan_iter`, its cleanup class, `bch2_bp_scan_iter_peek()`, `bch2_bp_scan_iter_advance()`, and the `backpointer_scan_for_each()` macro.
- The scanner supports restart-aware iteration and write-buffer flush tracking.

Other declarations:
- Backpointer bkey ops.
- Target lookup APIs.
- Bucket mismatch checking and full consistency passes.
- Bucket bitmap helpers for mismatch/empty tracking.

Role:
- This header is the shared contract between extent triggers, copygc/scrub/recovery, reconcile, and allocation checking for reverse physical-to-logical references.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.h -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets_types.h -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/buckets_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/check.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/check.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/check.h

This header declares allocation consistency-check and freespace initialization APIs.

Exports:
- `bch2_need_discard_or_freespace_err()` reports incorrect freespace or need-discard derived-index state.
- `need_discard_or_freespace_err()` and `need_discard_or_freespace_err_on()` wrap that helper in fsck error handling macros.
- `__bch2_check_freespace_key()` validates one freespace btree position against alloc state, returning both bucket generation and optional `journal_seq_empty`.
- `bch2_check_freespace_key_async()` is the allocator-path wrapper that uses `FSCK_ERR_NO_LOG` and no write-buffer flush tracker.
- `bch2_check_alloc_info()` runs the alloc/freespace/need-discard/bucket-gens consistency pass.
- `bch2_check_alloc_to_lru_refs()` verifies alloc-to-LRU and stripe references.
- `bch2_dev_freespace_init()` initializes freespace state for one device range.
- `bch2_fs_freespace_init()` initializes freespace state for all devices that need it.

Role:
- This is the public interface for allocation-derived-index verification, runtime freespace validation, and mount/device-add freespace initialization.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/check.h -->