# Group Research: group_231_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_journal_reclaim_c_525d4c8906f3

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/bcachefs-tools`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.c

This file implements journal space accounting, discard advancement, journal entry pin management, and journal reclaim for bcachefs-tools.

Key responsibilities:
- Computes per-device and aggregate journal availability through `bch2_journal_dev_buckets_available()`, `journal_dev_space_available()`, `__journal_space_available()`, and `bch2_journal_space_available()`.
- Maintains journal pressure flags and write watermark state in `bch2_journal_set_watermark()`.
- Drives discard of no-longer-dirty journal buckets with `bch2_journal_discard_work()`, `bch2_journal_do_discards()`, and per-device discard work.
- Tracks pinned journal sequences and advances `last_seq` / `last_seq_ondisk`.
- Provides APIs for pin set, add, update, copy, drop, replay put, and flush synchronization.
- Implements background and direct reclaim, including the reclaim kthread lifecycle.
- Exposes diagnostic text for pins, reclaim counters, blocked time stats, and reclaim thread backtraces.

Important control flow:
- Space accounting advances `dirty_idx` and `dirty_idx_ondisk` based on `last_seq` and `last_seq_ondisk`.
- Available space is calculated from the top `metadata_replicas` journal devices, then constrained by the smallest aligned bucket size.
- Dirty journal space is capped by a RAM-derived budget for soft throttling, while `next_entry` remains uncapped to avoid self-deadlock.
- Reclaim chooses a `seq_to_flush` from half-full journal devices and pin FIFO pressure.
- `journal_flush_pins()` selects eligible unflushed pins by type and sequence, calls the pin flush callback, then moves pins to flushed lists unless they were dropped or rearmed.
- `bch2_journal_flush_pins()` loops through pin types from lower priority to higher order so shutdown flushing can converge even when pin flushing generates more pins.

Important invariants:
- Journal bucket ring indexes obey `discard_idx <= dirty_idx_ondisk <= dirty_idx <= cur_idx` modulo the ring.
- The last bucket is held back unless writing a new `last_seq` will free another bucket.
- Pin FIFO entries hold a count for the journal entry itself, btree nodes, key cache entries, and replay references.
- `pin->seq == 0` means inactive.
- Pin list locks are acquired in sequence order when moving/copying pins across lists.
- Reclaim holds `j->reclaim_lock` and uses `PF_MEMALLOC_NOFS` to avoid recursion through memory reclaim.
- Flush callbacks must be present because diagnostics identify pins by callback function.

Dependencies:
- Uses allocator/device membership helpers, replica accounting, btree key cache and write buffer flush hooks, journal core state, counters, and member device APIs.
- Uses kernel workqueues, kthreads, closures, wait queues, RCU, spinlocks, mutexes, and printbuf diagnostics.

Research notes:
- This is one of the main liveness files for the journal. Incorrect space accounting can stall journal writers or cause premature throttling.
- The RAM/4 dirty budget comments document a subtle design: it influences the watermark ratio but must not clamp hard entry reservation capacity.
- Pin flushing order is part of clean shutdown correctness because btree writes can recursively create more journal dependencies.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.h

This header exports journal reclaim, space accounting, pin management, discard, and diagnostics APIs.

Key responsibilities:
- Defines `JOURNAL_PIN`.
- Provides `journal_reclaim_kick()`, which marks reclaim kicked and wakes the reclaim thread.
- Declares space accounting APIs:
  - `bch2_journal_dev_buckets_available()`
  - `bch2_journal_set_watermark()`
  - `bch2_journal_space_available()`
- Initializes pin list entries with `journal_pin_list_init()`.
- Provides pin helpers:
  - `journal_pin_active()`
  - `journal_seq_pin()`
  - `__bch2_journal_pin_put()`
  - `bch2_journal_pin_add()`
  - `bch2_journal_pin_update()`
- Defines `replicas_entry_refs` and a preallocated darray type used when releasing journal replica refs.
- Declares reclaim thread start/stop, direct reclaim, pin flush, device pin flush, discard, and text diagnostic functions.

Important invariants:
- `journal_seq_pin()` asserts the requested sequence is inside the pin FIFO range.
- Pin add only moves a pin to an older sequence if inactive or currently newer.
- Pin update only moves a pin to a newer sequence if inactive or currently older.
- `journal_pin_list_init()` resets unflushed/flushed lists, count, unreplayed state, replica-device count, and byte accounting.

Dependencies:
- Requires `struct journal`, `struct journal_device`, `struct journal_entry_pin_list`, `struct journal_entry_pin`, and journal type definitions from surrounding journal headers.

Research notes:
- The inline helpers encode the public semantics for pin movement and are used by hot btree and key-cache paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/sb.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/sb.c

This file implements superblock field operations for journal bucket lists and journal bucket ranges.

Key responsibilities:
- Validates legacy `BCH_SB_FIELD_journal` bucket lists.
- Validates `BCH_SB_FIELD_journal_v2` compact bucket ranges.
- Converts sorted bucket arrays into compact journal v2 superblock ranges with `bch2_journal_buckets_to_sb()`.
- Sorts and rewrites journal superblock fields with `bch2_sb_journal_sort()`.

Validation behavior:
- Legacy journal field validation:
  - Copies buckets into a darray.
  - Sorts them.
  - Rejects sector/bucket zero.
  - Rejects buckets before member `first_bucket`.
  - Rejects buckets beyond member `nbuckets`.
  - Rejects duplicates.
- Journal v2 validation:
  - Expands each entry into a start/end range.
  - Rejects empty or wrapped ranges.
  - Rejects start zero.
  - Rejects ranges before first bucket or past device end.
  - Rejects overlapping ranges.
  - Rejects total bucket count above `UINT_MAX`.

Conversion behavior:
- `bch2_journal_buckets_to_sb()` deletes both journal fields when no buckets remain.
- Non-empty bucket arrays are compacted into contiguous ranges and stored as `journal_v2`.
- Legacy `journal` is deleted when v2 is written.

Important invariants:
- Callers must hold `c->sb_lock` when writing journal buckets to a superblock.
- `bch2_sb_journal_sort()` requires a clean filesystem and not read-write mounted.
- Journal bucket arrays are sorted before v2 compaction during sort/repair.

Dependencies:
- Uses superblock field resize/delete helpers, member lookup, darrays, sort helpers, and online member iteration.

Research notes:
- This file is format-compatibility glue between old explicit bucket lists and newer compact range encoding.
- Validation is device-local: it checks against the superblock member at `sb->dev_idx`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/sb.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/sb.h

This header exposes helpers and field operations for journal superblock fields.

Key responsibilities:
- Defines `bch2_nr_journal_buckets()` for legacy explicit journal bucket arrays.
- Defines `bch2_sb_field_journal_v2_nr_entries()` for compact range entries.
- Declares:
  - `bch_sb_field_ops_journal`
  - `bch_sb_field_ops_journal_v2`
  - `bch2_journal_buckets_to_sb()`
  - `bch2_sb_journal_sort()`

Important invariants:
- Entry counts are derived from `vstruct_end()` and variable-length trailing arrays.
- Null field pointers produce zero entries.

Dependencies:
- Includes superblock I/O and vstruct helpers.

Research notes:
- This header is small but central to journal field parsing by both validator and mutator paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/sb.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.c

This file implements persistent and in-memory journal sequence blacklisting.

Purpose:
- Prevents reuse of journal sequence numbers associated with btree bsets that were flushed newer than the newest reliable journal entry.
- Lets recovery ignore bsets whose newest journal sequence was not safely committed.
- Records blacklisted ranges in the superblock so future mounts preserve the decision.

Key responsibilities:
- Adds and merges blacklist ranges in `bch2_journal_seq_blacklist_add()`.
- Builds an in-memory Eytzinger-ordered lookup table with `bch2_blacklist_table_initialize()`.
- Finds the next blacklisted or nonblacklisted sequence.
- Tests whether a sequence is blacklisted and optionally marks its table entry dirty.
- Reports the last blacklisted sequence.
- Validates and prints the superblock blacklist field.
- Garbage-collects obsolete blacklist entries with `bch2_blacklist_entries_gc()`.

Important behavior:
- Added ranges merge with overlapping or contiguous existing ranges.
- Superblock resize happens under `sb_lock` with `PF_MEMALLOC_NOFS`.
- Adding a blacklist range sets the `journal_seq_blacklist_v3` feature bit, writes the superblock, and rebuilds the table.
- Lookup uses Eytzinger search by range start or end for fast queries.
- GC keeps entries that were dirtied in memory or whose end is newer than `oldest_seq_found_ondisk`.

Important invariants:
- Superblock blacklist entries must be sorted, non-empty ranges with `start < end`, and non-overlapping.
- The in-memory table count must match the superblock field count during GC.
- Blacklist range `end` is exclusive in lookup logic.

Dependencies:
- Uses journal state, superblock field resize/write helpers, Eytzinger array utilities, and darray/array insertion helpers.

Research notes:
- The long file comment documents the correctness reason: journal sequence ordering must dominate btree node flush ordering after crash recovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.h

This header declares journal sequence blacklist APIs and a helper for counting on-disk entries.

Key responsibilities:
- Provides `blacklist_nr_entries()` to count `journal_seq_blacklist_entry` records in a variable-length superblock field.
- Declares sequence lookup APIs:
  - `bch2_journal_seq_next_blacklisted()`
  - `bch2_journal_seq_next_nonblacklisted()`
  - `bch2_journal_seq_is_blacklisted()`
  - `bch2_journal_last_blacklisted_seq()`
- Declares mutation and initialization:
  - `bch2_journal_seq_blacklist_add()`
  - `bch2_blacklist_table_initialize()`
  - `bch2_blacklist_entries_gc()`
- Exposes `bch_sb_field_ops_journal_seq_blacklist`.

Important invariants:
- The count helper returns zero for a null field.
- Entry count is computed from `vstruct_end()` and the trailing entry array size.

Dependencies:
- Requires the on-disk blacklist format and superblock field ops types.

Research notes:
- This is the narrow public API between journal read/recovery, btree validation, and superblock persistence.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist_format.h

This header defines the on-disk journal sequence blacklist superblock field.

Key definitions:
- `struct journal_seq_blacklist_entry`
  - `start`: little-endian inclusive range start.
  - `end`: little-endian exclusive range end.
- `struct bch_sb_field_journal_seq_blacklist`
  - Standard superblock field header.
  - Flexible array of blacklist entries.

Important invariants:
- Ranges are validated elsewhere as sorted, non-empty, and non-overlapping.
- Fields are endian-stable on disk.

Research notes:
- This is pure persistent format. Changes affect mount/recovery compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/seq_blacklist_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/types.h

This header defines the central in-memory journal state types.

Key definitions:
- Sequence and ring constants:
  - `JOURNAL_SEQ_MAX`
  - `JOURNAL_STATE_BUF_BITS`
  - `JOURNAL_STATE_BUF_NR`
  - `JOURNAL_STATE_BUF_MASK`
- `struct journal_buf`: one in-flight journal entry buffer, its jset data, destination key, held devices, failure state, waiters, sizing, reservation, flush, write, and compaction flags.
- `struct journal_ringbuf`: reservation fastpath ring slot.
- `enum journal_pin_type`: btree levels, key cache, and other pin categories.
- `struct journal_entry_pin_list`: per-sequence pin count, unflushed/flushed lists, replay state, replica device info, and byte accounting.
- `struct journal_entry_pin`: individual pinned object with flush callback and sequence.
- `struct journal_res`: reservation descriptor.
- `union journal_res_state`: atomic reservation word with packed offset, ring index, and per-ring-slot counts.
- Journal entry sizing and sentinel constants.
- `struct journal_space` and `enum journal_space_from`.
- Journal flags generated by `JOURNAL_FLAGS()`.
- `struct journal_bio`: bio wrapper for journal writes.
- `struct journal_rewind_range`.
- `struct journal`: full embedded filesystem journal state.
- `struct journal_device`: per-device journal bucket ring state and bio set.
- `struct journal_entry_res`: persistent entry reservation descriptor.
- `struct journal_start_info`: journal read/recovery start window summary.

Important invariants:
- `journal_buf.cas[]` mirrors extent pointers in append order so device objects remain accessible while write I/O refs are held.
- Reservation state has endian-aware bitfield ordering so the on-word bit layout is identical on little and big endian.
- `cur_entry_offset` sentinel values encode blocked, closed, and error states.
- `in_flight` FIFO front is `seq_ondisk + 1`; back is `cur_seq + 1`.
- `pin` FIFO tracks dirty journal sequences until all dependent btree/key-cache/replay refs are dropped.
- `journal_device` ring indexes are ordered as `discard_idx <= dirty_idx_ondisk <= dirty_idx <= cur_idx` modulo ring.
- `journal_start_info` partitions sequences into replay, blacklist, and future write zones.

Dependencies:
- Pulls in replica, allocation, extent, device, FIFO, cacheline, and workqueue types.

Research notes:
- This header contains detailed comments documenting race/lifetime assumptions for journal buffers and reservation state.
- Many files in this group depend on the exact layout and semantics defined here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/validate.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/validate.c

This file validates and formats journal sets and journal entries.

Key responsibilities:
- Builds contextual journal validation error messages with `bch2_journal_entry_err_msg()`.
- Repairs invalid entry/key ranges by zeroing or compacting entries when fsck policy allows.
- Validates btree key entries, btree root entries, blacklist entries, usage entries, clock entries, device usage entries, log entries, overwrite/log-bkey/write-buffer key entries, datetime entries, and rewind entries.
- Provides per-entry text formatting through `bch2_journal_entry_to_text()`.
- Validates full `jset` structures with `bch2_jset_validate()`.
- Performs early validation during journal scan with `bch2_jset_validate_early()`.

Important validation behavior:
- Key validation rejects zero `k->u64s`, key overrun, non-current key format, and bkey validator errors.
- Read validation applies compatibility conversion before validation; write validation converts after validation.
- Invalid btree key entries can shrink or delete the bad key payload while preserving the surrounding journal structure.
- Btree root validation treats bad root sizing specially by clearing the entry contents but keeping the root entry marker.
- Blacklist v1/v2 entries enforce exact expected sizes and valid range order.
- Usage/data-usage entries enforce minimum sizes and validate replica descriptors.
- Clock entries require exact size and `rw <= 1`.
- Device usage entries require minimum size and zero padding.
- `bch2_jset_validate()` checks magic, metadata version compatibility, checksum type validity, and `last_seq <= seq` for flush entries.
- Early validation checks magic/version and truncates entries that overrun the remaining bucket sectors.

Important invariants:
- `JOURNAL_ENTRY_NONE` means no matching journal magic.
- `JOURNAL_ENTRY_BAD` means structurally present but invalid/corrupt.
- `jset->last_seq` is ignored for noflush entries.
- Entry traversal stops or truncates when `vstruct_next(entry)` exceeds the jset end.
- Validation error handling differs for read versus write through the macro in `validate.h`.

Dependencies:
- Uses bkey compatibility/validation, fsck error infrastructure, replica validation, journal format enums, and printbuf formatting.

Research notes:
- This is both a validator and a controlled repair layer for journal metadata.
- The dispatch table is generated from `BCH_JSET_ENTRY_TYPES()`, so adding a journal entry type requires matching validate/to_text functions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/validate.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/validate.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/validate.h

This header declares journal validation APIs and defines the journal validation error macro.

Key responsibilities:
- Declares `bch2_journal_entry_err_msg()`.
- Defines `journal_entry_err()` and `journal_entry_err_on()`.
- Declares:
  - `bch2_journal_entry_validate()`
  - `bch2_journal_entry_to_text()`
  - `bch2_jset_validate()`
  - `bch2_jset_validate_early()`
- Defines `JOURNAL_ENTRY_NONE` and `JOURNAL_ENTRY_BAD`.

Important behavior:
- On read validation, errors are routed through `mustfix_fsck_err()`.
- On write validation, errors increment superblock fsck error counters and can mark the filesystem inconsistent, returning `fsck_errors_not_fixed`.
- Error messages include journal version, jset sequence, entry type, and entry offset when available.

Dependencies:
- Requires fsck validation flags, superblock error IDs, journal format types, and printbuf utilities.

Research notes:
- The macro centralizes policy differences between accepting/repairing on read and refusing corrupt metadata on write.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/validate.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/write.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/write.c

This file implements journal write allocation, preparation, checksum/encryption, submission, completion, and write scheduling.

Key responsibilities:
- Allocates journal write destinations across eligible devices and replicas.
- Advances devices to a new journal bucket when current bucket space is insufficient.
- Reallocates journal buffers and resizes the btree write buffer as needed.
- Prepares jsets for write by compacting entries, converting write-buffer keys, adding btree roots, datetime, usage, and clock entries.
- Sets journal magic/version/endian/checksum/encryption flags and computes checksums.
- Submits journal writes through bios, including optional separate preflush bios.
- Handles write completion, replica accounting, degraded writes, errors, emergency read-only transition, and in-flight FIFO advancement.
- Decides whether a journal entry should be flush or noflush and schedules writes from the oldest unallocated sequence.

Important control flow:
- `journal_write_alloc()` first tries the configured metadata/foreground target, then falls back to all devices.
- `__journal_write_alloc()` pins each selected device with a write I/O ref, appends an extent pointer, records the device in `w->cas[]`, updates bucket free space and bucket sequence, and accumulates durability.
- `bch2_journal_write_prep()` flushes write-buffer keys into the write buffer, converts them to btree keys, updates btree roots, marks empty entries, appends common superblock entries, and enforces reserved space.
- `bch2_journal_write_checksum()` validates before checksum when encryption or old metadata versions require it, encrypts payload, computes checksum, then zero-fills sector padding.
- `journal_write_submit()` maps the journal buffer into one or more bios per pointer and submits with sync/idle/meta flags plus FUA/PREFLUSH as needed.
- `journal_write_done()` advances `seq_ondisk`, `flushed_seq_ondisk`, `last_seq_ondisk`, `rewind_seq_ondisk`, releases replica refs in order, wakes waiters, recycles buffers, and recalculates journal space.
- `bch2_journal_do_writes_locked()` starts writes only when no reservations remain for the sequence and flush ordering permits.

Important invariants:
- `write_done` means all post-completion bookkeeping is finished, not merely that the bio completed.
- Flush writes are serialized so `seq_ondisk + 1 == seq` before submission.
- Separate flush is used when more than one read-write member exists.
- Clean superblock state delays journal replica marking until after write completion.
- If `nochanging` mode is enabled, I/O refs are released and completion runs without submitting bios.
- On demoting a flush to noflush, waiters and `must_flush` are carried forward to the next eligible entry.

Dependencies:
- Uses allocator target selection, device write refs, extent pointers, checksums/encryption, btree roots, btree write buffer, journal reclaim/validation, clean superblock helpers, counters, closures, bios, and block flush/FUA semantics.

Research notes:
- The completion path is race-sensitive. Comments document why `write_done` is set only after replica refs and sequence advancement are safe.
- The write scheduler balances latency through noflush writes while preserving enough flush writes for recovery and clean/dirty transitions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/write.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/write.h

This header declares journal write scheduling APIs and provides `jset_entry_init()`.

Key responsibilities:
- Declares closure callback `bch2_journal_write`.
- Declares:
  - `bch2_journal_do_writes_locked()`
  - `bch2_journal_do_writes()`
- Defines `jset_entry_init()` to append and zero a new variable-sized journal entry.

Important invariants:
- `jset_entry_init()` rounds entry size up to u64 alignment.
- `entry->u64s` counts payload u64s after shared entry fields, so it stores `u64s - 1`.
- The caller owns ensuring the target buffer has enough reserved space.

Dependencies:
- Requires vstruct helpers and journal entry format definitions.

Research notes:
- This helper is used by journal write preparation and clean-superblock entry construction.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/opts.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/opts.c

This file implements bcachefs option tables, parsing, formatting, superblock synchronization, mount parsing, and runtime option hooks.

Key responsibilities:
- Defines string tables for error actions, degraded actions, fsck fix modes, version upgrade modes, features, compat bits, btree IDs, checksum/compression/hash/data/member/reconcile/journal-scrub options, and dentry types.
- Provides bounds-checked print helpers for option-like enums.
- Implements the custom `fix_errors` option parser/printer.
- Builds `bch2_opt_table[]` from `BCH_OPTS()`.
- Provides option lookup, synonym lookup, validation, parsing, and text formatting.
- Applies option structs and generic get/set by option ID.
- Reads options from superblock/member/ext fields and writes options back to them.
- Parses mount option strings, including boolean `nofoo` negation and old mount option handling.
- Runs pre/post option hooks that trigger reconciliation scans, device state changes, feature checks, discard propagation, copygc/reconcile wakeups, and capacity recalculation.
- Builds inode I/O option snapshots and prints inode options.
- Provides option change locking with an odd/even cookie.

Important parsing behavior:
- Boolean options accept a local strict table: `0`, `1`, `false`, `no`, `true`, `yes`.
- Unsigned integer options reject missing values and negative strings.
- Human-readable integer options use `bch2_strtou64_h()`.
- String options use `match_string()` against choice tables.
- Bitfield options use `bch2_read_flag_list()`.
- Function-backed options delegate to option-specific parse/validate/text callbacks.
- Unknown mount options are ignored or rejected based on caller mode.
- Some options that require an open filesystem can be deferred into `parse_later`.

Important option hooks:
- I/O-affecting options bracket reconcile scans before/after changes.
- Metadata target/checksum/replica changes trigger metadata reconcile.
- Device durability changes can trigger pending and device reconcile scans.
- `state` changes call device state transition logic.
- Compression and erasure-code options check/set required feature state.
- `casefold_disabled` rejects mounts when casefolding is already in use.
- Runtime discard changes can propagate to member superblock fields.
- Incompatible `version_upgrade` triggers superblock upgrade logic.
- `read_only` wakes reconcile.

Important invariants:
- Options use paired `_defined` bits so partial option structs can override defaults selectively.
- Superblock storage transforms support sector shifts, ilog2 encoding, and one-biased values.
- Device option writes require an existing member slot.
- Runtime sysfs writability is represented through option flags and attribute mode.
- `bch2_io_opts_fixups()` disables compression/checksum/EC under nocow and caps EC replicas to RAID6-style limits.

Dependencies:
- Uses option definitions from `opts.h`, superblock/member/ext accessors, recovery pass names, allocation targets, compression parsing, reconcile/copygc hooks, and mount parser helpers.

Research notes:
- This is the central policy file for option side effects. Updating an option definition in `opts.h` without matching parse/hook implications here can silently miss required background repair work.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/opts.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/opts.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/opts.h

This header defines the bcachefs option schema and public option APIs.

Key responsibilities:
- Declares option string tables and enum-print helpers.
- Defines option flags, option types, function-backed option callbacks, and `struct bch_option`.
- Defines `BCH_FIX_ERRORS_OPTS()` and `enum fsck_err_opts`.
- Defines `BCH_OPTS()`, the central macro table for all filesystem, inode, mount, runtime, format, and device options.
- Generates:
  - `enum bch_opt_id`
  - `struct bch_opts_mask`
  - `struct bch_opts`
  - `struct bch_inode_opts`
- Declares parse, validate, formatting, superblock get/set, mount parse, hook, and inode option APIs.
- Provides `opt_defined()`, `opt_get()`, `opt_set()`, and `bch2_opts_empty()`.
- Defines `bch2_io_opts_fixups()` and an `opt_change_lock` guard.

Major option categories:
- Filesystem geometry and metadata: block size, btree node size, metadata replicas/checksum/target.
- Data I/O policy: data replicas, checksum, compression, targets, erasure coding, nocow.
- Directory/security features: str_hash, casefold, ACLs, quotas.
- Mount/recovery behavior: degraded, fsck, fix_errors, norecovery, journal rewind, recovery pass controls.
- Journal behavior: flush delay, reclaim delay, flush disabled, scrub recent journal entries.
- Background work: copygc, reconcile, auto snapshot deletion.
- Device options: state, bucket size, durability, data allowed, discard, rotational.
- Tool/test options: direct I/O, no data I/O, stdio pointer, retain/read journal controls.

Important invariants:
- Undefined option values fall back to `bch2_opts_default`.
- `BCH_OPTS()` is the single source for option IDs, struct fields, table entries, default values, flags, help, and superblock binding.
- `BCH_INODE_OPTS()` determines which options are inherited into inode I/O policy.
- `bch2_io_opts_fixups()` normalizes background target/compression and disables incompatible data features under nocow.
- Options with `OPT_SB_FIELD_SECTORS`, `OPT_SB_FIELD_ILOG2`, or `OPT_SB_FIELD_ONE_BIAS` require transforms when reading/writing superblock fields.

Dependencies:
- Includes bcachefs on-disk format definitions, Linux sysfs/log2/sizes helpers, and option-specific callback declarations provided elsewhere.

Research notes:
- This header is effectively the option ABI definition for format, mount, sysfs, and inherited inode behavior.
- The macro table approach reduces duplication but makes option changes high impact.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/opts.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/clean.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/clean.c

This file implements the `BCH_SB_FIELD_clean` superblock section used after clean shutdown.

Purpose:
- Stores btree roots and other journal-like entries in the superblock so a cleanly shut down filesystem can avoid reading/replaying the journal at mount.

Key responsibilities:
- Late-validates clean-section journal entries with `bch2_sb_clean_validate_late()`.
- Finds btree root entries inside either a clean section or a journal set.
- Verifies clean superblock roots against the final journal entry with `bch2_verify_superblock_clean()`.
- Reads and validates a clean section with `bch2_read_superblock_clean()`.
- Appends common journal/superblock entries through `bch2_journal_super_entries_add_common()`.
- Provides superblock field validate/to_text ops.
- Marks the filesystem dirty or clean with `bch2_fs_mark_dirty()` and `bch2_fs_mark_clean()`.

Clean section contents:
- Usage entry for key version.
- Read and write I/O clock entries.
- Btree root journal entries.
- Zero-filled tail padding.

Important behavior:
- If the superblock is marked clean but the clean section is missing, the clean bit is cleared and an invalid clean-section error is returned.
- Verification compares clean-section btree roots against journal roots by presence, level, key size, and key bytes.
- Marking clean sets clean flag, compat bits for allocation info/metadata, resizes the clean field, writes common entries and btree roots, validates, and updates journal position hints.

Important invariants:
- Clean field entries are encoded exactly like journal entries.
- Clean validation checks each entry stays within the superblock field.
- `bch2_fs_mark_clean()` returns early if the superblock is already clean.
- The clean section's journal sequence is the current journal sequence at clean marking.

Dependencies:
- Uses journal validation/text APIs, journal entry construction, btree root serialization, superblock field I/O, fsck error handling, and member journal position helpers.

Research notes:
- This file bridges journal recovery and superblock fast-mount state.
- Clean-section corruption is handled conservatively because it affects whether journal replay can be skipped.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/clean.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/clean.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/clean.h

This header declares clean-superblock section APIs.

Key responsibilities:
- Declares validation, verification, read, and common-entry append helpers:
  - `bch2_sb_clean_validate_late()`
  - `bch2_verify_superblock_clean()`
  - `bch2_read_superblock_clean()`
  - `bch2_journal_super_entries_add_common()`
- Exposes `bch_sb_field_ops_clean`.
- Declares dirty/clean state mutators:
  - `bch2_fs_mark_dirty()`
  - `bch2_fs_mark_clean()`

Important invariants:
- The clean section is represented as journal entries and must be validated by journal entry validators.
- Mark clean/dirty operate on superblock state.

Research notes:
- The header is the interface used by journal write, recovery, and superblock I/O paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/clean.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters.c

This file implements persistent and runtime filesystem counters.

Key responsibilities:
- Builds counter name, flag, and stable-ID maps from `BCH_PERSISTENT_COUNTERS()`.
- Provides superblock field ops for counters.
- Loads persistent counters from the superblock into per-CPU runtime counters.
- Stores per-CPU runtime counters back into the superblock.
- Samples recent counter history periodically for diagnostics.
- Prints persistent counters and recent activity deltas.
- Initializes and tears down filesystem counter state.
- Resets a selected counter.
- Implements `bch2_ioctl_query_counters()` when chardev support is enabled.

Important behavior:
- Stable counter IDs determine on-disk slots, not enum order.
- Missing counters default to zero when reading older superblocks.
- `bch2_sb_counters_from_cpu()` resizes the counters field if it has fewer than `BCH_COUNTER_NR` entries.
- Recent samples shift a fixed history window every `HZ / 2`.
- The ioctl can return either current runtime counters or mount-time counters depending on flags.

Important invariants:
- Runtime `now[]` counters are per-CPU u64 values.
- `mount[]` stores the counter values at mount/read time.
- Counter superblock validation is currently permissive.
- Counter query rejects unknown flags and nonzero padding.

Dependencies:
- Uses superblock field resize/get, percpu u64 helpers, delayed work, user copy helpers, and counter format definitions.

Research notes:
- Counter IDs are explicitly stable to preserve user-visible and on-disk compatibility across enum reordering.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters.h

This header declares counter APIs and defines event/trace helper macros.

Key responsibilities:
- Declares superblock counter load/store and filesystem counter lifecycle functions.
- Declares counter reset, recent-counter text output, and ioctl query.
- Exposes counter names, flags, stable map, and field ops.
- Defines `event_inc()` and `event_add()` for typed counter updates.
- Defines trace-coupled counter macros:
  - `event_trace()`
  - `event_add_trace()`
  - `event_inc_trace()`
  - `_fn` variants for out-of-line cold trace formatting.

Important invariants:
- `counter_typecheck()` uses `BUILD_BUG_ON()` to ensure sector counters use `event_add()` and event counters use `event_inc()`.
- Trace macros only build printbuf text when the tracepoint is enabled.
- `_fn` variants keep hot paths smaller by moving formatting into a function call.

Dependencies:
- Uses tracepoint naming conventions, printbuf, superblock I/O, and counter format/types.

Research notes:
- These macros are used throughout journal, btree, allocator, and data paths to keep accounting type-safe at compile time.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters_format.h

This header defines persistent counter IDs, types, descriptions, and on-disk counter layout.

Key definitions:
- `enum bch_counters_flags`
  - `TYPE_COUNTER`: event counters.
  - `TYPE_SECTORS`: sector amount counters.
- `BCH_PERSISTENT_COUNTERS()`: macro table of all persistent counters with stable numeric IDs, type flags, and descriptions.
- `enum bch_persistent_counters`: generated runtime enum order.
- `bch2_counter_flags[]`: generated counter type map.
- `enum bch_persistent_counters_stable`: generated stable on-disk IDs.
- `struct bch_sb_field_counters`: superblock field header plus flexible array of little-endian u64 counter values.
- `check_bch_counter_ids_unique()`: compile-time switch trick for duplicate stable ID detection.

Counter families:
- Sync/fsync and data read/write/update counters.
- Promotion and no-promotion reason counters.
- Reconcile scan/work counters.
- Stripe allocation/update/repair counters.
- Copygc and discard counters.
- Bucket allocation and sector allocation counters.
- Btree cache/node/path counters.
- Journal reservation/full/reclaim/write counters.
- GC generation counters.
- Transaction restart and commit counters.
- Write buffer and accounting slowpath counters.
- Generic thrown error counter.

Important invariants:
- Stable IDs are sparse and must remain unique.
- `TYPE_SECTORS` counters are measured in sectors.
- The superblock field stores values by stable ID slot, not runtime enum index.

Research notes:
- This header is both user-facing telemetry taxonomy and persistent format.
- Adding counters requires choosing a stable unused ID and correct type flag.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters_types.h

This header defines runtime counter storage.

Key definitions:
- `struct bch_fs_counters`
  - `mount[]`: counter values captured at mount/load time.
  - `now`: per-CPU current counters.
  - `recent[NR_RECENT_COUNTERS][BCH_COUNTER_NR]`: fixed history window for recent deltas.
  - `work`: delayed work used to refresh recent samples.
- `NR_RECENT_COUNTERS` is 20.

Important invariants:
- `now` must be allocated/freed by counter lifecycle code.
- Recent samples store absolute snapshots; text output computes deltas between snapshots.

Research notes:
- This is intentionally small and tied to counter enum size from `counters_format.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/counters_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.c

This file manages metadata-version upgrade/downgrade recovery requirements stored in the superblock.

Key responsibilities:
- Defines upgrade and downgrade tables mapping metadata versions to required recovery passes and fsck errors to silence.
- Applies upgrade requirements with `bch2_sb_set_upgrade()` and `bch2_sb_set_upgrade_incompat()`.
- Adds special upgrade requirements with `bch2_sb_set_upgrade_extra()`.
- Builds and updates the `BCH_SB_FIELD_downgrade` superblock field with `bch2_sb_downgrade_update()`.
- Applies downgrade requirements when moving from an older minor version range to a newer current version with `bch2_sb_set_downgrade()`.
- Validates and prints downgrade superblock entries.

Important behavior:
- `RECOVERY_PASS_ALL_FSCK` expands to the fsck recovery pass mask.
- Upgrade entries set bits in `ext->recovery_passes_required` and `ext->errors_silent`.
- Extra upgrade handling for `bucket_stripe_sectors` requires allocation checks if stripes exist.
- Downgrade field generation skips entries from other major versions or entries older than the incompatible version floor.
- Downgrade entries are variable length with packed 2-byte alignment.
- Applying downgrade entries ORs recovery pass bits and marks listed errors silent in both in-memory and superblock ext state.

Important invariants:
- Downgrade validation requires entry major version to match the superblock major version.
- On write validation, entries may not overrun the superblock field.
- Empty 2-byte-aligned tail entries at the end are tolerated.
- Downgrade field resize does not shrink an existing larger field.

Dependencies:
- Uses metadata version constants, recovery pass stable conversion, fsck error IDs, superblock ext fields, btree stripe-root state, darrays, and errors text formatting.

Research notes:
- This file is compatibility policy. It encodes which repair/scanning passes are needed when metadata semantics change across versions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.h

This header declares downgrade/upgrade superblock compatibility APIs.

Key responsibilities:
- Exposes `bch_sb_field_ops_downgrade`.
- Declares:
  - `bch2_sb_downgrade_update()`
  - `bch2_sb_set_upgrade()`
  - `bch2_sb_set_upgrade_incompat()`
  - `bch2_sb_set_upgrade_extra()`
  - `bch2_sb_set_downgrade()`

Research notes:
- This is the public interface used by superblock upgrade and recovery initialization paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade_format.h

This header defines the on-disk downgrade superblock field format.

Key definitions:
- `struct bch_sb_field_downgrade_entry`
  - `version`: metadata version threshold.
  - `recovery_passes[2]`: stable recovery pass bitmaps.
  - `nr_errors`: count of trailing fsck error IDs.
  - `errors[]`: little-endian fsck error IDs.
  - Packed and aligned to 2 bytes.
- `struct bch_sb_field_downgrade`
  - Standard superblock field header.
  - Flexible array of downgrade entries.

Important invariants:
- Entries are variable length and only 2-byte aligned.
- Recovery pass bitmaps are stored as little-endian u64 arrays.
- `errors[]` is counted by `nr_errors`.

Research notes:
- Consumers must parse carefully because section size is 8-byte aligned while entries are 2-byte aligned.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/downgrade_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors.c

This file implements persistent fsck/superblock error counting and formatting.

Key responsibilities:
- Builds `bch2_sb_error_strs[]` from `BCH_SB_ERRS()`.
- Prints error IDs with `bch2_sb_error_id_to_text()`.
- Validates `BCH_SB_FIELD_errors` entries.
- Prints superblock errors sorted by most recent error time.
- Prints in-memory filesystem error counts.
- Increments in-memory error counters with timestamp updates.
- Serializes in-memory error counts back to the superblock.
- Loads superblock error counts into in-memory darray state.

Important behavior:
- Validation rejects zero-count entries and entries not sorted by increasing error ID.
- Text output sorts a temporary darray by descending `last_error_time`.
- Counting preserves sorted in-memory order by error ID and increments existing entries.
- If darray allocation fails during counting, the new error count is dropped.
- Serialization resizes the errors field to match current in-memory count.

Important invariants:
- Error entry ID is 16 bits and count is 48 bits in a packed le64.
- In-memory and on-disk error entries are sorted by ID for update/search.
- Error timestamps are seconds from `ktime_get_real_seconds()`.

Dependencies:
- Uses superblock field helpers, darrays, printbuf datetime formatting, mutex-protected error count state, and error format definitions.

Research notes:
- This file supplies the persistent accounting used by journal validation, fsck, and downgrade/upgrade silent-error policy.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors.h

This header declares superblock/fsck error accounting APIs.

Key responsibilities:
- Includes runtime error types.
- Exposes `bch2_sb_error_strs[]`.
- Declares:
  - `bch2_sb_error_id_to_text()`
  - `bch2_fs_errors_to_text()`
  - `bch2_sb_error_count()`
  - `bch2_sb_errors_from_cpu()`
  - `bch2_sb_errors_to_cpu()`
- Exposes `bch_sb_field_ops_errors`.

Research notes:
- This is the small public interface between validators/fsck paths and persistent error count storage.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors_format.h

This header defines fsck error flags, the full fsck/superblock error ID catalog, and the on-disk error-count field.

Key definitions:
- `enum bch_fsck_flags`
  - `FSCK_CAN_FIX`
  - `FSCK_CAN_IGNORE`
  - `FSCK_AUTOFIX`
  - `FSCK_ERR_NO_LOG`
  - `FSCK_ERR_SILENT`
- `BCH_SB_ERRS()`: macro table mapping symbolic error names to stable numeric IDs and flags.
- `enum bch_sb_error_id`: generated stable fsck error IDs.
- `bch_sb_field_error_entry`: packed value plus last error timestamp.
- `struct bch_sb_field_errors`: superblock field header plus trailing error entries.
- Bitfields:
  - `BCH_SB_ERROR_ENTRY_ID`
  - `BCH_SB_ERROR_ENTRY_NR`

Error families:
- Clean/dirty journal state and jset validation errors.
- Journal entry and btree node/bset structural errors.
- Filesystem and device usage accounting mismatches.
- Allocation, bucket generation, discard, freespace, and backpointer errors.
- Extent pointer, CRC, stripe, reflink, snapshot, subvolume, inode, dirent, xattr, quota, and root errors.
- Accounting key and reconcile work errors.
- VFS integration and compression/device/journal bucket errors.

Important invariants:
- Numeric IDs are stable and sparse.
- `MAX` defines the current upper bound.
- Error entry ID is 16 bits; error count is 48 bits.
- Flags express fsck policy hints but the table itself is also persistent ABI.

Research notes:
- This is one of the core compatibility headers for fsck diagnostics. Renumbering entries would break persisted error counts and downgrade/upgrade policy tables.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors_types.h

This header defines in-memory superblock/fsck error count storage.

Key definitions:
- `struct bch_sb_error_entry_cpu`
  - 16-bit `id`
  - 48-bit `nr`
  - `last_error_time`
- `bch_sb_errors_cpu`: darray of CPU-side error entries.

Important invariants:
- The bit widths mirror the on-disk packed ID/count split.
- Callers keep entries sorted by error ID.

Research notes:
- This file separates runtime container type definitions from the on-disk format catalog.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/errors_types.h -->