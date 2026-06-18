# Group Research: bcachefs-tools fs/data extents, IO, movement, locking, read, and reconcile

Scope: `Docs/research_subset_a.md`; source tree `sources/cow-pools/bcachefs-tools` is included in subset A.

All listed source files were read completely. This group covers bcachefs extent on-disk encoding and iteration helpers, sparse-file operations, device data removal, data movement/scrub plumbing, no-COW bucket locking, the data read pipeline, and reconcile metadata/checking.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents.h

## Purpose
Core header for generic bcachefs keys that carry extent pointers. It defines entry traversal, CRC unpacking, pointer iteration/decoding, key classification helpers, durability/device queries, pointer mutation helpers, bkey ops declarations, and generic extent cutting/resizing helpers.

## Main Interfaces and Behavior
- Extent-entry access uses `extent_entry_type()`, `extent_entry_u64s()`, `extent_entry_bytes()`, `extent_entry_next()`, and `extent_entry_next_safe()`. Runtime entry sizes come from `c->sb.extent_type_u64s`, which lets newer entry layouts be skipped by older tools when known through the superblock.
- `__extent_entry_insert()` and `extent_entry_drop()` physically insert/remove variable-sized entries inside a bkey value and adjust `k->k.u64s`. `extent_entry_drop()` rejects `KEY_TYPE_stripe` because stripe pointer layout is not compatible with the generic memmove path.
- Type helpers distinguish pointer, stripe pointer, and CRC entries. `bch2_extent_crc_unpack()` converts on-disk `crc32`, `crc64`, and `crc128` entries into `struct bch_extent_crc_unpacked`, defaulting to an unencoded full-key extent when no CRC entry applies.
- `bch2_bkey_ptrs_c()` returns the pointer-entry span for btree pointers, extents, stripes, reflink values, and v2 btree pointers. Non-pointer-bearing key types return `{ NULL, NULL }`.
- The macro family `bkey_extent_entry_for_each*`, `bkey_for_each_ptr*`, `bkey_for_each_ptr_decode*`, and `bkey_for_each_crc*` is the canonical way to walk interleaved CRC/stripe/pointer entries. The decoded iterator carries the currently active CRC and EC association for each pointer.
- Defines bkey ops macros for `btree_ptr`, `btree_ptr_v2`, `extent`, and `reservation`, wiring validation, text rendering, endian swabbing, triggers, merge, compat, and repair hooks.
- Classification helpers include `bkey_is_btree_ptr()`, `bkey_extent_is_direct_data()`, `bkey_is_user_data()`, `bkey_extent_is_inline_data()`, `bkey_extent_is_data()`, `bkey_extent_is_allocation()`, `bkey_extent_is_unwritten()`, and `bkey_extent_is_reservation()`.
- Device/durability surface includes declarations for pointer counts, compression sectors, replicas, per-device durability, key durability, readability, device membership, target membership, stale/extra durability dropping, and text/validation routines.
- Mutation helpers append pointers, append decoded pointers, drop pointers/devices/EC masks, match extents and pointers, set cached state, and manage extent flags. The `bch2_bkey_drop_ptrs*` macros deliberately restart iteration after each removal because entry addresses shift.
- Generic extent helpers classify overlap, cut front/back, resize while preserving start offset, and read/set extent flags stored in an optional `flags` entry.

## Dependencies and Coupling
This header is heavily coupled to `bcachefs_format.h` key types through `bkey_s_*` conversions and to reconcile through entry types declared in `extents_format.h`. Many operations assume a visible `struct bch_fs *c` variable in iterator macros, which is an important call-site convention.

## Risks and Invariants
- `extent_entry_u64s()` BUGs if an entry type is at or above `c->sb.extent_types_known`; callers must use safe iteration when parsing possibly unknown data.
- Pointer decoding relies on CRC entries applying to all following pointers until the next CRC entry.
- Append/drop helpers assume caller-provided buffers are large enough; several paths enforce `BKEY_EXTENT_VAL_U64s_MAX` or explicit buffer u64 capacities.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_format.h

## Purpose
Defines the on-disk/in-memory packed format for bcachefs extent entries, pointers, checksums, extent flags, btree pointer values, reservations, and inline data.

## Main Interfaces and Behavior
- Extensive documentation explains why checksums live in btree keys instead of adjacent to data: the key establishes what data should be read, so stale or wrong-location data can be detected.
- For trimmed checksummed or compressed extents, CRC entries preserve original compressed/uncompressed size and live offset so reads can fetch/decode the full encoded extent and return only the live subset.
- `BCH_EXTENT_ENTRY_TYPES()` assigns compact entry type IDs for `ptr`, `crc32`, `crc64`, `crc128`, `stripe_ptr`, `rebalance_v1`, `flags`, `reconcile`, and `reconcile_bp`; the type is encoded as the first set bit in the entry word.
- CRC formats scale by space: `bch_extent_crc32` is compact and has no nonce, `crc64` has a 10-bit nonce, and `crc128` has wider sizes/offsets plus full `struct bch_csum`.
- `struct bch_extent_ptr` stores cached/unwritten bits, 44-bit sector offset, 8-bit device id, and 8-bit generation. `struct bch_extent_stripe_ptr` stores EC stripe block, redundancy, and index.
- `struct bch_extent_flags` currently exposes the `poisoned` flag.
- `union bch_extent_entry` overlays all entry layouts and provides endian-aware access to the type word.
- Value layouts include `bch_btree_ptr`, `bch_btree_ptr_v2`, `bch_extent`, `bch_reservation`, and `bch_inline_data`.
- Size macros bound maximum extent and btree-pointer value sizes. They explicitly account for evacuating-device pointers and reconcile placeholder pointers coexisting with normal replicas.

## Dependencies and Coupling
Includes `reconcile/format.h`, so reconcile entries are part of the generic extent-entry union and maximum-size calculations.

## Risks and Invariants
- Bitfield layouts are endian-specific and packed/aligned to 8 bytes.
- Maximum value-size constants are critical allocation bounds used by movement, reconcile, and extent mutation paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.c

## Purpose
Implements the superblock field that records extent-entry sizes in u64s. This lets code parse extents containing entry types from newer versions by knowing their serialized length.

## Main Interfaces and Behavior
- `extent_entry_u64s_known()` maps each known `BCH_EXTENT_ENTRY_*` type to `sizeof(struct bch_extent_*) / sizeof(u64)`.
- `bch2_sb_extent_type_u64s_nr_entries()` computes the number of stored byte entries in the variable-sized superblock field.
- `bch2_sb_extent_type_u64s_to_cpu()` reads the superblock field into `c->sb.extent_type_u64s` and `extent_types_known`, then overwrites all currently known entries with compiled-in sizes and ensures at least `BCH_EXTENT_ENTRY_MAX` known entries.
- `bch2_sb_extent_type_u64s_from_cpu()` allocates/min-sizes the superblock field under `c->sb_lock` and writes compiled-in sizes.
- Validation checks stored sizes against compiled-in known sizes and reports `invalid_sb_extent_type_u64s` on mismatch.
- Text rendering prints each recorded entry type name, or an unknown type label, with its u64 size.

## Dependencies and Coupling
Uses `data/extents_sb.h`, superblock field helpers from `sb/io.h`, and `bch2_extent_entry_types[]`.

## Risks and Invariants
- Known entry sizes must match compiled structures exactly; a mismatch indicates incompatible/corrupt superblock metadata.
- The `to_cpu()` function currently writes compiled sizes for all known entries regardless of what was read, while preserving the maximum known count.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.h

## Purpose
Public declarations for the extent-entry-size superblock field support.

## Main Interfaces
- `bch2_sb_extent_type_u64s_to_cpu(struct bch_fs *)`
- `bch2_sb_extent_type_u64s_from_cpu(struct bch_fs *)`
- `bch_sb_field_ops_extent_type_u64s`

## Dependencies
Relies on `struct bch_fs` and `struct bch_sb_field_ops` declarations from broader bcachefs headers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb_format.h

## Purpose
Defines the on-disk superblock field payload for extent-entry u64 sizes.

## Main Interfaces
- `struct bch_sb_field_extent_type_u64s` embeds `struct bch_sb_field field` followed by flexible byte array `d[]`, where each byte stores the u64 length for the entry type at the same index.

## Notes
The format is intentionally compact because extent entry sizes are small and indexed by `BCH_EXTENT_ENTRY_*`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_sb_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_types.h

## Purpose
Shared type definitions for decoded extent CRCs, decoded pointers, accumulated IO failures, and read flags.

## Main Interfaces and Behavior
- `struct bch_extent_crc_unpacked` normalizes encoded extent metadata: compressed size, uncompressed size, live size, checksum/compression types, offset, nonce, and checksum.
- `struct extent_ptr_decoded` combines a physical pointer, currently active CRC, optional EC stripe pointer, EC reconstruction flags, and retry count.
- `struct bch_io_failures` tracks per-device read/checksum/EC failures plus a print buffer for EC diagnostics. It has one more slot than `BCH_REPLICAS_MAX`.
- `BCH_READ_FLAGS()` defines read-path flags: retry on stale pointer, allow promotion, user-mapped destination, soft/hard read-device requirement, last fragment, forced bounce/clone, retry mode, and poison-check bypass.

## Dependencies
Includes `bcachefs_format.h` for checksum and replica constants.

## Risks and Invariants
- `bch_io_failures` is part of retry/self-heal selection; callers must initialize/exit its print buffer through helpers in `extents.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/io_misc.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/io_misc.c

## Purpose
Implements miscellaneous data operations: fallocate, hole punching, truncate, and file insert/collapse. Truncate and insert/collapse are logged operations so they can resume after crash.

## Main Interfaces and Behavior
- `bch2_extent_fallocate()` overwrites a range with zeroes/reservation. If no-COW unwritten extents are supported and requested, it allocates real extent pointers, marks them unwritten, and updates allocation clocks/open buckets. Otherwise it writes a reservation key.
- Fallocate computes missing replicas relative to existing fully allocated pointers, obtains a disk reservation before allocator interaction, and commits via `bch2_extent_update()`.
- `bch2_fpunch_snapshot()` is an fsck helper that deletes/trims extents over a snapshot range using max-sized delete keys and `bch2_extent_trim_atomic()`.
- `bch2_fpunch_at()` punches a file range for a subvolume/inode by resolving the subvolume snapshot, peeking extents up to an end position, constructing delete keys, and applying `bch2_extent_update()` in restart-aware loops.
- `bch2_fpunch()` is the external wrapper that creates a transaction and extent iterator.
- Truncate support includes `bch2_logged_op_truncate_to_text()`, `truncate_set_isize()`, `__bch2_resume_logged_op_truncate()`, `bch2_resume_logged_op_truncate()`, and `bch2_truncate()`. The resume path first updates inode size, then punches extents past rounded-up new size.
- File insert/collapse support includes logged-op rendering, `adjust_i_size()`, `__bch2_resume_logged_op_finsert()`, `bch2_resume_logged_op_finsert()`, and `bch2_fcollapse_finsert()`.
- The insert/collapse state machine has `LOGGED_OP_FINSERT_start`, `shift_extents`, and `finish` states. It updates inode size, optionally punches collapsed range, shifts extents backward or forward, stores progress in `op->v.pos`, and updates inode timestamps/size at finish.
- Both truncate and finsert/fcollapse hold `c->snapshots.create_lock` while starting/resuming/finishing because logged ops are not atomic with snapshot creation.

## Dependencies and Coupling
Depends on extent update, allocator reservations, inode read/write, logged ops, subvolume snapshot lookup, write points, and reconcile trigger support.

## Risks and Invariants
- Restart handling is explicit; some transaction restarts are converted to success at API boundaries after progress has been made.
- Insert/collapse must handle snapshot mismatches by reserving extra space when copying extents into a new snapshot.
- Compressed extent splits may require additional disk reservation because live data has to be rewritten.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/io_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/io_misc.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/io_misc.h

## Purpose
Declares fallocate, hole punch, truncate, and insert/collapse helpers, plus bkey ops for logged operations.

## Main Interfaces
- `bch2_extent_fallocate()`
- `bch2_fpunch_snapshot()`, `bch2_fpunch_at()`, `bch2_fpunch()`
- `bch2_logged_op_truncate_to_text()`, `bch2_resume_logged_op_truncate()`, `bch2_truncate()`
- `bch2_logged_op_finsert_to_text()`, `bch2_resume_logged_op_finsert()`, `bch2_fcollapse_finsert()`
- `bch2_bkey_ops_logged_op_truncate` and `bch2_bkey_ops_logged_op_finsert` expose text renderers and minimum value sizes.

## Dependencies
Relies on transaction, iterator, subvolume inode, inode opts, printbuf, bkey, and write point types from the surrounding bcachefs codebase.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/io_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist.c

## Purpose
Implements dynamic storage and front removal for `struct keylist`, a compact list of packed `bkey_i` values.

## Main Interfaces and Behavior
- `bch2_keylist_realloc()` grows backing storage by rounded power-of-two u64 count. It uses inline storage until the requested size exceeds inline capacity, then `krealloc()`s heap storage and copies existing inline keys on first promotion.
- `bch2_keylist_pop_front()` removes the first key by shrinking `top_p` and memmoving subsequent packed keys down.
- In debug builds, `bch2_verify_keylist_sorted()` asserts that adjacent keys are strictly ordered by position.

## Risks and Invariants
- `keys_p` points either to caller-provided inline storage or heap storage; free/realloc logic depends on comparing against the inline pointer.
- Packed key iteration uses each key's `k.u64s`; corrupt lengths would break traversal.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist.h

## Purpose
Inline API for initializing, freeing, appending, iterating, and measuring `struct keylist`.

## Main Interfaces and Behavior
- `bch2_keylist_init()` sets both bottom and top pointers to inline storage.
- `bch2_keylist_free()` releases heap storage only when the list was promoted out of inline storage.
- `bch2_keylist_push()` advances `top` by `bkey_next(top)`, and `bch2_keylist_add()` copies a packed key into `top` before pushing.
- `bch2_keylist_empty()`, `bch2_keylist_u64s()`, `bch2_keylist_bytes()`, and `bch2_keylist_front()` expose simple state.
- `for_each_keylist_key()` walks packed keys from `keys` to `top`.
- `keylist_sectors()` sums `k.size` across all stored keys.
- `bch2_verify_keylist_sorted()` is either debug verification or a no-op.

## Risks and Invariants
- Callers must ensure enough capacity, usually via `bch2_keylist_realloc()`, before appending.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/keylist_types.h

## Purpose
Defines `struct keylist`, a packed bkey list represented as u64 pointers and bkey pointers over the same memory.

## Main Interfaces
- `keys/keys_p` union points to the first stored key/u64.
- `top/top_p` union points one past the final stored key/u64.

## Notes
The union layout makes byte/u64 sizing and packed `bkey_i` traversal cheap without separate metadata.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/keylist_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/migrate.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/migrate.c

## Purpose
Implements data removal from a device, either by scanning data btrees or by using backpointers. It drops device pointers from user data, metadata btree pointers, and stripes while enforcing degradation/loss force flags.

## Main Interfaces and Behavior
- `drop_dev_ptrs()` reassembles a key, removes pointers for a target device, checks resulting durability against metadata/data replica requirements, and either marks the key for reconcile or converts unreadable user data to an error key.
- Metadata and data use different force flags: metadata loss/degradation versus data loss/degradation.
- `drop_btree_ptrs()` updates an in-memory btree node key after dropping device pointers.
- `bch2_dev_usrdata_drop_key()` updates a normal data key; deleted keys have size forced to zero because this path does not go through the extent overwrite iterator.
- `bch2_dev_btree_drop_key()` resolves a backpointer to a btree node and drops the device pointer from that node key.
- `bch2_dev_usrdata_drop()` scans all pointer-bearing btrees except stripes and applies device-pointer drops with progress tracking.
- `bch2_dev_metadata_drop()` scans btree nodes at all levels and drops metadata pointers. It does not implement forced metadata-lost removal.
- `data_drop_bp()` resolves a backpointer and dispatches to btree pointer drop, stripe invalidation, or user data drop.
- `bch2_dev_data_drop_by_backpointers()` scans the backpointer namespace for the device, repeatedly flushing and rescanning until the device has no data buckets. It tracks progress by `dev_data_buckets()` lows and aborts after 10 stalled scans.
- `bch2_dev_data_drop()` performs full user-data then metadata scans without relying on backpointers.

## Dependencies and Coupling
Uses backpointer lookup, btree node update, write-buffer flushing, EC stripe invalidation, reconcile option setting, durability accounting, and progress indicators.

## Risks and Invariants
- Backpointer scanning races with reconcile and stripe reshape; the function intentionally retries based on observed remaining device data rather than a fixed iteration cap.
- Open stripes are skipped and `bch2_fs_ec_flush_outstanding()` is called before rescanning.
- Metadata-lost removal is explicitly unimplemented.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/migrate.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/migrate.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/migrate.h

## Purpose
Public declarations for device data-drop operations.

## Main Interfaces
- `bch2_dev_data_drop_by_backpointers(struct bch_fs *, struct bch_dev *, unsigned flags, struct printbuf *)`
- `bch2_dev_data_drop(struct bch_fs *, unsigned dev_idx, unsigned flags, struct printbuf *)`

## Notes
The backpointer variant takes a live `struct bch_dev *`; the full scan variant takes a device index.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/migrate.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/move.c

## Purpose
Implements generic data movement, physical/logical data scans, device and bucket evacuation, scrub operations, journal scrub, repair scheduling, and movement status rendering.

## Main Interfaces and Behavior
- `bch2_data_ops_strs[]` maps ioctl data operation IDs to names.
- Moving context lifecycle:
  - `bch2_moving_ctxt_init()` creates a private transaction, closure, waitqueue, IO lists/counters, rate/stats references, and links the context into `c->moving_context_list`.
  - `bch2_moving_ctxt_exit()` flushes all IO, asserts counters are zero, unlinks, resets the transaction, and zeroes the context.
  - `bch2_moving_ctxt_flush_all()` drains pending reads/writes and waits on the closure.
- Read/write pipeline:
  - `__bch2_move_extent()` allocates a `data_update`, initializes it, starts a read via `__bch2_read_extent()`, and accounts read IO.
  - `move_read_endio()` marks the read done and wakes waiters.
  - `bch2_moving_ctxt_do_pending_writes()` converts completed reads into writes.
  - `move_write_done()` accounts write completion, handles EC allocation failure by marking pending reconcile, exits the data update, and releases closure refs.
- `bch2_move_extent()` handles data extents, btree pointer rewrites, and scrub reads. ENOMEM waits for in-flight IO and restarts.
- `bch2_move_extent_pred()` fetches IO opts, updates reconcile opts, commits lazily, calls a caller-supplied predicate to fill `data_update_opts`, traces the decision, and starts movement when the predicate returns positive.
- `bch2_move_ratelimit()` honors copygc waits, kthread stop/freezer state, configured rate delays, and global in-flight byte/IO limits.
- `bch2_move_data_btree()` walks logical data btrees and btree roots at a level, moving keys selected by a predicate.
- Physical scanning is driven by `struct bp_walk` and `__bch2_move_data_phys()`, which walks either normal device backpointers or EC-orphan stripe backpointers, validates bucket/backpointer mismatches, resolves original keys, and calls movement predicates.
- Evacuation predicates select pointers by device, by removed-device EC stripe association, or by exact bucket/generation. Public helpers include `bch2_evacuate_data()`, `bch2_evacuate_ec_orphan()`, and `bch2_evacuate_bucket()`.
- `scrub_pred()` sets up hard-device reads and skips non-checksummed non-btree data for scrub.
- `bch2_scrub_journal()` walks replayed journal flush ranges newest-first, checks extents referenced by journal keys, records checksum failures by device, updates member flush error counters, and reports a rewind sequence after bad flush ranges.
- `bch2_scrub_journal_do_repairs()` drains queued repair records and self-heals bad replicas through `scrub_journal_repair_one()`.
- `bch2_data_job()` currently dispatches `BCH_DATA_OP_scrub`.
- Text/status helpers render movement counters and in-flight read/write state. Filesystem init/exit manage moving context lists and the journal scrub repair darray.

## Dependencies and Coupling
This file is central glue for allocator/write points, backpointers, btree read/update/interior code, data update, read path, reconcile triggers, EC, journal replay, copygc, and ioctl data jobs.

## Risks and Invariants
- Each in-flight IO holds a closure reference; counters must be balanced before context exit.
- Physical backpointer walks must tolerate write-buffer races and topology changes.
- Movement predicates return positive for “move this key”, zero for skip, and negative for errors; several expected per-extent failures are downgraded so scans continue.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/move.h

## Purpose
Public movement API plus `struct moving_context`, wait macros, predicate signature, and movement/scrub declarations.

## Main Interfaces and Behavior
- `struct moving_context` tracks a transaction, list linkage, caller IP, rate limiter, stats, write point, copygc wait preference, closure, IO lists, sequence counter, atomic read/write sector and IO counters, mutex, and waitqueue.
- `move_ctxt_wait_event_timeout()` and `move_ctxt_wait_event()` drain pending writes before waiting and unlock the transaction during long waits.
- `move_pred_fn` lets callers inspect a btree key and fill `data_update_opts` for selected movement.
- Declares context lifecycle, pending write handling, rate limiting, extent movement, logical and physical scan helpers, evacuation helpers, journal scrub/repair, ioctl data job dispatch, stats rendering, and filesystem move init/exit.

## Dependencies
Includes ioctl data definitions, bucket helpers, bbpos, btree iterator, data update, and movement types.

## Risks and Invariants
- Wait macros assume the context’s transaction can be dropped during long waits.
- The comments document the in-flight IO accounting contract used by both extent moves and stripe repairs.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/move_types.h

## Purpose
Defines data structures shared by movement, scrub, and repair code.

## Main Interfaces
- `struct bch_move_stats` stores operation name, physical/logical position, return code, moved/raced/seen/error counters, and devices with uncorrected errors.
- `struct move_bucket_key` and `struct move_bucket` identify and track buckets currently in movement with hash linkage and refcount.
- `scrub_journal_repair` stores a btree id, bad device mask, and padded key for later repair.
- `DEFINE_DARRAY(scrub_journal_repair)` creates the dynamic array type used by journal scrub repair queues.

## Notes
The stats union supports both logical `bbpos` progress and physical `dev/offset` progress.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/move_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.c

## Purpose
Implements hashed bucket locks used to coordinate no-COW copy/update access to buckets referenced by extent pointers.

## Main Interfaces and Behavior
- Locks are stored in hashed `nocow_lock_bucket` entries. Each slot records a bucket id and signed atomic count.
- Positive counts represent update locks; negative counts represent copy locks. Opposite signs conflict, same signs can nest/share.
- `bch2_bucket_nocow_is_locked()` checks whether a bucket has any active slot count.
- `__bch2_bucket_nocow_unlock()` subtracts the matching signed count, asserts sign consistency, and wakes waiters when a slot reaches zero.
- `__bch2_bucket_nocow_trylock()` finds or allocates a slot under spinlock, rejects opposite-sign contention, detects overflow/sign changes, and reports bucket-full or contended errors.
- `bch2_bkey_nocow_unlock()` unlocks all pointer buckets for which the parallel `cas[]` device-ref array indicates a lock was taken.
- `bch2_bkey_nocow_trylock()` attempts to lock all pointer buckets and unwinds already-taken locks on failure.
- `bch2_bkey_nocow_lock()` first tries the fast path; on failure it builds a bucket list, sorts by lock-bucket address to avoid deadlocks, waits on contention, and retries all locks when a hash bucket is full.
- `bch2_nocow_locks_to_text()` renders active locks and coalesces empty entries.
- Filesystem init/exit initialize spinlocks and assert all locks are released at exit.

## Dependencies and Coupling
Uses extent pointer iteration, device bucket helpers, closures waitlists, darray utilities, and timing stats.

## Risks and Invariants
- The `cas[]` array is authoritative for which device refs/locks exist; code avoids re-deriving devices from `c->devs[]` because device removal may clear entries while refs remain.
- Sorting by hash-bucket address is the deadlock-avoidance mechanism for multi-bucket locks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.h

## Purpose
Public API and hashing helper for no-COW bucket locking.

## Main Interfaces
- `bucket_nocow_lock()` hashes a packed bucket id with `hash_64()` into `BUCKET_NOCOW_LOCKS` buckets.
- `BUCKET_NOCOW_LOCK_UPDATE` selects update-lock sign; absence is copy-lock sign.
- Declares bucket lock query/unlock, bkey pointer lock/unlock/trylock, text rendering, and filesystem init/exit.

## Dependencies
Includes bcachefs core, allocation background helpers, lock types, and Linux hash helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking_types.h

## Purpose
Defines the no-COW lock table layout.

## Main Interfaces
- `BUCKET_NOCOW_LOCKS_BITS` is 10, so the table has 1024 hash buckets.
- Each `nocow_lock_bucket` has a waitlist, spinlock, six bucket ids, and six atomic counts, cacheline-aligned.
- `struct bucket_nocow_lock_table` embeds the fixed array.

## Notes
The six-entry per-hash-bucket limit is handled at runtime by waiting for an empty bucket when full.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/read.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/read.c

## Purpose
Implements the bcachefs data read pipeline: extent lookup, device selection, IO submission, checksum/decryption/decompression, split/bounce handling, retry, self-heal, cache promotion, stale pointer handling, poisoning, and initialization of read biosets/mempools.

## Main Interfaces and Behavior
- The file-level documentation states the intended behavior: reads are transparent and self-healing; checksum/IO failures retry other replicas and can rewrite bad copies; read target selection adapts by device latency.
- Latency/congestion helpers compute per-device congestion and probabilistically mark targets congested, used to avoid promotion to overloaded targets. `bch2_dev_congested_to_text()` renders metrics when latency accounting is enabled.
- Promotion/self-heal:
  - `should_promote()` rejects already-promoted, unwritten, or congested-target reads.
  - `__promote_alloc()` creates a `promote_op` backed by `data_update`, either for cached promotion or self-heal after failures.
  - `promote_alloc()` decides whether to promote full extents, forces bounce/full read as needed, and marks the original read as self-healing for failure recovery.
  - Completion flows through `promote_start()`, `promote_start_work()`, `promote_done()`, and `promote_free()`.
- Error and retry:
  - `bch2_read_err_msg_trans()` formats inode/offset-aware errors.
  - `bch2_rbio_error()` either queues retry work for retryable errors or completes with failure.
  - `bch2_rbio_retry()` redoes lookup/read with `BCH_READ_in_retry`, clears hard device requirement, forces clone, disables promotion, tracks failures, and emits success/self-heal/error diagnostics.
  - `rbio_mark_io_failure()` records device/EC/checksum failures and propagates IO-error masks to parent data updates.
- Checksum/poison/narrowing:
  - `maybe_poison_extent()` marks extents with checksum errors as `BCH_EXTENT_FLAG_poisoned` when mounted read-write and updates a parent data update copy if needed.
  - `bch2_rbio_narrow_crcs()` can rechecksum an uncompressed checksummed extent and update its CRC entry after a full read, reducing future read amplification.
- End IO:
  - `bch2_read_endio()` accounts block IO completion, restores iterators, checks stale pointers, and punts to high-priority or unbound workqueues when checksum/compression/encryption/promotion/narrowing require process context.
  - `__bch2_read_endio_work()` validates checksum, decrypts, decompresses when necessary, copies bounced data, verifies data-update decompression when requested, and completes or returns retryable errors.
- Read submission:
  - `__bch2_read_extent()` handles inline data, poison checks, pointer selection via `bch2_bkey_pick_read_device()`, missing encryption keys, stale dirty pointers, read-full/bounce decisions, EC reconstruction reads, direct block IO submission, and retry-mode synchronous completion.
  - `read_extent_rbio_alloc()` allocates or reuses rbios, handles promotion rbios, clone/bounce decisions, adjusts CRC/pointer offsets for partial unencoded reads, sets bio sector/endio, traces, and increments clocks.
  - `read_extent_inline()` fills zeros before/after inline payload as needed.
  - `read_extent_hole()` zero-fills holes/reservations and reports overwritten keys to data-update retries.
- Top-level `bch2_read()` walks extent slots for a subvolume inode, resolves reflink indirect extents through `bch2_read_indirect_extent()`, splits a bio across extents, maintains previous-read failure state in retry mode, and calls `__bch2_read_extent()` for each fragment.
- Debug/text/init:
  - `bch2_read_bio_to_text()` and atomic helpers render rbio timing, state flags, selected pointer, and bio.
  - `bch2_fs_io_read_init()` allocates per-CPU promotion semaphores, bounce page mempool, and read/split biosets.
  - `bch2_fs_io_read_exit()` releases those resources.

## Dependencies and Coupling
Coupled to checksum/encryption, compression, EC reconstruction, btree extent lookup, subvolume snapshots, data update, write promotion, device IO refs, allocator targets, and error accounting.

## Risks and Invariants
- If reading into user-mapped buffers and checksum fails without bounce, the read is retried with forced bounce because userspace might have modified the buffer.
- For compressed/checksummed extents, partial logical reads may require full encoded extent reads.
- Retry mode is the only mode where `__bch2_read_extent()` returns many errors directly; non-retry mode generally completes through bio endio.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/read.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/read.h

## Purpose
Public structures and entry points for the bcachefs data read path.

## Main Interfaces and Behavior
- Defines bounce buffer pool length and read error bitmasks for checksum, IO, decompression, and EC reconstruction.
- `struct bch_read_err_report` aggregates errors and messages under a mutex.
- `struct bch_read_bio` extends `struct bio` with filesystem/device refs, timing, parent/endio union, saved iterator, extent offsets, flags/state bits, selected decoded pointer, read/data positions, inode opts, failure/report pointers, and work item.
- State bits distinguish data update reads, verify-decompress, promotion, bounce, split, CRC narrowing, observed errors, self-heal, and workqueue context.
- `bch2_read_indirect_extent()` resolves `KEY_TYPE_reflink_p` through `bch2_lookup_indirect_extent()`, switches data btree to reflink, and reassembles the target extent.
- Declares error message rendering, `__bch2_read_extent()`, inline `bch2_read_extent()`, top-level `bch2_read()`, rbio fragment/original initializers, promotion/read text renderers, and fs read init/exit.

## Risks and Invariants
- Split rbios store `parent`; unsplit rbios store original `end_io` in the same union.
- `rbio_init_fragment()` inherits opts and error reporting from the original rbio.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/read.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.c

## Purpose
Fsck/checker support for reconcile metadata. It verifies and repairs reconcile work btrees, physical reconcile work, btree-node reconcile backpointers, reconcile-scan backpointers, and stripe widening metadata.

## Main Interfaces and Behavior
- `fix_reconcile_work_btree()` sets or clears a bit in a reconcile work btree depending on whether that btree is the desired location.
- `check_reconcile_work_one()` parallel-walks a data btree and the normal/hipri/pending reconcile work btrees, maps data positions to reconcile work positions, computes where a key should be queued via `bch2_bkey_reconcile_work_id()`, repairs mismatches, and refreshes reconcile options.
- `check_reconcile_work_data_btree()` applies the above to a full data btree with progress and write-buffer flush tracking.
- `check_reconcile_work_phys_one()` validates physical reconcile work btrees against backpointer `BACKPOINTER_RECONCILE_PHYS()` state.
- `check_reconcile_work_phys()` scans normal backpointers and physical reconcile work/hipri btrees.
- `check_reconcile_work_btree_key()` refreshes reconcile opts on btree pointer keys and validates/repairs their `reconcile_bp` extent entries and corresponding `BTREE_ID_reconcile_scan` backpointer records.
- `check_reconcile_work_btrees()` walks all live btree roots and interior nodes by level to validate btree pointer reconcile state.
- `check_reconcile_btree_bp()` and `check_reconcile_btree_bps()` validate reconcile scan backpointers by resolving them back to btree node keys.
- `check_stripe_can_widen_one()` recomputes each stripe’s `can_widen` from disk label RW-member count and EC policy; it skips errors if a stripe scan cookie is already pending.
- `check_stripe_can_widen()` scans stripes with a widen cache.
- `bch2_check_reconcile_work()` orchestrates checks over stripes, reflink, extents, physical reconcile work, btrees, reconcile backpointers, and stripe widening.

## Dependencies and Coupling
Depends on reconcile trigger/work helpers, btree bit btrees, write-buffer flush state, EC stripe widen helpers, progress indicators, and fsck error machinery.

## Risks and Invariants
- Data positions are remapped into shared reconcile work keyspace; stripes/reflink/extents occupy different ranges through `data_to_rb_work_pos()`.
- The checker repairs by mutating bit btrees and btree-node keys; transaction restarts and commits are intentionally frequent.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.h

## Purpose
Declares the top-level reconcile fsck/check entry point.

## Main Interface
- `int bch2_check_reconcile_work(struct bch_fs *);`
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/format.h

## Purpose
Defines on-disk reconcile/rebalance extent entries and the btree/work/accounting IDs used to track background reconciliation.

## Main Interfaces and Behavior
- Header comments describe reconcile metadata:
  - extents carry `bch_extent_reconcile` when background processing is pending;
  - indirect extents may carry reconcile opts to preserve owning inode IO-path options;
  - scan cookies represent option-change propagation work;
  - separate normal, hipri, pending, and physical work btrees track work.
- `struct bch_extent_rebalance_v1` is an older packed format with IO options and “from inode” bits.
- `struct bch_extent_reconcile` stores type, moving pointer bitmask, hipri/pending bits, `need_rb` bitmask, six IO options, and six “from inode” markers.
- `struct bch_extent_reconcile_bp` stores an index into reconcile scan backpointer space for btree pointer reconcile work.
- `BCH_RECONCILE_OPTS()` enumerates persisted IO options: data replicas, checksum, erasure coding, background compression, background target, promote target.
- `BCH_RECONCILE_ACCOUNTING()` enumerates accounting buckets for replicas, checksum, erasure code, compression, target, high priority, pending, and stripes.
- `RECONCILE_WORK_IDS()` defines none, hipri, normal, and pending. Static maps convert work IDs to logical and physical reconcile work btree IDs.
- Scan-cookie constants reserve cookies for filesystem, metadata, pending, stripes, and per-device scans.

## Risks and Invariants
- `pending` work is not represented in the physical work map.
- The bitfield width of targets/options bounds representable option values.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.c

## Purpose
Implements validation, text rendering, extraction, trigger accounting, work-btree updates, btree reconcile backpointer management, IO option lookup, and mutation of extent reconcile metadata.

## Main Interfaces and Behavior
- `bch2_extent_reconcile_validate()` rejects pending without need, hipri without data-replicas work, and zero data replicas.
- `bch2_bkey_reconcile_opts()` finds a reconcile entry among a key’s extent entries. `bch2_bkey_reconcile_work_id()` maps stripe `needs_reconcile` or extent reconcile bits to a work ID.
- Text renderers output v1 rebalance or current reconcile options, including inode-derived markers and targets.
- `rb_accounting_counters()` converts a reconcile entry to accounting counters, adding pending/high-priority accounting and suppressing target/replica counters while pending.
- Reconcile backpointer helpers:
  - `bch2_bkey_get_reconcile_bp_pos()` returns `(work_id, bp_index)`.
  - `bch2_bkey_set_reconcile_bp()` adds, updates, or drops the `reconcile_bp` entry in a key.
  - `reconcile_bp_add()` allocates a backpointer record in `BTREE_ID_reconcile_scan`.
  - `reconcile_bp_del()` validates and deletes a reconcile scan backpointer.
  - `reconcile_bp_get_key()` resolves a reconcile backpointer to a btree node key and repairs stale/missing records.
- `__bch2_trigger_extent_reconcile()` is the core trigger. Transactionally, it moves leaf keys between normal/hipri/pending work bit btrees or manages btree-node reconcile backpointers. In transactional/GC modes it also updates reconcile accounting and dev-leaving counters for moving pointers.
- `bch2_bkey_needs_reconcile()` computes desired reconcile state from current IO opts, key pointers, CRC/compression, targets, device evacuation, durability, EC, invalid placeholder pointers, unwritten/incompressible/poisoned state, and old pending/hipri state.
- `new_needs_rb_allowed()` fsck-validates new reconcile requirements, allowing known exceptions for option-change scans, foreground writes, missing initial EC on foreground writes, option-change races, indirect extents, and scan cookies.
- `bch2_bkey_set_needs_reconcile()` mutates a mutable key: add/update/drop reconcile entries, set stripe `needs_reconcile`, add or remove `BCH_SB_MEMBER_INVALID` placeholder pointers, and update `trans->extra_disk_res` when placeholders add durability obligations.
- `bch2_extent_trigger_set_needs_reconcile()` grows trigger-owned new keys when needed and fills reconcile metadata lazily from IO opts.
- `bch2_update_reconcile_opts()` updates leaf keys or btree node keys already in a scan/check path, using transaction kmalloc and btree node update for interior levels.
- `bch2_bkey_get_io_opts()` derives effective IO options for metadata, reflink/indirect, and user data. With `per_snapshot_io_opts`, it caches inode options by inode and snapshot ancestry during ordered scans. For reflink values, persisted reconcile options can override inode-derived fields and are re-run through IO option fixups.

## Dependencies and Coupling
Depends on extent entry iteration, disk accounting, btree bit updates, btree node update, inode option lookup, snapshot ancestry, reconcile scan cookies, compression/checksum option helpers, and fsck error reporting.

## Risks and Invariants
- New reconcile requirements are tightly controlled; unexpected missing/incorrect reconcile opts are treated as fsck errors unless a scan cookie or recognized race explains them.
- Multiple `BCH_SB_MEMBER_INVALID` placeholder pointers may require a reconcile incompat feature; otherwise the function clamps updates.
- Trigger behavior differs for leaf data and interior btree nodes; btree nodes need explicit reconcile scan backpointers because they cannot be tracked in the same leaf work bitsets.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.h

## Purpose
Public reconcile trigger API, position mapping helpers, IO-option cache types, and helpers for converting IO opts to reconcile entries.

## Main Interfaces and Behavior
- `data_to_rb_work_pos()` maps stripes, reflink, and extents into a shared reconcile work position space. Stripes use inode 0, reflink positions are shifted, and extents start at `BCACHEFS_ROOT_INO`.
- `rb_work_to_data_pos()` reverses that mapping into `struct bbpos`.
- `rb_work_id()` maps a reconcile entry to none/pending/hipri/normal, and `rb_work_id_phys()` suppresses pending for physical work.
- `io_opts_to_reconcile_opts()` copies six IO options and their from-inode flags into a `bch_extent_reconcile` entry with the correct type bit.
- Declares reconcile validation, backpointer get/set/add/delete/resolve helpers, text renderers, reconcile option extraction, work ID calculation, trigger implementation, IO option lookup, reconcile mutation, and extent-trigger lazy mutation.
- `rb_needs_trigger()` quickly checks whether a reconcile entry has work or moving pointers.
- Inline `bch2_trigger_extent_reconcile()` extracts old/new reconcile entries and calls the heavy trigger only when necessary.
- Defines `enum set_needs_reconcile_ctx` for option change, indirect option change, foreground write, and other contexts.
- `struct per_snapshot_io_opts` caches effective IO options across ordered scans, including filesystem options, per-inode snapshot entries, scan-cookie cache bits, and device-cookie cache.

## Risks and Invariants
- The position mapping is shared by checkers, triggers, and work processors; changing it would require migrating reconcile work btrees.
- `per_snapshot_io_opts` caches positive scan-cookie/device-cookie state but deliberately avoids trusting cached non-existence in some paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/types.h

## Purpose
Defines runtime state for the reconcile background subsystem.

## Main Interfaces
- `struct bch_fs_reconcile` stores the reconcile thread pointer/kick counter, running flag, wait timing, current phase, current work position/stats/progress, scan range/stats, in-flight option-change scan tracking, and power-supply state.
- `scans_in_flight` is an rhashtable protected by `scans_in_flight_lock`, with an init-done flag.
- Optional power-supply notifier state is compiled under `CONFIG_POWER_SUPPLY`.

## Dependencies
Includes bbpos types, move stats, progress indicators, mutexes, and rhashtable types.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/reconcile/types.h -->