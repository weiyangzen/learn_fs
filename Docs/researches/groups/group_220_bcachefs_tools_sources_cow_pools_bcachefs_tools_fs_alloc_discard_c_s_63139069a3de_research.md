# Group Research: group_220_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_alloc_discard_c_s_63139069a3de

Scope checked against `Docs/research_subset_a.md`. I read every listed source file completely. The referenced internal group report path was not present before this run.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/discard.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/discard.c

Implements bcachefs discard/TRIM processing and cached-bucket invalidation for the bcachefs-tools source tree. The file operates over `BTREE_ID_need_discard`, alloc keys, per-device discard work, the btree write buffer, journal rewind state, LRU entries, and backpointers.

Key responsibilities:
- Track discard bios in `c->discards.in_flight`, with global and per-device in-flight reference counters.
- Submit `REQ_OP_DISCARD` bios for buckets whose alloc key is `BCH_DATA_need_discard`.
- Convert discarded alloc keys from `BCH_DATA_need_discard` to `BCH_DATA_free` after IO completion.
- Enforce reuse safety with `journal_seq_empty`, `journal.flushed_seq_ondisk`, and `journal.rewind_seq_ondisk`.
- Compute per-device discard release pressure, advancing journal rewind sequence when pending discard buckets are blocking free space.
- Flush the journal and btree write buffer when discard progress requires them.
- Provide normal async discard work and a fast per-device discard queue for recently closed open buckets.
- Invalidate cached buckets by walking LRU entries, resolving bucket backpointers, dropping the removed/invalidated device from referenced keys, and converting unreadable keys to `KEY_TYPE_ERROR_device_removed`.

Important control flow:
- `bch2_do_discards()` scans `BTREE_ID_need_discard` ordered by journal sequence, calls `bch2_discard_one_bucket()`, drains completed discards, then handles journal rewind/write-buffer flush policy.
- `bch2_discard_one_bucket()` checks nouse buckets, duplicate in-flight entries, fastpath eligibility, journal flush state, rewind state, alloc data type, open-bucket state, device write refs, discard hardware support, and `opts.nochanges`.
- `__discard_mark_free()` is the committed alloc-btree state transition. It clears the compatibility discard flag, sets `data_type = BCH_DATA_free`, clears journal sequence fields, updates with `BTREE_TRIGGER_is_discard`, and commits at reclaim watermark.
- `discard_endio()` only marks an in-flight entry complete and drops the IO counters. Alloc-btree updates and device write-ref release are completed later by `bch2_discards_complete()`.
- `calculate_discard_sectors_to_release()` computes discard pressure per device so one device’s need-discard backlog cannot be hidden by filesystem-wide free space.
- `__bch2_do_invalidates()` starts from the cached-bucket LRU, validates alloc-key/LRU consistency, then invalidates buckets by their backpointers.

Concurrency and lifetime:
- `c->discards.lock` protects `in_flight`, `ref`, and `refs[]`.
- Device write refs are held until the alloc-btree mark-free update has committed, preventing device removal from deleting the same alloc-btree range concurrently.
- Work is queued on `c->write_ref_wq` and guarded by filesystem/device enumerated write refs.
- Fast discard queues are per-device darrays guarded by `discard_fast_lock`.

Failure behavior:
- If a post-discard alloc key is no longer `BCH_DATA_need_discard` in `__discard_mark_free()`, the filesystem is forced emergency read-only.
- Expected write-buffer races where an alloc key no longer has need-discard state are counted as `bad_data_type`.
- Worker exits suppress `EROFS`-style errors but log other failures.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/discard.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/discard.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/discard.h

Public header for discard and cached-bucket invalidation work.

Exports:
- Fast discard queue APIs: `bch2_fast_discard_bucket_add()`, `bch2_fast_discard_bucket_del()`, and `bch2_fast_discards_to_text()`.
- Discard diagnostics via `bch2_discards_to_text()`.
- Normal discard scheduling and worker entry points: `bch2_do_discards_async()`, `bch2_do_discards_going_ro()`, `bch2_do_discards_work()`, and `bch2_do_discards_fast_work()`.
- Invalidation worker entry points: `bch2_do_invalidates_work()`, `bch2_dev_do_invalidates()`, and `bch2_do_invalidates()`.
- Per-device and filesystem discard init/exit functions.

Important inline policy:
- `should_invalidate_buckets()` targets roughly `nbuckets / 32` free buckets beyond stripe watermark reserve and clamps the result by cached-bucket count.

Role:
- Used by foreground allocation to trigger discards, generation cleanup, and cached-data invalidation when free-space pressure makes those actions useful.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/discard.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.c

Implements disk group superblock validation, RCU CPU representation construction, target resolution, disk-group path manipulation, option parsing, and text rendering.

Key responsibilities:
- Validate `BCH_SB_FIELD_disk_groups`:
  - Device group indexes must exist.
  - Devices may not reference deleted groups.
  - Non-deleted labels must be nonempty.
  - Sibling labels under the same parent must be unique.
- Build `struct bch_disk_groups_cpu` from the on-disk superblock field.
- Populate each CPU disk group with the transitive mask of devices in that group and its descendants.
- Resolve allocation targets:
  - `TARGET_NULL` means no target mask.
  - `TARGET_DEV` maps to one device.
  - `TARGET_GROUP` maps to the disk group’s device mask.
- Parse dotted group paths, find existing path components, or create missing components in the superblock.
- Assign devices to groups and persist the superblock.
- Parse target mount/options strings as `none`, device names, or disk group paths.
- Render targets and disk paths from either live filesystem state or raw superblock state.

Important APIs:
- `bch2_sb_disk_groups_to_cpu()`
- `bch2_target_to_mask()`
- `bch2_dev_in_target_rcu()`
- `bch2_disk_path_find()`
- `bch2_disk_path_find_or_create()`
- `__bch2_dev_group_set()` / `bch2_dev_group_set()`
- `bch2_opt_target_parse()`
- `bch2_target_to_text()` / `bch2_opt_target_to_text()`

Concurrency:
- Superblock mutation requires `c->sb_lock`.
- Live group lookup uses RCU through `c->disk_groups`.
- `bch2_dev_group_set()` marks reconcile scanning before and after changing group membership, uses `PF_MEMALLOC_NOFS`, writes the superblock, and refreshes CPU group state.

Dependencies:
- Superblock member helpers, superblock field resize/write helpers, device lookup, reconcile work marking, RCU device iteration, and Linux `sort`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.h

Public disk group and allocation target header.

Defines:
- `disk_groups_nr()` for deriving the number of variable-length disk group entries from a superblock field.
- `struct target` with `TARGET_NULL`, `TARGET_DEV`, and `TARGET_GROUP`.
- Target encoding constants `TARGET_DEV_START` and `TARGET_GROUP_START`.
- `dev_to_target()`, `group_to_target()`, and `target_decode()`.
- `target_rw_devs()` to intersect allocator RW device masks with a target mask.
- `bch2_target_accepts_data()` to test whether a target can accept a data type.
- `bch2_dev_in_target()` wrapper around the RCU-aware implementation.

Exports:
- Disk path lookup/create/text helpers.
- Target parse/text option helpers through `bch2_opt_target`.
- Disk group superblock-to-CPU conversion.
- Device group assignment functions.
- Disk group diagnostic text.

Role:
- Foreground allocation uses target helpers to restrict candidate devices by mount option, device label, disk group, or data type.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_format.h

On-disk disk group format header.

Defines:
- `BCH_SB_LABEL_SIZE` as 32 bytes.
- `struct bch_disk_group`, containing a fixed-size label and two 64-bit flag words.
- Bitfields:
  - `BCH_GROUP_DELETED`
  - `BCH_GROUP_DATA_ALLOWED`
  - `BCH_GROUP_PARENT`
- `struct bch_sb_field_disk_groups`, a variable-length superblock field containing disk group entries.

Purpose:
- Stores hierarchical disk labels/groups in the bcachefs superblock.
- Parent IDs are stored as 1-based values; callers convert by subtracting or adding one when walking group paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_types.h

In-memory disk group type declarations.

Defines:
- `struct bch_disk_group_cpu` with deletion state, parent ID, fixed label, and accumulated device mask.
- `struct bch_disk_groups_cpu` with RCU header, entry count, and flexible array of CPU group entries.

Purpose:
- Provides the live RCU-safe representation used by target resolution and allocator device filtering.
- CPU entries are derived from superblock disk-group metadata and include transitive device membership masks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.c

Core foreground bucket and sector allocator implementation. It manages open buckets, write points, allocation waits, device selection, replica placement, erasure-coded allocation, partial bucket reuse, allocator diagnostics, and shutdown/drop behavior.

Main responsibilities:
- Maintain open bucket handles, freelist, hash table, and partial open-bucket list.
- Allocate buckets from `BTREE_ID_freespace`, with an early alloc-btree scan path before freespace is initialized.
- Avoid superblock buckets, nouse buckets, open buckets, nocow-locked buckets, and buckets whose empty journal sequence is not flushed.
- Trigger discard, GC generation cleanup, copygc, and cached-bucket invalidation when allocation pressure indicates they may unblock allocation.
- Select devices through `dev_stripe_state`, a weighted fair virtual-time scheme biased toward devices with more free space.
- Allocate enough effective durability to satisfy requested replicas, including zero-durability cache-device handling.
- Reuse write-point open buckets and partial open buckets before allocating new buckets.
- Allocate from partially constructed erasure-code stripes when appropriate.
- Resize active write points based on stranded free-space pressure.
- Stop/drop open buckets for device removal, erasure-coding shutdown, or filesystem shutdown.
- Render allocator, open-bucket, write-point, device, request, and stuck-wait diagnostics.
- Filter allocator wait wakeups through per-device `alloc_wake_counter` snapshots.

Important control flow:
- `bch2_bucket_alloc_trans()` allocates a single bucket from `req->ca`, handling free-space pressure, copygc wakeups, discard wakeups, waitlist parking, and early/freespace allocation paths.
- `bch2_bucket_alloc_set_trans()` sorts candidate devices and attempts allocation until enough effective durability is accumulated.
- `bucket_alloc_from_stripe()` reuses buckets already attached to an EC stripe head.
- `bch2_alloc_sectors_req()` is the high-level allocator path: finds a write point, computes eligible devices from target/data type, reuses open buckets, tries partial buckets, EC stripe allocation, normal allocation, target fallback, EC fallback, and final alignment.
- `writepoint_find()` maps hashed write streams to write points, grows the write-point pool when possible, or recycles the oldest write point.
- `try_decrease_writepoints()` drops a write point when allocation stalls and stranded open-bucket space is too high.
- `__bch2_wait_on_allocator()` waits with timeout diagnostics and avoids full retries for unrelated fs-wide wakeups.

Concurrency:
- `allocator.freelist_lock` protects open bucket freelist/hash/partial arrays.
- Each open bucket has its own spinlock and atomic pin count.
- Write points are protected by per-write-point mutexes.
- Write point hash mutation uses `write_points_hash_lock` and RCU hlist operations.
- Allocation waiters use closure waitlists plus device wake-counter snapshots to reduce retry storms.

Failure and fallback behavior:
- Returns rich bcachefs error codes for no buckets, open-bucket exhaustion, blocked allocation, insufficient devices, no progress, and EC allocation failure.
- Can commit degraded allocation when at least one replica exists and waiting cannot make progress.
- Copygc watermark writes avoid deadlocking the freeing operation against its own wait.
- Btree writes avoid unsafe degradation in copygc bailout cases because under-replicated btree writes can force emergency read-only.

Dependencies:
- Alloc/background/check/discard/disk group helpers, btree iter/update/check APIs, copygc, EC create/init, nocow locking, write types, journal state, counters, time stats, and device/member state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.h

Public and inline support for the foreground allocator.

Defines:
- `struct dev_alloc_list`, a compact sorted list of candidate device IDs.
- `alloc_trace_entry`, used to diagnose allocation attempts and wake-counter snapshots.
- `struct alloc_request`, the central allocator request object containing requested replicas, EC options, target, write flags, write point, candidate masks, device list, counters, scratch fields, and preallocated trace storage.
- Open bucket helper APIs, iteration macros, hash lookup helpers, and pin/put logic.
- Sector allocation append/done inline helpers.
- Write point specifier helpers for hash-based and pointer-based write points.

Important inline behavior:
- `alloc_trace_add()` records allocation attempt state, including retry flags, device, error, wake-counter snapshot, free buckets, and copygc progress.
- `bch2_open_buckets_reserved()` reserves different amounts of open-bucket capacity by watermark.
- `bch2_bucket_is_open_safe()` checks open-bucket state with a lock-protected recheck.
- `bch2_bucket_set_discard_fast()` marks an open bucket for fast discard when it is later closed.
- `alloc_request_get()` initializes allocator request state and disables EC when too few EC replicas are requested.
- `bch2_alloc_sectors_append_ptrs_inlined()` appends extent pointers from open buckets and advances per-bucket free-sector counters.
- `bch2_alloc_sectors_done_inlined()` drops empty open buckets and emits sector allocation tracing.
- `bch2_wait_on_allocator()` only enters the full wait loop when the closure still has outstanding waits.

Exports:
- Device allocation ordering and stripe increment helpers.
- Bucket/open-bucket allocation APIs.
- Sector allocation start/done APIs.
- Open bucket shutdown and diagnostic text APIs.
- Allocator stuck wait helper.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/format.h

On-disk allocation metadata format header.

Defines:
- Legacy `struct bch_alloc`, `bch_alloc_v2`, and `bch_alloc_v3` formats.
- Current `struct bch_alloc_v4`, the main per-bucket alloc-btree value.
- Field lists for v1/v2 variable fields.
- Compatibility flags for need-discard and need-inc-gen.
- `BCH_ALLOC_V4_U64s_V0` and `BCH_ALLOC_V4_U64s` size constants.
- Alloc-v4 bitfields for discard/inc-gen and backpointer packing metadata.
- Bucket generation key format: `struct bch_bucket_gens`, with 256 generation bytes per key.

Important alloc-v4 semantics:
- `data_type` stores current bucket state.
- Empty-state transitions are explicit:
  - nonempty to empty becomes `BCH_DATA_need_discard`.
  - need-discard to empty becomes `BCH_DATA_free`.
  - free with exhausted GC generation becomes `BCH_DATA_need_gc_gens`.
- `journal_seq_nonempty` and `journal_seq_empty` track bucket state transitions for noflush and discard safety.
- `NEED_DISCARD` is retained for forward/backward compatibility, though current `alloc_data_type()` no longer reads it.
- `stripe_refcount`, `stripe_sectors`, dirty/cached sector counts, IO times, generation fields, and external backpointer counters support allocator, GC, LRU, and EC logic.

Role:
- This header is the shared wire format consumed by alloc triggers, discard, freespace, LRU, backpointer, and foreground allocation code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru.c

Implements LRU key validation, text rendering, LRU update helpers, LRU consistency checks, and device-removal cleanup.

Key responsibilities:
- Validate LRU keys, currently rejecting entries at time zero.
- Render LRU values and encoded LRU positions.
- Add/remove buffered `BTREE_ID_lru` set keys.
- Change LRU position atomically by clearing old position and setting new position.
- Check that alloc or stripe keys have matching LRU entries.
- Remove LRU entries associated with a removed device.
- Full fsck-style scan of the LRU btree with write-buffer flush assistance and progress reporting.

Important logic:
- `__bch2_lru_set()` uses `bch2_btree_bit_mod_buffered()` for buffered set/clear operations.
- `bch2_lru_check_set()` repairs missing LRU entries when the referring alloc/stripe key expects one.
- `lru_pos_to_bp()` maps LRU key type to the btree/key that should justify the LRU entry:
  - read and bucket-fragmentation LRUs point to alloc keys.
  - stripe-fragmentation LRUs point to stripe keys.
- `bkey_lru_type_idx()` recomputes the expected LRU time from alloc read time, alloc fragmentation, or stripe LRU position.
- `bch2_check_lru_key()` removes incorrect LRU entries after reporting fsck errors.
- `bch2_check_lrus()` scans all LRU keys and commits repairs with `BCH_TRANS_COMMIT_no_enospc`.

Dependencies:
- Alloc conversion helpers, btree buffered updates, btree write buffer flush helpers, EC stripe LRU helpers, fsck/progress infrastructure, and recovery/error code support.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru.h

Public LRU helper header.

Defines:
- `lru_pos_id()` and `lru_pos_time()` for decoding LRU positions.
- `lru_pos()` for encoding an LRU ID, device/bucket payload, and time into `struct bpos`.
- `lru_start()` / `lru_end()` bounds helpers.
- `lru_type()` mapping special LRU IDs to read, bucket-fragmentation, or stripe-fragmentation LRUs.
- `bch2_bkey_ops_lru` with validation/text callbacks and minimum value size.
- `bch2_lru_change()` wrapper that avoids work when the time is unchanged.

Exports:
- LRU validation/text helpers.
- LRU change helper.
- Device LRU cleanup.
- Missing-entry check/repair helper.
- Full LRU check entry point.

Role:
- Used by alloc triggers, discard invalidation, cached bucket eviction, stripe fragmentation tracking, and fsck validation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru_format.h

On-disk LRU format header.

Defines:
- `struct bch_lru`, an obsolete key value containing an `idx`.
- `BCH_LRU_TYPES()` and `enum bch_lru_type`:
  - read
  - fragmentation
  - stripes
- Special LRU IDs:
  - `BCH_LRU_BUCKET_FRAGMENTATION`
  - `BCH_LRU_STRIPE_FRAGMENTATION`
- LRU time encoding constants:
  - `LRU_TIME_BITS = 48`
  - `LRU_TIME_MAX`

Role:
- Provides the encoded key-space layout used by `BTREE_ID_lru`.
- Current LRU presence is represented primarily by `KEY_TYPE_set` keys in the LRU btree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/lru_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.c

Implements replica-set tracking, validation, superblock conversion, refcounting, GC cleanup, readability/writability checks, and device-data queries.

Main responsibilities:
- Represent on-disk replica entries as sorted in-memory `struct bch_replicas_cpu` entries with atomic refs.
- Convert bkeys and device lists into `bch_replicas_entry_v1` entries.
- Mark new replica entries, adding them to the CPU table and superblock when needed.
- Refcount journal replica entries and remove unused ones.
- Garbage-collect unreferenced or obsolete replica entries.
- Convert between superblock `replicas_v0`, `replicas`, and in-memory CPU form.
- Validate superblock replica fields, including invalid devices, bad required counts, and duplicates.
- Determine whether a filesystem can be read or written with a given device mask and force flags.
- Query whether the superblock has journal replicas or whether a device has any data types recorded.
- Verify replica refs are clean at shutdown.

Important data flow:
- `extent_to_replicas()` extracts non-cached extent pointers. EC pointers set `nr_required = 0` because stripe data is represented separately.
- `stripe_to_replicas()` records stripe devices and required block count as `nr_blocks - nr_redundant`.
- `bch2_bkey_to_replicas()` maps btree pointers to btree replicas, extents/reflink values to user replicas, and stripes to parity replicas.
- `cpu_replicas_add_entry()` grows the in-memory table, copies old entries, appends a variable-length new entry, and sorts in Eytzinger order.
- `bch2_mark_replicas_slowpath()` updates CPU state under `mark_lock` and `sb_lock`, converts it back to superblock form, then writes the superblock if changed.
- `bch2_replicas_gc_accounted()` compares replica entries against disk accounting keys and removes entries no longer accounted.

Compatibility behavior:
- `replicas_v0` entries have no `nr_required`; conversion sets `nr_required = 1`.
- If no entry requires `nr_required != 1`, CPU-to-superblock conversion writes the v0 field; otherwise it writes the v1 `replicas` field.
- For metadata version `no_sb_user_data_replicas` and later, user-data replica entries are considered obsolete and skipped/implicitly marked.

Read/write policy:
- `bch2_can_read_replicas_with_devs()` checks online devices against `nr_required`, distinguishing metadata/data lost and degraded force flags.
- Cached replicas are always readable for this check.
- `bch2_can_write_fs_with_devs()` requires online journal, btree, and user data writable durability and enforces metadata/data degraded force flags against desired replicas.

Concurrency:
- `c->capacity.mark_lock` protects the in-memory replica table.
- `c->sb_lock` protects superblock field updates.
- `PF_MEMALLOC_NOFS` is used around superblock/replica mutation paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.h

Public replicas tracking header.

Exports:
- Replica entry sort, text, and validation helpers.
- CPU replica table text rendering.
- Device-list and bkey-to-replica conversion helpers.
- Marked/mark APIs for ensuring replica entries exist.
- Cached replica-entry constructor.
- Readability/writability checks for device masks.
- Superblock journal/data query helpers.
- Replica entry get/put/kill APIs for refcounted journal entries.
- Replica GC helpers.
- Superblock-to-CPU conversion.
- Superblock field ops for `replicas` and `replicas_v0`.
- Shutdown verification and cleanup helpers.

Defines:
- `bch2_replicas_entry_has_dev()`.
- `bch2_replicas_entry_eq()`.
- `replicas_entry_next()` and `for_each_replicas_entry()` for variable-length superblock fields.

Role:
- Shared by allocation, journal, mount/device checks, fsck/accounting, and superblock validation code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_format.h

On-disk replicas format header.

Defines:
- `struct bch_replicas_entry_v0`:
  - `data_type`
  - `nr_devs`
  - flexible `devs[]`
- `struct bch_sb_field_replicas_v0`.
- `struct bch_replicas_entry_v1`:
  - `data_type`
  - `nr_devs`
  - `nr_required`
  - flexible `devs[]`
- `struct bch_sb_field_replicas`.
- `replicas_entry_bytes()` for variable-length entry sizing.
- `replicas_entry_add_dev()` append helper.

Purpose:
- Stores which devices contain each class of data and how many devices/blocks are required to read it.
- V1 adds `nr_required`, enabling degraded/erasure-coded availability checks that v0 cannot express directly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_types.h

In-memory replicas type declarations.

Defines:
- `struct bch_replicas_entry_cpu`, containing an atomic refcount and an embedded variable-length `bch_replicas_entry_v1`.
- `struct bch_replicas_cpu`, containing entry count, uniform in-memory entry size, and pointer to the entries array.
- `union bch_replicas_padded`, a stack-safe padded replica entry large enough for `BCH_BKEY_PTRS_MAX` devices.

Purpose:
- Supports efficient sorted lookup and refcounting of variable-length replica entries.
- Provides padded temporary storage for constructing replica entries from bkeys and device lists.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/types.h

Allocator runtime type header.

Defines:
- Watermark names and `enum bch_watermark`.
- Open-bucket constants:
  - `OPEN_BUCKETS_COUNT = 4096`
  - `WRITE_POINT_HASH_NR = 32`
  - `WRITE_POINT_MAX = 32`
- `open_bucket_idx_t`, with zero reserved as invalid/null.
- `struct open_bucket`, tracking an active bucket’s pin count, freelist/hash links, EC stripe association, data type, flags, device, generation, remaining sectors, bucket number, and EC stripe pointer.
- `struct open_buckets`, a compact list of open-bucket indexes.
- `struct dev_stripe_state`, the weighted fair per-device virtual-time state used for allocation ordering.
- Write point state enum and `struct write_point`.
- `struct write_point_specifier`.
- Capacity accounting structs:
  - `bch_fs_capacity_pcpu`
  - `bch_fs_capacity`
- `struct bch_fs_allocator`, containing RW device masks, free/open-bucket waitlists, open bucket arrays/hash/partial lists, write points, and special btree/reconcile write points.
- `discard_in_flight`, `discard_release`, `discard_state`, and `struct bch_fs_discards`.

Important semantics:
- `open_bucket` entries pin buckets until index updates make newly written data reachable.
- `dev_stripe_state` uses per-device virtual clocks incremented by inverse free space, biasing allocation toward devices with more free buckets.
- `write_point` is cache-line split between allocation state and index-update/work state.
- `bch_fs_capacity.capacity_gen` invalidates outstanding reservations when capacity decreases.
- `bch_fs_discards.refs[]` limits in-flight discards per device and coordinates discard completion waiters.

Role:
- Central shared allocator state used by foreground allocation, discard, cached invalidation, capacity accounting, write path, and shutdown/device-removal logic.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/alloc/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs.h

Core bcachefs runtime header. It pulls together subsystem type headers and defines central filesystem/device structures, logging helpers, flags, reference categories, time stats, unit conversions, and small cross-subsystem helpers.

Major contents:
- Logging prefix macros and `bch_err`/`bch_warn`/`bch_info` style wrappers.
- Error-printing helpers that suppress transaction restart noise.
- Debug static-key parameter declarations.
- `BCH_TIME_STATS()` and `enum bch_time_stats`, including allocator, journal, btree, data IO, write-buffer, nocow, and discard wait metrics.
- Device read/write enumerated ref categories.
- `struct bucket_bitmap`.
- `struct bch_dev`, the live member-device object.
- Filesystem flags in `BCH_FS_FLAGS()` and `enum bch_fs_flags`.
- Write ref categories in `BCH_WRITE_REFS()`.
- `struct bch_fs`, the main filesystem object.
- Error throwing helper `bch_err_throw()`.
- Read-only ref get/put helpers.
- Unit conversion and time conversion helpers.
- Filesystem/device name helpers.
- Discard option resolution.
- Casefold availability check.
- Structured log message RAII/class helpers.

Important `struct bch_dev` fields:
- Device lifetime refs: `ref`, `ref_outer`, and `io_ref[READ/WRITE]`.
- Backpointer to `struct bch_fs`, device index, removal state, and cached member info.
- Superblock handle and write/read scratch state.
- Per-bucket state: GC buckets, bucket generations, oldest generations, nouse bitmap, backpointer mismatch/empty bitmaps.
- Per-device usage counters.
- Allocator fields: allocation cursors, wake counter, open/partial bucket counts, invalidate/discard fast work, discard queue.
- Journal device state, IO error work, latency/congestion counters, and IO done counters.

Important `struct bch_fs` fields:
- Global lifecycle refs and state locks.
- Device arrays/masks and mount options.
- Superblock CPU/disk state and superblock lock.
- Unicode/casefold state.
- Counters, time stats, and persistent error tracking.
- Journal, journal replay, journal keys, and journal sequence blacklist.
- Recovery, btree, GC, accounting, replicas, disk groups, capacity, allocator, and discards state.
- Snapshot, compression, reconcile, copygc, EC, nocow, moving, VFS, quota, and debug state.
- Dedicated workqueues, including `write_ref_wq` used by write-ref-holding tasks.

Important helpers:
- `bucket_bytes()`, `block_bytes()`, and `block_sectors()`.
- `bch2_time_to_timespec()`, `timespec_to_bch2_time()`, `bch2_current_time()`, and `bch2_current_io_time()`.
- `bch2_discard_opt_enabled()` resolves filesystem mount discard override versus per-device discard setting.
- `bch2_fs_casefold_enabled()` validates Unicode/casefold availability.
- `bch2_log_msg` helpers build structured log output.

Role:
- This is the primary inclusion point for most bcachefs subsystems and the owner of allocator/discard/replica/disk-group state used by the files in this group.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs_format.h

Central on-disk format header for bcachefs. It defines common bitfield helpers, btree key layout, bkey types, superblock fields, btree IDs, metadata versions, superblock layout, feature/option enums, journal formats, and btree node formats.

Major sections:
- Overview comments for superblock, journal, btree, and btree key structure.
- Generic native-endian and little-endian bitfield accessor macros.
- `struct bkey_format`, `struct bpos`, `struct bversion`, `struct bkey`, `struct bkey_packed`, and `struct bkey_i`.
- Position/key construction helpers: `SPOS`, `POS`, `POS_MIN`, `POS_MAX`, `KEY`, `POS_KEY`, `bkey_init()`, and `bkey_bytes()`.
- Bkey type definitions in `BCH_BKEY_TYPES()`, including deleted/whiteout/error/cookie/hash entries, btree pointers, extents, inodes, alloc formats, stripes, reflink, inline data, snapshots, LRU, backpointers, bucket gens, logged ops, accounting, and extent whiteouts.
- Key error types such as `device_removed`, `double_allocation`, and `no_valid_pointers_repair`.
- Core small value structs: deleted/whiteout/error/cookie/hash/set/csum/backpointer.
- Backpointer flags, including reconcile-physical linkage and erasure/stripe pointer flags.
- Superblock field base type and all `BCH_SB_FIELDS()`.
- Btree flags and all `BCH_BTREE_IDS()`.
- Includes for all subordinate format headers, including allocation, replicas, LRU, members, accounting, extents, EC, inode, dirent, quota, snapshots, and journal blacklist formats.
- Journal bucket, crypt, clean-shutdown, and extended superblock field structures.
- Full metadata version list through current format evolution, including alloc v4, freespace, backpointers, LRU changes, disk accounting, casefolding, reconcile, erasure coding, and need-discard-by-journal-seq.
- `struct bch_sb_layout` and `struct bch_sb`.
- Superblock flags and option bitfields for checksum, compression, replicas, targets, journal tuning, write buffer, version upgrade, degraded action, casefolding, scrub journal, EC limits, and related options.
- Feature and compatibility bit enums.
- Error/degraded action enums.
- String hash, checksum, compression, and scrub-journal option enums.
- Magic numbers for bcache/bcachefs superblocks, journal sets, and bsets.
- Journal entry types and journal entry structures.
- Btree reconstruction helpers and btree node/bset formats.

Important format relationships:
- `struct bkey` is the common key header used across btrees; values are type-specific and inline.
- `BCH_BKEY_TYPES()` and `BCH_BTREE_IDS()` define which key types are valid in each btree.
- `BTREE_ID_need_discard`, `BTREE_ID_freespace`, `BTREE_ID_lru`, `BTREE_ID_alloc`, backpointers, bucket gens, and accounting are the allocator-relevant btrees.
- `BCH_SB_FIELD_disk_groups`, `BCH_SB_FIELD_replicas_v0`, and `BCH_SB_FIELD_replicas` are the superblock fields implemented by files in this group.
- `btree_id_is_alloc()` classifies allocator/reconstructable metadata btrees.
- `btree_id_can_reconstruct()` and `btree_id_recovers_from_scan()` describe recovery expectations for reconstructable metadata.
- Journal rewind entries and rewind limit entries connect to discard safety and journal rewind behavior.
- `struct btree_node` and `struct btree_node_entry` define the COW btree node log format.

Role:
- This file is the authoritative shared wire-format contract for bcachefs-tools and kernel-compatible metadata parsing/writing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs_format.h -->