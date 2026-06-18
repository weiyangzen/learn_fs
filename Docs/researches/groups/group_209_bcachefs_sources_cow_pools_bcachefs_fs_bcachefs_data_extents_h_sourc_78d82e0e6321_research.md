# Group Research: group_209_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_data_extents_h_sourc_78d82e0e6321

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.h

## Role

`extents.h` is the central inline API for bcachefs extent values and other bkeys that contain physical pointers. It abstracts the variable-length extent-entry stream used by data extents, btree pointers, reflink values, stripe keys, reconcile metadata, checksums, and flags.

## Main Interfaces

- Defines entry iteration helpers: `extent_entry_type()`, `extent_entry_u64s()`, `extent_entry_next()`, `bkey_extent_entry_for_each()`.
- Provides typed entry casts for pointers and checksums: `entry_to_ptr()`, `entry_to_crc()`, `to_entry()`.
- Unpacks CRC/compression entries into `struct bch_extent_crc_unpacked` with `bch2_extent_crc_unpack()`.
- Defines pointer iteration APIs over many key types with `bch2_bkey_ptrs_c()`, `bch2_bkey_ptrs()`, `bkey_for_each_ptr()`, and `bkey_for_each_ptr_decode()`.
- Declares validation, text formatting, merge, swab, cut, resize, durability, device membership, pointer drop, and extent-flag helpers.
- Defines bkey operation tables for btree pointers, v2 btree pointers, extents, and reservations.

## Important Behavior

Decoded pointer iteration carries the current CRC entry forward until the next CRC entry, and also records stripe/EC metadata when a `stripe_ptr` precedes a pointer. This matches the on-disk format where checksum/compression metadata applies to following pointers.

The file treats btree pointers, user extents, reflink values, and stripe keys as “keys with pointers” while still preserving key-type-specific layouts. `bch2_bkey_ptrs_c()` is the key dispatch point.

`bch2_key_resize()` preserves extent start position while changing the endpoint, which is important because bcachefs extent bkeys store position as the end of the range.

## Invariants

- Extent entry sizes come from `c->sb.extent_type_u64s`; unknown entries can be skipped only if the superblock advertised their size.
- `extent_entry_drop()` is forbidden for stripe keys because stripe pointer layout is not compatible with generic entry movement.
- Pointer append refuses duplicate devices and enforces `BKEY_EXTENT_VAL_U64s_MAX`.
- Data classification helpers distinguish direct data, inline data, reflink pointers, reservations, allocations, and user data.
- Reconcile/poison flags are represented as extent entries and accessed through generic pointer-entry streams.

## Dependencies

This header depends on `extents_types.h`, bkey APIs, `bch_fs` superblock extent-type metadata, and many implementations in adjacent data/reconcile/trigger code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_format.h

## Role

`extents_format.h` defines the on-disk layout for bcachefs extent entries, btree pointers, reservations, and inline data. It also documents why bcachefs stores checksums in btree metadata rather than next to the data blocks.

## On-Disk Model

Extent values are streams of typed entries. Entry type is encoded by the position of the first set bit, allowing compact discrimination between entries such as pointers, CRCs, stripe pointers, reconcile metadata, and flags.

Checksum entries apply to following pointers until superseded by another checksum entry. This allows multiple replicas of the same logical extent to have different physical formats after copygc, tiering, promotion, or partial overwrites.

## Main Structures

- `struct bch_extent_crc32`, `bch_extent_crc64`, `bch_extent_crc128`: packed CRC/compression descriptors with biased size fields.
- `struct bch_extent_ptr`: physical device pointer with cached/unwritten bits, 44-bit offset, device id, and generation.
- `struct bch_extent_stripe_ptr`: EC stripe association.
- `struct bch_extent_flags`: per-extent flags, currently including `poisoned`.
- `union bch_extent_entry`: generic typed entry union.
- `struct bch_btree_ptr`, `bch_btree_ptr_v2`: btree node pointer payloads.
- `struct bch_extent`: generic user/reflink extent payload.
- `struct bch_reservation`: reservation/unwritten allocation metadata.
- `struct bch_inline_data`: inline data payload.

## Size Limits

The file defines maximum key/value sizes for extent and btree pointer values:
- `BKEY_EXTENT_PTR_U64s_MAX`
- `BKEY_EXTENT_VAL_U64s_MAX`
- `BKEY_EXTENT_U64s_MAX`
- `BKEY_BTREE_PTR_VAL_U64s_MAX`
- `BKEY_BTREE_PTR_U64s_MAX`

These limits account for maximum replicas, evacuating-device pointers, reconcile placeholder pointers, and reconcile backpointer metadata.

## Important Design Point

For checksummed or compressed extents, partial overwrites cannot simply move the physical pointer forward. Reads must fetch the full original encoded extent, verify/decompress it, then return the live portion. The CRC entry records original compressed/uncompressed sizes and the live offset.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.c

## Role

`extents_sb.c` implements the superblock field that records the size, in u64s, of each extent entry type. This supports forward-compatible parsing of extent streams containing newer entry types.

## Main Functions

- `extent_entry_u64s_known()`: returns the in-memory known size for every compiled-in `BCH_EXTENT_ENTRY_*` type.
- `bch2_sb_extent_type_u64s_to_cpu()`: loads advertised entry sizes from the superblock into `c->sb.extent_type_u64s` and sets `extent_types_known`.
- `bch2_sb_extent_type_u64s_from_cpu()`: allocates/fills the superblock field from the compiled-in entry-size table.
- `bch2_sb_extent_type_u64s_validate()`: verifies superblock-advertised sizes match compiled-in sizes for known entry types.
- `bch2_sb_extent_type_u64s_to_text()`: prints entry names and sizes.
- `bch_sb_field_ops_extent_type_u64s`: registers validate/text callbacks.

## Important Behavior

Even after reading the superblock field, the implementation overwrites all compiled-in entry sizes with `extent_entry_u64s_known()` and ensures `extent_types_known >= BCH_EXTENT_ENTRY_MAX`. Older or newer fields are only useful for parsing beyond what the current binary knows.

## Invariants

- Validation rejects mismatches for any known extent entry type.
- `from_cpu()` requires `c->sb_lock`.
- Missing allocation for the superblock field becomes `ENOSPC_sb_extent_type_u64s`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.h

## Role

`extents_sb.h` declares the extent-entry-size superblock conversion and operation table.

## API

- `bch2_sb_extent_type_u64s_to_cpu(struct bch_fs *)`
- `bch2_sb_extent_type_u64s_from_cpu(struct bch_fs *)`
- `bch_sb_field_ops_extent_type_u64s`

## Use

Included by superblock I/O and mount/update paths that need to parse, validate, or emit extent-entry size metadata.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb_format.h

## Role

`extents_sb_format.h` defines the on-disk superblock field layout for extent entry sizes.

## Structure

`struct bch_sb_field_extent_type_u64s` contains:
- common `struct bch_sb_field field`
- flexible byte array `d[]`, where each byte stores the u64 count for the corresponding extent entry type

## Purpose

The compact byte array lets old binaries skip unknown extent entry types by reading their advertised size from the superblock field.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_types.h

## Role

`extents_types.h` defines runtime-only types shared by extent read, update, movement, and failure-handling code.

## Main Types

- `struct bch_extent_crc_unpacked`: normalized checksum/compression metadata with compressed size, uncompressed size, live size, checksum type, compression type, offset, nonce, and checksum value.
- `struct extent_ptr_decoded`: decoded view of one readable pointer plus its active CRC and optional EC stripe pointer.
- `struct bch_io_failures`: per-read failure accumulator containing per-device error state and an EC diagnostic print buffer.

## Read Flags

`BCH_READ_FLAGS()` defines read behavior modifiers:
- stale-pointer retry behavior
- promotion permission
- user-mapped buffer handling
- soft/hard required read device
- last-fragment completion
- forced bounce/clone
- retry state
- poison-check bypass

These flags are used heavily by `read.c`, movement code, scrub, and self-healing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.c

## Role

`io_misc.c` implements filesystem data-range operations that mutate extents but are not normal writeback: fallocate, punch hole, truncate, insert range, and collapse range.

## Major Functions

- `bch2_extent_fallocate()`: overwrites a range with reservation keys or unwritten extents, depending on nocow support.
- `bch2_fpunch_snapshot()`: fsck-oriented punch over a snapshot range.
- `bch2_fpunch_at()` / `bch2_fpunch()`: delete or trim extent coverage over a logical byte range.
- `bch2_truncate()`: creates and resumes a logged truncate operation.
- `bch2_resume_logged_op_truncate()`: replays truncate by setting inode size then punching extents past EOF.
- `bch2_fcollapse_finsert()`: starts logged insert/collapse-range operations.
- `bch2_resume_logged_op_finsert()`: replays extent shifting and inode size adjustment.

## Fallocate Behavior

For ordinary allocation, the file emits `KEY_TYPE_reservation` keys sized to the requested sector range and desired replica count. For nocow plus unwritten-extent support, it directly allocates physical sectors, appends pointers, and marks them unwritten.

The code reserves disk space before allocator interaction, tracks sectors actually allocated, and increments the write clock after successful physical allocation.

## Logged Operations

Truncate and finsert/fcollapse are represented as logged bkeys so they can resume after crash. Both hold `snapshots.create_lock` for snapshot consistency during operation start/resume/finish.

Finsert/fcollapse has a state machine:
- start
- shift extents
- finish

It shifts extents backward or forward through the extents btree, uses delete+copy insertions, handles snapshot divergence, and updates `op->v.pos` so replay can continue.

## Invariants

- Transaction restarts are expected and retried around btree mutations.
- Extent punch uses extent-update paths for correct trimming/accounting.
- Insert-range can split compressed extents and reserves enough space when snapshot copies or compressed splits require new allocation accounting.
- Logged operation resume treats missing subvolumes differently when running from recovery versus foreground paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.h

## Role

`io_misc.h` declares the miscellaneous range-mutation APIs implemented in `io_misc.c`.

## API Surface

- Fallocate: `bch2_extent_fallocate()`
- Punch hole: `bch2_fpunch_snapshot()`, `bch2_fpunch_at()`, `bch2_fpunch()`
- Truncate logged op formatting, ops table, resume, and start: `bch2_logged_op_truncate_to_text()`, `bch2_bkey_ops_logged_op_truncate`, `bch2_resume_logged_op_truncate()`, `bch2_truncate()`
- Insert/collapse logged op formatting, ops table, resume, and start: `bch2_logged_op_finsert_to_text()`, `bch2_bkey_ops_logged_op_finsert`, `bch2_resume_logged_op_finsert()`, `bch2_fcollapse_finsert()`

## Key Detail

The logged-op bkey operation tables only provide value text formatting and minimum value size. Behavioral resume is driven by logged-op infrastructure calling the declared resume functions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.c

## Role

`keylist.c` implements dynamic storage support for `struct keylist`, a compact append-only list of packed `bkey_i` records.

## Main Functions

- `bch2_keylist_realloc()`: grows the keylist backing store by rounded power-of-two u64 capacity, preserving inline keys when transitioning to heap allocation.
- `bch2_keylist_pop_front()`: removes the first key by shrinking `top_p` and memmoving the remaining packed keys down.
- `bch2_verify_keylist_sorted()`: debug-only sorted-order verifier.

## Invariants

- `keys_p` may point to caller-provided inline storage or heap storage.
- `top_p` always points just past the last packed key.
- The debug sorted check requires strictly increasing key positions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.h

## Role

`keylist.h` provides inline operations and declarations for packed bkey lists.

## Main Helpers

- `bch2_keylist_init()` / `bch2_keylist_free()`
- `bch2_keylist_push()` / `bch2_keylist_add()`
- `bch2_keylist_empty()`
- `bch2_keylist_u64s()` / `bch2_keylist_bytes()`
- `bch2_keylist_front()`
- `for_each_keylist_key()`
- `keylist_sectors()`

## Use

Keylists are useful where code must accumulate multiple btree keys contiguously without per-key allocation overhead. They rely on the standard `bkey_next()` packed-key traversal convention.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist_types.h

## Role

`keylist_types.h` defines `struct keylist`.

## Structure

`struct keylist` stores:
- `keys` / `keys_p`: start of packed key storage, typed either as `struct bkey_i *` or `u64 *`
- `top` / `top_p`: current append cursor, typed the same way

## Design

The union layout lets callers treat the storage as packed bkeys or as raw u64s for size/capacity arithmetic.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/keylist_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.c

## Role

`migrate.c` implements data dropping during device removal or forced device-data evacuation. It removes pointers to a device from user data, metadata btree nodes, stripes, and backpointer-discovered keys while preserving durability rules unless force flags allow degradation or loss.

## Main Flow

`drop_dev_ptrs()` is the core routine:
- checks whether a key has the target device
- reassembles a mutable key with sufficient maximum buffer space
- drops the device pointer
- computes durability
- refuses loss/degradation unless permitted by flags
- marks readable keys as needing reconcile, or converts unreadable user data to an error key

User data scan:
- `bch2_dev_usrdata_drop()` walks all btrees that may contain data pointers except stripes.
- `bch2_dev_usrdata_drop_key()` updates keys with `BTREE_UPDATE_internal_snapshot_node`.

Metadata scan:
- `bch2_dev_metadata_drop()` walks btree nodes by level and updates node keys.
- Metadata loss removal is explicitly unimplemented when forced loss is requested.

Backpointer scan:
- `bch2_dev_data_drop_by_backpointers()` walks `BTREE_ID_backpointers` for one device.
- `data_drop_bp()` resolves each backpointer to its referenced key and dispatches to btree pointer, stripe invalidation, or user data pointer dropping.

## Important Behavior

Backpointer-based dropping retries up to ten full iterations because reconcile and stripe reshape can modify backpointers for read-only devices while the scan is running.

`dev_has_data()` checks actual device usage counters to decide whether the scan has converged.

## Invariants

- Stripe keys are excluded from generic user-data scans and handled through EC/stripe-specific invalidation.
- If dropping a pointer would reduce durability below policy, the operation requires force flags.
- Btree pointer keys are updated through btree-node update paths, not regular leaf updates.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.h

## Role

`migrate.h` declares device-data drop APIs.

## API

- `bch2_dev_data_drop_by_backpointers(struct bch_fs *, struct bch_dev *, unsigned, struct printbuf *)`
- `bch2_dev_data_drop(struct bch_fs *, unsigned dev_idx, unsigned flags, struct printbuf *)`

## Use

These functions are called by device removal/evacuation management paths that need to delete or invalidate references to a device.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move.c

## Role

`move.c` is the main data relocation engine. It supports copygc, evacuation, scrub, journal scrub, self-healing repair, and user-visible data jobs by reading existing extents and rewriting or validating them through `data_update`.

## Moving Context

`struct moving_context` tracks in-flight reads and writes, rate limits movement, owns a transaction, and records stats. Reads complete first, then pending writes are started from `bch2_moving_ctxt_do_pending_writes()`.

Key lifecycle:
- `bch2_moving_ctxt_init()` initializes transaction, closure, lists, waitqueue, rate/stats/write point.
- `__bch2_move_extent()` initializes a `data_update`, submits an extent read, and links the operation into context lists.
- `move_read_endio()` marks reads complete and wakes waiters.
- `move_write()` starts data-update write after read completion.
- `move_write_done()` releases accounting and handles EC allocation failures by marking reconcile pending.
- `bch2_moving_ctxt_flush_all()` waits for all reads/writes.
- `bch2_moving_ctxt_exit()` asserts counters drain and removes the context from fs diagnostics.

## Logical and Physical Scans

`bch2_move_data_btree()` walks keys in a logical btree range. It fetches inode/snapshot I/O options, updates reconcile opts if needed, asks a predicate whether to move the key, then calls `bch2_move_extent()`.

`bch2_move_data_phys()` and `__bch2_move_data_phys()` walk physical backpointers. They can scan normal device backpointers or EC-orphan stripe backpointers, resolve each backpointer to the owning key, and move matching extents. The scan also checks bucket/backpointer mismatches.

## Predicates and Operations

- `evacuate_pred()`: kills pointers on a target device.
- `evacuate_ec_orphan_pred()`: matches invalid-device pointers by EC stripe index/block.
- `evacuate_bucket_pred()`: kills noncached pointers in a specific bucket/generation.
- `scrub_pred()`: reads from a required device and scrubs only relevant checksummed extents or btree pointers.

## Journal Scrub

`bch2_scrub_journal()` walks journal flush ranges from newest to older, rereads referenced journal keys from specific devices, detects checksum errors that indicate bad flush/FUA behavior, records device flush errors in member superblock fields, and returns a rewind sequence.

`bch2_scrub_journal_do_repairs()` drains queued bad-replica repairs and rewrites affected extents with self-heal options.

## User Job Entry

`bch2_data_job()` currently handles scrub jobs, initializes stats, flushes btree interior updates, and calls physical movement with `scrub_pred()`.

## Diagnostics

`bch2_move_stats_to_text()` and `bch2_fs_moving_ctxts_to_text()` print progress, counters, limits, and in-flight data updates.

## Invariants

- Movement I/O is throttled by both sectors and I/O counts.
- Memory allocation failures are handled by waiting for I/O progress and returning nested transaction restart.
- Data update failures for individual extents are tolerated for long scans.
- EC allocation failures during movement turn into pending reconcile work rather than disappearing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move.h

## Role

`move.h` declares the data movement API and defines `struct moving_context`.

## Main Types and APIs

- `struct moving_context`: transaction, stats, rate limit, write point, in-flight read/write lists, counters, closure, waitqueue.
- `move_pred_fn`: predicate used by movement scans to decide whether and how a key should be updated.
- Movement lifecycle: `bch2_moving_ctxt_init()`, `bch2_moving_ctxt_exit()`, `bch2_moving_ctxt_flush_all()`.
- Movement operations: `bch2_move_extent()`, `bch2_move_data_btree()`, `bch2_move_data_phys()`, `bch2_evacuate_data()`, `bch2_evacuate_ec_orphan()`, `bch2_evacuate_bucket()`.
- Scrub and jobs: `bch2_scrub_journal()`, `bch2_scrub_journal_do_repairs()`, `bch2_data_job()`.
- Stats/diagnostics and fs init/exit helpers.

## Wait Macros

`move_ctxt_wait_event()` and `move_ctxt_wait_event_timeout()` always process pending writes before sleeping and unlock the long-held transaction while blocked.

## Invariants

Every in-flight operation holds a closure reference; context flush/exit waits for all references and asserts all counters are zero.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move_types.h

## Role

`move_types.h` defines shared data structures for movement stats, bucket tracking, and journal scrub repair records.

## Main Structures

- `struct bch_move_stats`: operation name, logical/physical progress position, return state, movement counters, read-error counters, and devices with uncorrected errors.
- `struct move_bucket_key`: device bucket plus generation.
- `struct move_bucket`: hashable bucket-in-flight record with sector count and atomic reference count.
- `scrub_journal_repair`: delayed repair item containing btree id, bad device mask, and padded extent key.

## Use

These types are used by copygc, scrub, journal scrub, bucket evacuation, and diagnostics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/move_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.c

## Role

`nocow_locking.c` implements bucket-level synchronization for no-COW updates versus copy/move operations. It prevents in-place updates and relocation from racing on the same physical bucket.

## Lock Model

Each bucket lock table entry contains several tracked `dev:bucket` slots. The atomic lock value sign distinguishes modes:
- positive: update locks
- negative: copy locks

Opposite signs conflict. Same-sign users can share the lock, subject to overflow checks.

## Main Functions

- `bch2_bucket_nocow_is_locked()`: checks whether a bucket has any active nocow lock.
- `__bch2_bucket_nocow_trylock()`: low-level slot lookup/allocation and mode-compatible lock acquisition.
- `__bch2_bucket_nocow_unlock()`: decrements lock count and wakes waiters when zero.
- `bch2_bkey_nocow_trylock()`: tries to lock all pointer buckets for a key, rolling back partial success.
- `bch2_bkey_nocow_lock()`: blocking ordered acquisition for all pointer buckets.
- `bch2_bkey_nocow_unlock()`: unlocks buckets for pointers previously locked.
- `bch2_nocow_locks_to_text()`: diagnostic dump.
- `bch2_fs_nocow_locking_init_early()` / `exit()`: initialize spinlocks and assert no locks remain.

## Deadlock Avoidance

Blocking acquisition first builds a list of bucket table entries, prefetches them, sorts by lock-bucket address, and takes locks in that order. If a hash bucket is full, it drops earlier locks, waits for the bucket to become empty, and retries all.

## Invariants

- The `cas[]` array is parallel to extent pointers and records exactly which device references were acquired; it is authoritative for unlock.
- Unlock asserts that remaining lock count, if nonzero, keeps the same sign.
- Exit asserts no nocow locks remain.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.h

## Role

`nocow_locking.h` declares no-COW bucket lock helpers and defines the hash lookup function.

## API

- `bucket_nocow_lock()`: hashes a device bucket into the fixed lock table.
- `BUCKET_NOCOW_LOCK_UPDATE`: flag selecting update lock mode.
- `bch2_bucket_nocow_is_locked()`
- `bch2_bucket_nocow_unlock()` / `__bch2_bucket_nocow_unlock()`
- `bch2_bkey_nocow_trylock()`, `bch2_bkey_nocow_lock()`, `bch2_bkey_nocow_unlock()`
- diagnostics and fs init/exit helpers

## Use

Used by write/update and data movement paths when physical buckets can be updated in place or copied.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking_types.h

## Role

`nocow_locking_types.h` defines the no-COW bucket lock table layout.

## Constants

- `BUCKET_NOCOW_LOCKS_BITS = 10`
- `BUCKET_NOCOW_LOCKS = 1024`
- `NOCOW_LOCK_BUCKET_SIZE = 6`

## Structures

- `struct nocow_lock_bucket`: waitlist, spinlock, six bucket identifiers, and six atomic lock counts; aligned to cache line size.
- `struct bucket_nocow_lock_table`: fixed array of hashed lock buckets.

## Design

This is a compact hash table rather than one lock per physical bucket. Collision handling is bounded by six slots per hash bucket.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/read.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/read.c

## Role

`read.c` implements bcachefs data reads. It handles extent lookup, reflink indirection, device selection, split reads, bounce buffers, checksum verification, decryption, decompression, stale-pointer detection, retry, self-healing, cache promotion, poison marking, and read diagnostics.

## High-Level Flow

`bch2_read()` walks the extents btree for the requested subvolume/inode range. For each covered fragment it:
1. resolves snapshot and extent slot,
2. follows reflink indirection if present,
3. limits the fragment to the current extent,
4. calls `__bch2_read_extent()`.

`__bch2_read_extent()` handles inline data, holes/reservations, poison checks, read-device selection, encryption-key checks, stale pointer checks in retry mode, bounce/full-read decisions, rbio allocation, bio submission, or EC reconstruction.

Completion runs through `bch2_read_endio()` and `__bch2_read_endio_work()`, which validate checksums, decrypt, decompress, copy bounced data back, and complete or retry.

## Retry and Self-Healing

Failures that should retry include transaction restart, explicit data-read retry, and block-device I/O error. `bch2_rbio_retry()` records the failed replica, clears hard device requirements, disables promotion, forces clone behavior, and retries from another replica or EC reconstruction.

If retry succeeds after checksum/I/O failure, the path can allocate a `promote_op` configured as self-heal. Failed pointers are marked in `data_update_opts.ptrs_io_error` and `ptrs_kill`.

`maybe_poison_extent()` marks an extent with `BCH_EXTENT_FLAG_poisoned` after checksum failure when the filesystem is writable, so future user reads fail unless poison checks are explicitly bypassed.

## Cache Promotion

Promotion is opportunistic and bounded by per-CPU semaphores and write refs. It is skipped when:
- the extent already has the promote target,
- the extent is unwritten,
- the target is congested,
- write refs cannot be acquired,
- rate limits or allocation fail.

Promotion uses the data update path with cached writes and may read whole extents depending on compression, errors, or the `promote_whole_extents` option.

## Encoded Extents

Checksummed, encrypted, or compressed extents often require full physical reads into bounce buffers. The completion path verifies checksum over the encoded extent, decrypts as needed, decompresses into the destination bio, or copies a selected live slice.

`bch2_rbio_narrow_crcs()` can opportunistically rewrite a CRC entry to a narrower checksum after a successful read of an uncompressed extent whose stored CRC covers more data than needed.

## Stale Pointer Handling

Read completion checks device pointer generation. If stale, normal reads enter retry. Retry-mode stale dirty pointers are treated as I/O failures and produce detailed inconsistency diagnostics.

## Diagnostics and Initialization

The file provides:
- congestion text output for latency accounting,
- read bio text formatting,
- async object list tracking for reads and promotions,
- bioset/mempool initialization and teardown for normal reads, split reads, and bounce buffers.

## Invariants

- Non-retry `__bch2_read_extent()` should not return hard errors directly; it schedules completion or retry.
- User-mapped buffers are bounced on suspicious checksum retry paths to avoid userspace scribble false positives.
- Compressed reads must bounce and read full encoded extents.
- Data-update reads may read into buffers larger than the key but reject too-small buffers.
- EC reconstruction is attempted only in retry context.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/read.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/read.h

## Role

`read.h` declares the read path API and defines `struct bch_read_bio`.

## Main Types

`struct bch_read_bio` extends `struct bio` with:
- filesystem/device references,
- timing fields,
- parent/end_io union for split reads,
- saved iterator,
- read flags and state bits,
- decoded chosen pointer,
- read/data positions,
- bversion,
- inode I/O options,
- failure and error-report pointers,
- work item.

`struct bch_read_err_report` accumulates read error bits and formatted messages under a mutex.

## Helpers

- `bch2_read_indirect_extent()`: resolves `KEY_TYPE_reflink_p` into `BTREE_ID_reflink` data.
- `bch2_read_extent()`: inline wrapper around `__bch2_read_extent()` for one extent.
- `rbio_init_fragment()` and `rbio_init()`: initialize split/parent read bios.
- `to_rbio()`: gets `bch_read_bio` from a bio.

## Constants

- `BIO_BOUNCE_BUF_POOL_LEN`
- read error bits for checksum, I/O, decompression, and EC reconstruction

## Exported Functions

- `bch2_read()`
- `__bch2_read_extent()`
- `bch2_read_err_msg_trans()`
- `bch2_promote_op_to_text()`
- `bch2_read_bio_to_text()`
- `bch2_fs_io_read_init()` / `bch2_fs_io_read_exit()`
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/read.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.c

## Role

`reconcile/check.c` verifies and repairs reconcile work indexes. It ensures that logical data keys, physical backpointers, btree-node reconcile backpointers, and stripe widening metadata agree with the current reconcile state.

## Logical Work Check

`check_reconcile_work_one()` compares:
- the data key’s computed reconcile work id,
- `BTREE_ID_reconcile_work`,
- `BTREE_ID_reconcile_hipri`,
- `BTREE_ID_reconcile_pending`.

If bits are set in the wrong work btree, fsck can call `fix_reconcile_work_btree()` to update buffered bit btrees.

It also calls `bch2_bkey_get_io_opts()` and `bch2_update_reconcile_opts()` to refresh reconcile opts on the data key.

`check_reconcile_work_data_btree()` runs this over stripes, reflink, and extents btrees.

## Physical Work Check

`check_reconcile_work_phys_one()` compares backpointer `BACKPOINTER_RECONCILE_PHYS()` state against physical work bit btrees:
- `BTREE_ID_reconcile_work_phys`
- `BTREE_ID_reconcile_hipri_phys`

It repairs incorrect physical bits through the same buffered bit modification helper.

## Btree Pointer Reconcile Backpointers

`check_reconcile_work_btree_key()` validates that btree pointer keys that need reconcile have a valid `reconcile_bp` entry and that the target `BTREE_ID_reconcile_scan` backpointer points back to the correct btree node key.

It repairs:
- missing reconcile backpointer entries,
- bad reconcile backpointer entries,
- missing scan backpointer records,
- conflicting scan positions by allocating a new empty slot.

## Stripe Widening Check

`check_stripe_can_widen()` verifies each stripe’s stored `can_widen` value against the current disk-label RW member count and EC max data block policy. If a stripes scan cookie is pending, drift is expected and not flagged.

## Entry Point

`bch2_check_reconcile_work()` runs:
1. logical data-btree work check,
2. physical backpointer work check,
3. btree pointer reconcile backpointer check,
4. reconcile scan backpointer validation,
5. stripe `can_widen` validation.

## Invariants

- Work bits must exist in exactly one reconcile work btree or none.
- Logical work positions map extents/reflink/stripes into a shared position namespace.
- Physical pending work is derived from backpointer metadata.
- Btree nodes use reconcile scan backpointers because regular work btrees cannot track them directly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.h

## Role

`check.h` declares the reconcile consistency checker.

## API

- `int bch2_check_reconcile_work(struct bch_fs *);`

## Use

Called by fsck/mount repair paths to verify reconcile work queues and related metadata.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/format.h

## Role

`reconcile/format.h` defines on-disk metadata used to track background data reconciliation: replica correction, checksum changes, compression changes, target movement, EC changes, high-priority evacuation, pending work, and btree-node backpointers.

## Main Structures

- `struct bch_extent_rebalance_v1`: older on-disk rebalance options entry.
- `struct bch_extent_reconcile`: current reconcile entry embedded in extent-entry streams.
- `struct bch_extent_reconcile_bp`: index of a reconcile scan backpointer for btree-node keys.

## Reconcile Options

`BCH_RECONCILE_OPTS()` covers:
- data replicas
- data checksum
- erasure code
- background compression
- background target
- promote target

Each option can store both a value and whether it came from inode options.

## Work Btrees

The comments define the reconcile work model:
- `BTREE_ID_reconcile_scan`: scan cookies and btree-node backpointers.
- `BTREE_ID_reconcile_work`: normal pending extent work.
- `BTREE_ID_reconcile_hipri`: high-priority pending work, especially failed-device evacuation.
- `BTREE_ID_reconcile_pending`: work blocked because a desired target is unavailable/full.

Physical variants are mapped by `reconcile_work_phys_btree[]`.

## Accounting Types

`BCH_RECONCILE_ACCOUNTING()` defines counters for replica, checksum, EC, compression, target, high priority, pending, and stripes work.

## Scan Cookies

Cookie IDs distinguish filesystem-wide scans, metadata scans, pending scans, stripe scans, and per-device scans.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.c

## Role

`reconcile/trigger.c` translates extent state and I/O policy into reconcile metadata, work queues, backpointers, and accounting. It is called from btree triggers, fsck/update scans, foreground writes, option-change propagation, and movement paths.

## Validation and Formatting

- `bch2_extent_reconcile_validate()` rejects bad pending, hipri, or replica fields.
- `bch2_extent_rebalance_v1_to_text()` and `bch2_extent_reconcile_to_text()` print old and new reconcile entries.
- `bch2_bkey_reconcile_opts()` finds the reconcile entry in a key’s extent-entry stream.
- `bch2_bkey_reconcile_work_id()` returns none/hipri/normal/pending for a key.

## Reconcile Backpointers

Btree pointer keys need reconcile scan backpointers because normal leaf work bit btrees track extents/reflink/stripes, not btree nodes.

Functions:
- `bch2_bkey_get_reconcile_bp_pos()`
- `bch2_bkey_set_reconcile_bp()`
- `reconcile_bp_add()`
- `reconcile_bp_del()`
- `reconcile_bp_get_key()`

These maintain `BTREE_ID_reconcile_scan` entries that point back to btree node keys.

## Trigger Effects

`__bch2_trigger_extent_reconcile()` handles two classes of side effects:
- Transactional work index updates: moving logical keys between normal/hipri/pending bit btrees, or adding/removing btree-node reconcile backpointers.
- Transactional/GC accounting: updating `reconcile_work` counters and device-leaving counters based on old/new reconcile entries and key sizes.

`bch2_trigger_extent_reconcile()` skips the full trigger when neither old nor new reconcile metadata needs work or device accounting.

## Determining Need for Reconcile

`bch2_bkey_needs_reconcile()` compares actual key pointers and encoded formats against target I/O options:
- checksum type,
- compression type,
- background target,
- data replicas/durability,
- erasure-code state,
- evacuating/bad devices,
- invalid-device placeholders,
- poisoned/unwritten/incompressible constraints.

It sets:
- `need_rb` option bits,
- `hipri` for degraded/evacuating cases,
- `ptrs_moving` for pointers moving off devices/targets,
- `pending` preservation where applicable,
- invalid-device placeholder add/drop count.

## Writing Reconcile Entries

`bch2_bkey_set_needs_reconcile()` mutates a key to add, update, or drop `bch_extent_reconcile`, and may add/drop `BCH_SB_MEMBER_INVALID` placeholder pointers for durability accounting.

`bch2_extent_trigger_set_needs_reconcile()` grows trigger-mutated keys as needed and fills reconcile metadata automatically.

`bch2_update_reconcile_opts()` is the scanner/update path; for leaf keys it creates a mutable copy and updates it, while for btree-node keys it updates the node key through btree-node update infrastructure.

## Option Lookup

`bch2_bkey_get_io_opts()` computes applicable I/O options for metadata, user extents, and reflink data:
- metadata uses filesystem metadata options,
- user data can use per-inode snapshot-specific options,
- reflink values can preserve inode-derived options stored in reconcile metadata.

`per_snapshot_io_opts` caches inode options while scanning natural key order.

## Safety Checks

`new_needs_rb_allowed()` prevents unexpected new reconcile needs unless they are justified by option-change scans, foreground-write allowances, EC creation timing, device scan cookies, or cached scan-cookie state. Otherwise fsck reports incorrect/missing reconcile options.

## Invariants

- Pending reconcile requires `need_rb`.
- Hipri reconcile is tied to replica/durability work.
- Reconcile entries are omitted when not needed, except reflink values may retain inode-derived options.
- Btree pointer reconcile backpointers are transactional and must move when work id changes.
- Pending work suppresses target/replica accounting in favor of pending accounting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.h

## Role

`reconcile/trigger.h` declares reconcile trigger APIs and provides mapping helpers for reconcile work positions and option caching.

## Position Mapping

- `data_to_rb_work_pos()`: maps extents, reflink, and stripes into the shared reconcile work namespace.
- `rb_work_to_data_pos()`: reverses that mapping into a `bbpos`.
- `rb_work_id()`: maps a reconcile entry to none, pending, hipri, or normal.
- `rb_work_id_phys()`: suppresses pending for physical work tracking.

## Utility Helpers

- `io_opts_to_reconcile_opts()`: converts inode I/O options into an extent reconcile entry.
- `rb_bp()`: constructs a btree-node reconcile backpointer payload.
- `extent_has_rotational()`: checks whether any pointer references a rotational device.
- `rb_needs_trigger()`: true when reconcile entry needs trigger side effects.

## Declared APIs

- validation/text: `bch2_extent_reconcile_validate()`, `bch2_extent_rebalance_v1_to_text()`, `bch2_extent_reconcile_to_text()`
- reconcile lookup/work id: `bch2_bkey_reconcile_opts()`, `bch2_bkey_reconcile_work_id()`
- backpointer management: `bch2_bkey_get_reconcile_bp_pos()`, `bch2_bkey_set_reconcile_bp()`, `reconcile_bp_add()`, `reconcile_bp_del()`, `reconcile_bp_get_key()`
- trigger/update: `__bch2_trigger_extent_reconcile()`, `bch2_trigger_extent_reconcile()`, `bch2_update_reconcile_opts()`, `bch2_bkey_set_needs_reconcile()`, `bch2_extent_trigger_set_needs_reconcile()`
- option lookup: `bch2_bkey_get_io_opts()`

## Snapshot Option Cache

`struct per_snapshot_io_opts` caches filesystem and inode options while scanning keys. It tracks current inode, metadata/user mode, scan-cookie cache bits, per-device cookie cache, and a dynamic array of snapshot-specific inode options.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/types.h

## Role

`reconcile/types.h` defines in-memory filesystem state for the reconcile subsystem.

## Main Structure

`struct bch_fs_reconcile` contains:
- reconcile thread pointer and kick counter,
- running flag,
- wait timing fields,
- current phase,
- work position and work stats,
- progress indicator,
- scan start/end and scan stats,
- in-flight option-change scan hashtable plus lock,
- battery/power notification state when power-supply support is enabled.

## Use

This state backs the background reconcile worker and option-change scan tracking. It coordinates pending work scans, progress reporting, and power-aware behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/types.h -->