# Group Research: group_203_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_alloc_discard_c_sour_f713d8b1933d

Scope checked against `Docs/research_subset_a.md`. The referenced internal group report path was not present in this checkout. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.c

Implements bcachefs discard/TRIM processing and cached-bucket invalidation. It operates over `BTREE_ID_need_discard`, alloc keys, LRU keys, backpointers, per-device discard queues, and filesystem/device write refs.

Key responsibilities:
- Track in-flight discard bios in `c->discards.in_flight`, with per-device and global ref counters.
- Submit `REQ_OP_DISCARD` bios for buckets whose alloc state is `BCH_DATA_need_discard`.
- After IO completion, mark alloc keys back to `BCH_DATA_free` in the alloc btree.
- Enforce journal safety: buckets are not freed for reuse until `journal_seq_empty` is flushed and older than rewind limits.
- Compute per-device discard release pressure and advance journal rewind sequence when free-space pressure requires it.
- Provide async normal discard work and fast per-device discard work.
- Invalidate cached buckets by walking LRU entries, resolving backpointers, dropping a removed/evicted device from referenced extents, and setting unrecoverable error keys if no readable pointer remains.
- Initialize and tear down discard/invalidations work items, bioset, and dynamic arrays.

Important control flow:
- `bch2_do_discards()` iterates `BTREE_ID_need_discard`, calls `bch2_discard_one_bucket()`, drains completed bios via `bch2_discards_complete()`, then may flush the journal/write buffer and retry.
- `bch2_discard_one_bucket()` performs eligibility checks: nouse bucket, duplicate in-flight discard, journal flush state, rewind state, data type, open bucket, device writable ref, hardware discard availability, and `opts.nochanges`.
- `__discard_mark_free()` is the committed state transition from `need_discard` to `free`; it also clears compatibility discard flags and emits trace events.
- Fast discard queues buckets from just-closed open buckets via `bch2_fast_discard_bucket_add()`.
- Invalidation starts at LRU entries, confirms alloc key consistency, scans backpointers, and mutates referenced keys to remove the target device.

Concurrency and lifetime:
- `c->discards.lock` protects in-flight discard entries and ref counters.
- Device write refs pin devices until both discard IO and alloc-btree mark-free commits are complete.
- Work is scheduled on `c->write_ref_wq` and guarded by enumerated filesystem write refs.
- Comments explicitly call out a race avoided between device removal and `discards_complete()` by holding `io_ref` through alloc updates.

Dependencies:
- Alloc key conversion/update helpers, btree iterators, write buffer flushing, journal flush/rewind APIs, device usage accounting, LRU helpers, backpointer helpers, and trace events.

Failure behavior:
- Unexpected post-discard alloc type mismatch in `__discard_mark_free()` triggers emergency read-only.
- Normal races from the write buffer are counted as `bad_data_type`.
- EROFS errors are suppressed at worker exit; other errors are logged.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.h

Public header for discard and invalidation work.

Exports:
- Fast discard queue APIs: `bch2_fast_discard_bucket_add()`, `bch2_fast_discard_bucket_del()`, text dump helper.
- Normal discard worker entry points and async scheduling.
- Going-read-only discard pressure handling.
- Invalidation worker entry points and per-device/global invalidation scheduling.
- Device/filesystem discard init and exit functions.

Inline policy:
- `should_invalidate_buckets()` computes how many cached buckets should be invalidated to keep roughly `nbuckets / 32` buckets free above stripe watermark reserve, clamped by cached bucket count.

Dependencies:
- Includes `alloc/buckets.h` for usage and reservation helpers.
- Consumed by allocator foreground code to trigger cached-data invalidation under free-space pressure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.c

Implements disk group superblock validation, CPU mirror construction, target resolution, disk group path manipulation, option parsing, and display helpers.

Key responsibilities:
- Validate `BCH_SB_FIELD_disk_groups`:
  - Member group indices must exist.
  - Members cannot reference deleted groups.
  - Non-deleted labels must be non-empty.
  - Sibling labels under the same parent must be unique.
- Convert on-disk disk group entries to an RCU-protected `bch_disk_groups_cpu`.
- Populate each group’s transitive device mask by walking parent links from each alive member’s group.
- Resolve targets:
  - `TARGET_NULL` means no target restriction.
  - `TARGET_DEV` maps directly to one device.
  - `TARGET_GROUP` maps to a group’s device mask.
- Parse dotted disk paths, find or create missing path components in the superblock, and assign devices to groups.
- Parse mount/options target strings as either device names, group paths, or `none`.
- Render targets and disk paths against either live filesystem state or a raw superblock.

Important APIs:
- `bch2_sb_disk_groups_to_cpu()`
- `bch2_target_to_mask()`
- `bch2_dev_in_target_rcu()`
- `bch2_disk_path_find()`
- `bch2_disk_path_find_or_create()`
- `bch2_dev_group_set()`
- `bch2_opt_target_parse()`
- `bch2_target_to_text()`

Concurrency:
- Superblock mutations require `c->sb_lock`.
- Live disk group lookup uses RCU.
- `bch2_dev_group_set()` wraps mutation in `PF_MEMALLOC_NOFS`, writes the superblock, and marks reconcile scanning state before/after changing group membership.

Dependencies:
- Superblock member helpers, superblock IO, device lookup, reconcile work marking, RCU device iteration, and Linux `sort`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.h

Public disk group and target header.

Defines:
- `disk_groups_nr()` for deriving entry count from variable-size superblock field.
- `struct target` and target encoding constants.
- `dev_to_target()`, `group_to_target()`, and `target_decode()`.
- `target_rw_devs()` to intersect allocator RW device masks with a target mask.
- `bch2_target_accepts_data()` for checking whether a target can accept a data type.

Exports:
- Disk path lookup/create/text functions.
- Target parse/text option functions via `bch2_opt_target`.
- Disk group superblock-to-CPU conversion.
- Device group assignment functions.
- Disk group debug text.

Role in allocator:
- Foreground allocation uses `target_rw_devs()` to decide eligible devices for a write’s data type and target.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_format.h

On-disk disk group format.

Defines:
- `BCH_SB_LABEL_SIZE` as 32 bytes.
- `struct bch_disk_group`, containing fixed-size label and two 64-bit flag words.
- Bitfields:
  - `BCH_GROUP_DELETED`
  - `BCH_GROUP_DATA_ALLOWED`
  - `BCH_GROUP_PARENT`
- `struct bch_sb_field_disk_groups`, a variable-length superblock field of disk group entries.

Purpose:
- Stores hierarchical disk labels/groups inside the bcachefs superblock.
- Parent field is 1-based in user-facing group references, matching logic in `disk_groups.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_types.h

In-memory disk group type declarations.

Defines:
- `struct bch_disk_group_cpu`:
  - deletion flag
  - parent group ID
  - fixed label
  - accumulated device mask
- `struct bch_disk_groups_cpu`:
  - RCU header
  - number of entries
  - flexible array of CPU group entries

Purpose:
- Provides RCU-safe live group lookup and target mask resolution derived from superblock disk group metadata.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.c

Core foreground bucket/sector allocator implementation. It manages open buckets, write points, device selection, allocation retries, EC stripe allocation, partial bucket reuse, allocator waiting, and allocator diagnostics.

Main responsibilities:
- Maintain open bucket handles and their hash table.
- Allocate buckets from either `BTREE_ID_freespace` or the early alloc-btree scan path before freespace is initialized.
- Avoid superblock buckets, nouse buckets, open buckets, nocow-locked buckets, and buckets whose empty journal sequence is not safely flushed.
- Schedule discard, GC generation cleanup, copygc, and cached bucket invalidation when allocation pressure indicates they can help.
- Choose devices with a weighted fair queue style `dev_stripe_state`, biased toward devices with more free space.
- Allocate enough effective durability to satisfy requested replicas, with special handling for zero-durability cache devices and erasure-coded buckets.
- Reuse write point open buckets and partial open buckets before allocating new buckets.
- Resize the number of active write points according to stranded space pressure.
- Stop/drop open buckets during device removal, EC shutdown, or filesystem shutdown.
- Render detailed allocator, open-bucket, write-point, device, and stuck-wait diagnostics.
- Filter allocator wait wakeups using per-device `alloc_wake_counter` snapshots.

Important control flow:
- `bch2_bucket_alloc_trans()` allocates one bucket from `req->ca`, possibly sleeping on open-bucket or free-space waitlists.
- `bch2_bucket_alloc_set_trans()` walks sorted candidate devices and accumulates bucket replicas.
- `bch2_alloc_sectors_req()` is the high-level allocator path: finds a write point, computes eligible devices, reuses open buckets, tries EC stripe allocation or normal bucket allocation, falls back from target-only to all devices when allowed, and aligns final sector availability.
- `bucket_alloc_from_stripe()` pulls buckets from partially constructed EC stripes.
- `writepoint_find()` hashes inode/write streams to write points, grows or recycles write points as needed.
- `__bch2_wait_on_allocator()` waits with timeout diagnostics and re-parks on unrelated fs-wide wakeups.

Concurrency:
- Open bucket freelist/hash/partial arrays are protected by `allocator.freelist_lock`.
- Individual open buckets have their own spinlock and atomic pin count.
- Write points are mutex-protected.
- Write point hash mutations use `write_points_hash_lock` and RCU hlist operations.
- Allocation waiters use closure waitlists plus per-device wake counters to avoid retry storms from unrelated device wakes.

Failure and fallback behavior:
- Returns rich bcachefs error codes for no buckets, insufficient devices, blocked allocation, open bucket exhaustion, EC failure, and no progress.
- Can reduce write point count and retry after blocked allocation/open-bucket failures.
- Copygc watermark writes avoid deadlocking copygc against its own free-space wait.
- Btree allocations are not allowed to degrade in the copygc bailout case because under-replicated btree writes can force emergency read-only.

Dependencies:
- Alloc/background/check/discard/disk group helpers, btree iter/update/check, copygc, EC creation/init, nocow locking, data write types, journal state, counters, time stats, and device/member state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.h

Public and inline support for the foreground allocator.

Defines:
- `struct dev_alloc_list`, a compact sorted list of candidate device IDs.
- `alloc_trace_entry`, used to diagnose allocation attempts and wake-counter snapshots.
- `struct alloc_request`, the central allocator request state containing replicas, EC options, target, flags, write point, candidate devices, counters, scratch buffers, and trace storage.
- Open bucket helper APIs and iteration macros.
- Write point specifier helpers for hash-based or pointer-based write points.

Important inline behavior:
- `alloc_trace_add()` records allocation attempt metadata and preserves the wake counter sampled before waitlist parking.
- `bch2_open_buckets_reserved()` reserves open-bucket handles by watermark; higher-priority watermarks reserve fewer handles.
- `bch2_open_bucket_put()` drops atomic pins and releases buckets via `__bch2_open_bucket_put()` at zero.
- `bch2_alloc_sectors_done_inlined()` closes/puts open buckets with less than one block remaining, emits sector allocation trace, and unlocks the write point.
- `bch2_bucket_is_open()` checks the open-bucket hash table.
- `bch2_bucket_is_open_safe()` rechecks under freelist lock.
- `bch2_bucket_set_discard_fast()` marks an open bucket for fast discard when it closes.
- `alloc_request_get()` allocates and initializes request state from a btree transaction.
- `bch2_ob_ptr()` constructs an extent pointer for the current offset inside an open bucket.
- `bch2_alloc_sectors_append_ptrs_inlined()` appends device pointers to a bkey and decrements free sectors from write point/open buckets.

Exports:
- Bucket allocation APIs.
- Device stripe ordering APIs.
- Alloc wait/wake helpers.
- Debug text helpers.
- Allocator initialization and open bucket shutdown.

Role:
- This header carries many allocator hot-path inlines used by data write code, journal resizing, btree allocation, and copygc/EC paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/format.h

On-disk allocation metadata formats.

Defines historical and current alloc key formats:
- `struct bch_alloc` plus V1 packed field list.
- `struct bch_alloc_v2`.
- `struct bch_alloc_v3` with journal sequence and flags.
- `struct bch_alloc_v4`, the current per-bucket allocation state.
- `struct bch_bucket_gens`, packed generation array for 256 buckets.

Important `bch_alloc_v4` fields:
- `journal_seq_nonempty` and `journal_seq_empty` track empty/nonempty transitions for noflush and discard safety.
- `flags` retains compatibility flags such as `NEED_DISCARD` and `NEED_INC_GEN`.
- `gen`, `oldest_gen`, and `data_type` describe bucket generation and allocation state.
- Sector counters: dirty, cached, stripe sectors.
- `io_time[2]` supports read/write LRU accounting.
- Stripe and backpointer counts support EC and backpointer metadata.

Key comment:
- Empty-state transitions are explicit:
  - nonempty to empty becomes `BCH_DATA_need_discard`.
  - `need_discard` to reusable empty becomes `BCH_DATA_free`.
  - high generation pressure can become `BCH_DATA_need_gc_gens`.
- `NEED_DISCARD` is maintained for compatibility but no longer drives `alloc_data_type()`.

Dependencies:
- Included by `bcachefs_format.h` to define `KEY_TYPE_alloc_v*` values and alloc btree payload layout.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.c

Implements LRU key validation, display, mutation, device removal cleanup, and fsck checking.

Key responsibilities:
- Validate LRU entries, currently rejecting time zero.
- Render LRU values and positions.
- Add/remove LRU set keys through the btree write buffer.
- Update LRU entries with `__bch2_lru_change()`.
- Remove alloc-related LRU entries for a device during device removal.
- Verify LRU btree consistency against the referenced alloc or stripe key.
- Repair missing or incorrect LRU entries through fsck error handling.

Important behavior:
- `lru_pos_to_bp()` maps LRU entries back to the referenced btree:
  - read and fragmentation LRUs reference alloc keys by device bucket.
  - stripe LRU references stripe keys.
- `bkey_lru_type_idx()` computes the expected LRU time/index from alloc or stripe metadata.
- `bch2_check_lru_key()` compares actual LRU position time with expected index and deletes bad entries if fsck elects repair.
- `bch2_lru_check_set()` checks that a referring key has its expected LRU set entry and can create it during repair.
- `bch2_check_lrus()` walks the whole LRU btree with progress reporting and write-buffer maybe-flush support.

Dependencies:
- Alloc conversion helpers, btree iter/update/write buffer, EC stripe trigger helpers, recovery/progress helpers, and fsck error framework.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.h

LRU helper header.

Defines:
- `lru_pos_id()` and `lru_pos_time()` for decoding the 64-bit inode field into LRU ID and time.
- `lru_pos()`, `lru_start()`, and `lru_end()` for constructing btree positions.
- `lru_type()` mapping special LRU IDs to read, fragmentation, or stripe LRU types.
- Bkey ops for `KEY_TYPE_lru`.
- Inline wrapper `bch2_lru_change()` that avoids work when old and new times match.

Exports:
- LRU validation/text helpers.
- LRU position rendering.
- LRU change, device removal, check/set, and full check functions.

Role:
- Shared by allocator/discard invalidation and fsck consistency checks for cached buckets, fragmentation ordering, and stripe cache ordering.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru_format.h

On-disk LRU key value definitions.

Defines:
- `struct bch_lru`, with generic value header and `idx`.
- `BCH_LRU_TYPES()` list:
  - `read`
  - `fragmentation`
  - `stripes`
- `enum bch_lru_type`.
- Special LRU IDs:
  - `BCH_LRU_BUCKET_FRAGMENTATION`
  - `BCH_LRU_STRIPE_FRAGMENTATION`
- 48-bit time/index encoding limit: `LRU_TIME_BITS` and `LRU_TIME_MAX`.

Purpose:
- Encodes multiple LRU domains in one `BTREE_ID_lru` namespace by storing type in high bits of `bpos.inode` and time/index in low bits.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.c

Implements replica-entry tracking in memory and on disk, plus read/write availability checks.

Main responsibilities:
- Convert bkeys, extents, stripes, and device lists into normalized `bch_replicas_entry_v1` entries.
- Keep in-memory replicas sorted in Eytzinger layout for fast lookup.
- Add newly observed replica entries to `c->replicas` and persist them into the superblock.
- Maintain atomic refcounts for journal replica entries.
- Garbage collect unreferenced or no-longer-accounted replica entries.
- Convert superblock replica fields between legacy v0 and current v1 encodings.
- Validate replica fields during superblock validation.
- Check if a filesystem can be read or written with a given device mask and force flags.
- Query whether a superblock/device has journal/data by replica entries.

Important behavior:
- User-data replica entries are treated as obsolete in superblocks when metadata version is at least `no_sb_user_data_replicas`; metadata and journal entries remain relevant.
- `extent_to_replicas()` ignores cached pointers and sets `nr_required = 0` when EC is present so stripe accounting supplies requirements.
- `stripe_to_replicas()` sets `nr_required` to data blocks (`nr_blocks - nr_redundant`) and lists stripe devices.
- Slow-path marking takes `sb_lock` and `capacity.mark_lock`, updates CPU replicas, converts to superblock format, and writes the superblock after dropping mark lock.
- v0 superblock output is used when no entry needs `nr_required != 1`; v1 is used when required count matters.

Read/write policy:
- `bch2_can_read_replicas_with_devs()` distinguishes metadata vs user data and maps missing/degraded states to force flags.
- `bch2_can_write_fs_with_devs()` checks online durable devices by data type, enforcing journal, btree, and user-data availability plus replica count thresholds unless degraded force flags allow it.

Concurrency:
- `capacity.mark_lock` protects `c->replicas`.
- `sb_lock` protects persisted superblock updates.
- Journal replica entry refcounts use atomics.

Dependencies:
- Accounting memory GC, bucket/device helpers, superblock IO, journal data type constants, sort/Eytzinger helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.h

Public replicas API and iteration helpers.

Exports:
- Replica sorting, text, validation, and CPU text functions.
- Conversion from bkey or device list to replica entry.
- Replica mark/query functions.
- Cached-data one-device replica initializer.
- Read/write availability checks.
- Superblock and live device data-presence queries.
- Journal replica ref get/put APIs.
- Replica entry kill and GC functions.
- Superblock-to-CPU conversion and superblock field ops.
- Cleanup and leak verification.

Inline helpers:
- `bch2_replicas_entry_has_dev()`
- `bch2_replicas_entry_eq()`
- `replicas_entry_next()`
- `for_each_replicas_entry()`

Role:
- Shared by allocation/accounting, journal, mount/device validation, fsck, and superblock parsing paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_format.h

On-disk replica superblock field formats.

Defines:
- `struct bch_replicas_entry_v0`: data type, device count, flexible device list.
- `struct bch_sb_field_replicas_v0`: variable-length v0 entries.
- `struct bch_replicas_entry_v1`: data type, device count, required count, flexible device list.
- `struct bch_sb_field_replicas`: variable-length v1 entries.
- `replicas_entry_bytes()` for variable entry sizing.
- `replicas_entry_add_dev()` for appending device IDs.

Purpose:
- v1 adds `nr_required`, which is needed for erasure coding and other layouts where “devices listed” is not the same as “devices required to read.”
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_types.h

In-memory replicas type declarations.

Defines:
- `struct bch_replicas_entry_cpu`, wrapping a variable-length v1 entry with an atomic refcount.
- `struct bch_replicas_cpu`, containing entry count, fixed padded CPU entry size, and entry storage pointer.
- `union bch_replicas_padded`, stack-friendly storage large enough for max pointer count.

Purpose:
- Supports sorted fixed-stride in-memory lookup even though on-disk replica entries are variable length.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/types.h

Core allocator/discard type declarations.

Defines:
- `enum bch_watermark` and watermark bit constants.
- Open bucket limits: `OPEN_BUCKETS_COUNT`, write point hash/count constants.
- `open_bucket_idx_t`, with index 0 reserved as invalid/sentinel.
- `struct open_bucket`, tracking one active allocation bucket, pin count, hash/freelist links, data type, EC attachment, sectors free, generation, and fast-discard flag.
- `struct open_buckets`, a small array of open bucket indices.
- `struct dev_stripe_state`, per-write-point weighted allocation clocks and cached device mask.
- Write point state enum and `struct write_point`, including allocation state, open buckets, per-device stripe allocation state, write lists, state timing, and index update work.
- `struct write_point_specifier`.
- Filesystem capacity structures with atomic/percpu usage and mark lock.
- `struct bch_fs_allocator`, containing RW device masks, freelists, waitlists, open buckets, partial buckets, write points, and special btree/reconcile write points.
- `discard_in_flight`, `discard_release`, `discard_state`, and `struct bch_fs_discards`.

Purpose:
- Central shared type layer for foreground allocation, discard processing, capacity accounting, and write point management.

Notable invariants:
- Open bucket index 0 is sentinel.
- `dev_stripe_state` comments describe weighted fair allocation by virtual clock increments inverse to free space.
- `discard_in_flight` stores `struct bch_dev *ca` so completion/removal races do not need to recover the device from `c->devs`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs.h

Central bcachefs runtime header. It includes on-disk format definitions, subsystem type headers, logging/error macros, debug parameter declarations, time stats IDs, device and filesystem core structs, unit/time helpers, and log message RAII helpers.

Key contents:
- Logging format macros for filesystem, device, offset, and inode contexts.
- Error logging helpers that suppress transaction-restart noise.
- Debug parameter declarations for always-on and debug-only runtime knobs.
- `BCH_TIME_STATS()` enum definitions, including allocator/discard/journal/blocking time stats.
- Device read/write ref enumerations.
- `struct bch_dev`, the live member-device state.
- Filesystem flags and write-ref enumerations.
- `struct bch_fs`, the live filesystem root object.
- Error throwing helper `bch_err_throw()`.
- Read-only ref helpers.
- Unit conversion helpers for bucket and block sizes.
- bcachefs time conversion helpers.
- Discard option resolution between mount option and device option.
- Casefold availability helper.
- Log-message scoped class helpers.

Allocator/discard-related fields:
- `struct bch_dev` contains allocator cursors, `alloc_wake_counter`, open/partial bucket counters, invalidate work, fast discard work/queue/lock, and device usage state.
- `struct bch_fs` contains `replicas`, RCU `disk_groups`, `capacity`, `allocator`, and `discards`.
- `BCH_WRITE_REFS()` includes discard, fast discard, discard freespace checking, invalidate, and GC generation refs.
- `BCH_DEV_WRITE_REFS()` includes journal discard, bucket discard, fast discard, invalidation, EC, and IO write refs.

Important helper:
- `bch2_discard_opt_enabled()` resolves discard behavior: a mount-level discard option overrides per-device persisted discard setting only for the current mount.

Role:
- This header is the integration point where the allocator/discard/replicas/disk group subsystems become part of the live bcachefs filesystem object.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_format.h

Primary on-disk format header for bcachefs.

Major responsibilities:
- Define bitmask helper macros for native and little-endian packed fields.
- Define core btree key primitives: `bpos`, `bversion`, `bkey`, `bkey_packed`, `bkey_i`, and key construction helpers.
- Enumerate bkey types and their semantic descriptions.
- Define common simple key values such as deleted, whiteout, error, cookie, set, checksum, and backpointer values.
- Define superblock field header, superblock field types, and single-device field mask.
- Enumerate btree IDs, flags, allowed key types, and descriptions.
- Include all subsystem format headers, including alloc, disk groups, LRU, replicas, accounting, extents, EC, inode, quota, journal, members, and snapshots.
- Define journal superblock fields, encryption key/KDF formats, clean shutdown field, extended superblock field, metadata versions, superblock layout, and core superblock.
- Define superblock option bitfields, features, compat flags, checksum/compression/hash options, magic constants, journal entry types, journal entry payloads, journal set format, and btree node formats.

Allocator-related format details:
- `BTREE_ID_alloc`, `freespace`, `need_discard`, `backpointers`, `bucket_gens`, `lru`, `accounting`, and reconcile btrees are all declared here.
- `BTREE_ID_need_discard` is a write-buffer btree of `KEY_TYPE_set` entries for buckets waiting for discard/TRIM.
- Metadata version `need_discard_by_journal_seq` documents reindexing `need_discard` by journal sequence for efficient discard eligibility.
- `BCH_SB_FIELD_disk_groups`, `replicas_v0`, and `replicas` connect allocator targeting and replica accounting to superblock metadata.
- `btree_id_is_alloc()` classifies allocation/accounting/reconcile btrees for recovery/reconstruction handling.
- `btree_id_can_reconstruct()` and `btree_id_recovers_from_scan()` encode which btrees can be rebuilt from other metadata.

Important on-disk structures:
- `struct bch_sb_layout` records backup superblock layout.
- `struct bch_sb` stores versioning, UUIDs, label, device count/index, block size, flags, feature/compat masks, layout, and variable fields.
- `struct jset` stores journal entries with sequence, version, checksum, no-flush/overwrite flags, and oldest dirty sequence.
- `struct bset`, `struct btree_node`, and `struct btree_node_entry` describe btree node write sets and node metadata.

Versioning:
- `BCH_METADATA_VERSIONS()` lists format evolution from early bkey renumbering through current versions, including recent allocator-relevant changes such as `bucket_stripe_index`, `no_sb_user_data_replicas`, `erasure_coding`, and `need_discard_by_journal_seq`.
- `bcachefs_metadata_version_current` is derived from `bcachefs_metadata_version_max - 1`.

Role:
- All files in this group depend on this header directly or indirectly for data type IDs, btree IDs, key/value formats, superblock field IDs, and metadata version gates.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_format.h -->