# Group Research: group_213_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_init_passes_c_source_5ad466f0651f

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.c

## Role

Implements bcachefs recovery-pass scheduling, persistence, dependency handling, ratelimiting, rewind, async online-pass execution, and status reporting.

## Major Responsibilities

- Builds `bch2_recovery_passes[]` and the `recovery_passes[]` dispatch table from `BCH_RECOVERY_PASSES()`.
- Converts between execution-order pass IDs and stable superblock IDs with `bch2_recovery_passes_to_stable()` / `from_stable()`.
- Owns the superblock `recovery_passes` field text output and per-pass last-run/runtime tracking.
- Decides whether an explicit pass should be persisted, run immediately, deferred, ratelimited, or cause recovery rewind.
- Runs passes sequentially via `bch2_run_recovery_passes()` and startup selection via `bch2_run_recovery_passes_startup()`.
- Defers eligible `PASS_ONLINE` passes into background work after mount recovery.
- Provides human-readable recovery-pass status.

## Key Control Flow

`bch2_run_recovery_passes_startup()` composes the pass set from always-run passes, unclean-shutdown passes, fsck passes, mount-option requested passes, and superblock-required passes. It applies `recovery_pass_last`, excludes requested passes except `set_may_go_rw`, skips passes before `from`, and defers online-safe passes unless fsck is active.

`bch2_run_recovery_passes()` loops through the lowest set pass bit, runs it, flushes the journal, records completion, and handles rewinds by restoring the original pass set from `rewound_to`.

`__bch2_run_explicit_recovery_pass()` is the central repair hook. It can set persistent superblock bits, set ephemeral bits, mark ratelimited passes, trigger async online passes, or return `restart_recovery` if the requested pass is earlier than the current recovery position.

## Notable Details

- Stable IDs are deliberately separate from enum order; the second field in `BCH_RECOVERY_PASSES()` is the persistent ABI.
- `scan_for_btree_nodes` is never scheduled persistently; `check_topology` invokes it when required.
- `recovery_pass_should_defer()` only defers a pass if it and all scheduled dependents can run online.
- `bch2_recovery_pass_set_no_ratelimit()` appears name-sensitive: the implementation currently calls `SET_BCH_RECOVERY_PASS_NO_RATELIMIT(e, false)` even when entering the branch for a missing no-ratelimit flag.
- After crossing `check_snapshots`, the runner wakes copygc and reconcile work.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.h

## Role

Public interface for recovery-pass scheduling and status helpers.

## Contents

- Declares `bch2_recovery_passes[]` and superblock field ops for persisted recovery-pass records.
- Exposes stable-ID conversion helpers and the fsck pass mask helper.
- Defines `RUN_RECOVERY_PASS_nopersistent` and `RUN_RECOVERY_PASS_ratelimit`.
- Provides `go_rw_in_recovery()`, which determines whether recovery needs early read-write mode.
- Provides `recovery_pass_will_run()` and `bch2_recovery_cancelled()` inline helpers.
- Declares explicit-pass scheduling, pass requirement, async pass execution, startup pass execution, status formatting, and initialization.

## Notable Details

`go_rw_in_recovery()` gates early RW on upgrade/downgrade permission and conditions such as journal keys, read-only state, unclean superblock, requested recovery passes, or fsck without alloc info.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_format.h

## Role

Defines the recovery-pass catalog, persistent pass identifiers, pass flags, dependency masks, and the on-disk superblock recovery-pass record format.

## Major Responsibilities

- Defines pass flags: silent, fsck, unclean, always, online, alloc, nodefer, and debug fsck behavior.
- Defines `BCH_RECOVERY_PASSES()` as the single source for pass enum order, stable IDs, flags, dependencies, and descriptions.
- Generates `enum bch_recovery_pass` in run order.
- Generates `enum bch_recovery_pass_stable` for superblock persistence.
- Defines `struct recovery_pass_entry` with `last_run`, `last_runtime`, and flags.
- Defines `struct bch_sb_field_recovery_passes`.
- Provides `recovery_passes_nr_entries()`.

## Pass Categories

The list spans topology scan/repair, accounting/alloc initialization, journal setup/replay, allocator consistency checks, snapshot/subvolume checks, inode/extent/directory/xattr checks, logged-op resume, dead inode/snapshot cleanup, migration passes, reconcile-work checks, btree bitmap GC, and final root inode lookup.

## Notable Details

The file explicitly warns that passes may be reordered but stable IDs must never change. This is the compatibility anchor for persisted recovery requirements and pass history.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_types.h

## Role

Defines runtime recovery-pass state embedded in `struct bch_fs`.

## Contents

`struct bch_fs_recovery` tracks:

- Ephemeral scheduled passes.
- Current pass set and current pass.
- Rewind source/target and `pass_done`.
- Completed, failing, and ratelimited pass masks.
- A spinlock for state updates.
- A `run_lock` mutex to serialize pass execution.
- A work item for async online recovery passes.

## Notable Details

The separation between persistent superblock bits and `scheduled_passes_ephemeral` lets the filesystem request immediate recovery ordering without committing every transient prerequisite to disk.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.c

## Role

Implements coarse progress indicators for long btree scans during recovery/fsck.

## Major Responsibilities

- Initializes progress state with a message, target btree masks, and estimated node totals.
- Estimates total nodes from accounting counters, falling back to disk-sector estimates when older accounting data lacks node counts.
- Updates progress from a `btree_iter`, including cancellation checks.
- Periodically logs progress every 10 seconds unless silent.
- Formats progress as percent, nodes seen/total, and current btree position.

## Notable Details

The implementation explicitly treats totals as estimates because node replica counts can vary. It prefers underestimating missing accounting data as zero or using disk-sector estimates instead of blindly trusting incomplete counters.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.h

## Role

Declares the recovery/fsck progress indicator structure and helpers.

## Contents

- `struct progress_indicator` stores message, current `bbpos`, next print time, seen/total node counts, last node, and silent mode.
- Declares initialization, iterator update, and text formatting functions.

## Notable Details

The header comments call these indicators a fallback for contexts where userspace progress reporting is not wired up, especially older code and mount-time recovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.c

## Role

Implements the main bcachefs recovery and new-filesystem initialization pipeline.

## Major Responsibilities

- Marks btrees as having lost data and schedules the required repair passes.
- Supports allocator reconstruction and journal-rewind error silencing.
- Transitions recovery into early read-write mode.
- Replays journal keys into btrees, with accounting keys replayed first.
- Performs early replay of root, usage, blacklist, and clock journal entries.
- Reads btree roots, reconstructing fake roots where needed.
- Drives mount recovery from clean superblock or journal scan through startup recovery passes.
- Handles journal rewind, recent-journal scrub, blacklisting of unsafe post-replay sequences, fsck verification, quota loading, superblock cleanup, and background cleanup triggers.
- Initializes a new filesystem, including fake roots, journal allocation/start, root inode, `lost+found`, first journal flush, and initialized superblock state.

## Key Recovery Flow

`__bch2_fs_recovery()` reads the clean section for clean shutdowns or scans journal entries for unclean/recovery-info/rewind/scrub modes. It establishes journal start positions, runs early replay, resizes on mount, applies read-only restrictions for special image layouts, reconstructs alloc info if required, handles rewind setup, blacklists skipped sequence ranges, starts the journal, sorts journal keys, reads roots, starts the btree runtime, applies option hooks/upgrades, optionally scrubs recent journal entries, then runs startup recovery passes.

After pass execution it ensures `BCH_FS_may_go_rw`, clears fsck state, flushes rewrites, persists fixed-error metadata, optionally performs a second debug fsck, reads quotas, updates upgrade/compat bits, garbage-collects blacklist entries, starts dead-snapshot deletion, and runs replicas cleanup.

## Journal Replay

`bch2_journal_replay()` requires the journal key buffer to be stable, replays accounting deltas first, then tries sorted replay for locality. Keys that cannot be replayed in the fast path are sorted by journal sequence and replayed in journal order while dropping replay pins. Repair-generated allocated keys force immediate flush.

## Notable Details

- After unclean shutdown, recovery advances `cur_seq` by 64 before blacklisting skipped sequences.
- If encryption is enabled and shutdown was unclean, key version is advanced by `1 << 16` to avoid nonce reuse.
- Missing btree roots can be tolerated for reconstructible btrees and fake roots are allocated for missing standard roots.
- `bch2_fs_recovery()` wraps the internal recovery path and forces emergency read-only on recovery failure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.h

## Role

Public declarations for the recovery pipeline.

## Contents

Declares helpers for lost btree data, journal rewind error silencing, early RW transition, journal replay, full filesystem recovery, and new filesystem initialization.

## Notable Details

This header exposes only the top-level recovery operations; pass scheduling details are in `passes.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.c

## Role

Handles journal bucket allocation, deletion, device journal initialization, filesystem journal startup/shutdown, and journal object allocation.

## Major Responsibilities

- Allocates additional journal buckets on a device and persists them to the superblock.
- Deletes a journal bucket and adjusts ring indices.
- Allocates default journal space per device.
- Stops per-device and filesystem-wide journal activity safely.
- Starts journal runtime state from `journal_start_info`.
- Initializes replay pins and device replica references for journal entries.
- Sets replay-done/running flags after recovery.
- Initializes/exits device journal arrays, biosets, work items, workqueues, FIFOs, and buffers.

## Startup Details

`bch2_fs_journal_start()` clamps `cur_seq` above blacklisted sequences, rejects sequence overflow, sizes the pin FIFO based on the recovery window plus slack, initializes replay pins as `unreplayed`, establishes `seq`, `seq_ondisk`, `last_seq`, rewind bounds, and aligns `in_flight.front/back` with sequence numbering.

For each replayed journal entry, it records the replica device set on the corresponding pin and validates that journal replicas were represented in filesystem replica metadata unless degraded.

## Notable Details

- Default journal size is about 1/128 of device buckets, clamped to at least `BCH_JOURNAL_BUCKETS_MIN` and at most 8192 buckets or 8 GiB worth of sectors.
- `in_flight` starts with 256 slots and is sequence-aligned manually instead of using `init_fifo()`.
- Shutdown waits for reclaim, flushes all pins, writes metadata, quiesces bookkeeping, and verifies the last empty sequence when possible.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.h

## Role

Declares journal allocation, startup/shutdown, replay completion, and init/exit helpers.

## Contents

Functions cover device bucket count changes, bucket deletion, device/fs journal allocation, per-device stop, fs stop/start, replay-done transition, and early/full init/exit for device and filesystem journal objects.

## Notable Details

`bch2_fs_journal_start()` consumes `struct journal_start_info`, which is produced by journal read/recovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.c

## Role

Core journal reservation, entry open/close, write triggering, flush, rewind-range, blocking, and diagnostics implementation.

## Major Responsibilities

- Opens and closes journal entries around atomic reservation state.
- Starts writes when a closed buffer has no outstanding reservation references.
- Tracks unwritten buffers in `in_flight`.
- Detects stuck journal conditions and forces emergency read-only.
- Provides slowpath reservation acquisition with reclaim and wait diagnostics.
- Resizes reserved per-entry space.
- Flushes specific sequences or current journal metadata.
- Adds rewind ranges to runtime state and early journal entries.
- Marks journal ranges as no-flush when supported.
- Blocks/unblocks journal reservations for write-buffer flush coordination.
- Exposes detailed debug text for journal state and devices.

## Key Mechanics

The hot reservation path uses `journal_res_get_fast()` in `journal.h`; when it fails, `bch2_journal_res_get_slowpath()` may preallocate buffers, close the current entry, open a new one, run reclaim, or wait on `async_wait`.

`journal_entry_open()` increments the global sequence, creates a pin FIFO entry, pushes an `in_flight` buffer, claims the preallocated data buffer, publishes the four-slot ring pointer, copies early entries, and atomically marks the entry open.

`__journal_entry_close()` atomically closes the entry, finalizes `u64s`, records bytes, checks reserved sector bounds, writes `last_seq`, refreshes space accounting, and drops the opening pin reference so the write can begin when references drain.

## Flush/Rewind Details

`bch2_journal_flush_seq_async()` marks a buffer as `must_flush`, opens an empty entry if needed, waits on the target buffer, and closes the current entry when appropriate. `bch2_journal_add_rewind_range()` records runtime rewind bounds and appends a persistent rewind entry to `early_journal_entries`.

## Notable Details

- The journal can be halted by closing the current entry with `JOURNAL_ENTRY_ERROR_VAL`.
- `bch2_journal_noflush_seq()` refuses no-flush if a relevant flush is already requested or persisted.
- `bch2_next_write_buffer_flush_journal_buf()` can block the journal, wait for reservation refs to drain, and hand a buffer to the btree write buffer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.h

## Role

Primary journal API and hot-path inline implementation.

## Major Responsibilities

- Documents journal purpose, on-disk layout, pinning, reclaim, flush/no-flush writes, recovery, blacklisting, options, and self-healing.
- Provides sequence helpers and buffer lookup helpers.
- Implements reservation ring-state counters and fast reservation acquisition.
- Provides journal entry add/init helpers.
- Defines reservation put behavior.
- Declares entry close/write, quiesce, flush, rewind, meta, halt, block/unblock, debug, and write-buffer coordination APIs.

## Key Data Access Patterns

- `journal_seq_to_buf()` requires `j->lock` and indexes `in_flight`.
- `journal_res_buf()` and `journal_res_data()` are lockless for held reservations via the four-slot ring.
- `journal_res_get_fast()` atomically advances `cur_entry_offset`, increments the current ring-slot count, checks watermark and entry capacity, and returns reservation metadata.

## Notable Details

Reservation state encodes current entry offset, ring index, and four buffer refcounts in one 64-bit atomic. This is the core concurrency primitive for journal writes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.c

## Role

Reads journal buckets from devices, validates and deduplicates journal entries, computes the replay window, handles blacklist/drop policy, and supports rewind rereads.

## Major Responsibilities

- Persists/resumes last journal bucket position in member info.
- Formats journal pointers and sequence datetimes.
- Verifies journal checksums and decrypts journal entries.
- Adds journal entries to the replay radix, deduplicating replicas.
- Drops overwrite/log entries unless recovery info, rewind, or scrub needs them.
- Reads buckets fully or peeks headers first for large journals.
- Detects checksum errors, duplicate mismatches, same-device duplicates, missing sequences, blacklisted entries, and non-monotonic bucket sequences.
- Re-reads older journal entries required for rewind.
- Produces `journal_start_info` with `last_seq`, `replay_end`, `cur_seq`, and clean state.

## Read Strategy

For large journals outside fsck/full-read mode, each device first peeks the first block of each bucket to collect sequence numbers, sorts buckets by descending sequence, and fully reads only buckets likely to contain live entries. Otherwise it scans every bucket.

## Replay Window Selection

`bch2_journal_read()` reverse-iterates entries. `cur_seq` is one greater than the highest on-disk entry of any kind. It skips no-flush entries and an initial torn flush write, then chooses the most recent valid flush entry as `replay_end`; that entry’s `last_seq` becomes the replay start. Entries after `replay_end` are later blacklisted by recovery.

## Notable Details

- `journal_entries_base_seq` maps 64-bit journal sequences into genradix indices and requires all replayed sequences to fit within a roughly 32-bit span.
- Rewind can lower `drop_before`, but refuses rewinds earlier than persisted `rewind_seq`.
- `bch2_journal_reread_for_rewind()` un-ignores entries previously dropped as not dirty when rewind requires them.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.h

## Role

Public interface and iteration helpers for journal reading and replay-entry traversal.

## Contents

- Declares member-info journal position helpers.
- Defines `journal_replay_ignore()`.
- Provides typed jset-entry iteration helpers and key iteration macros.
- Defines `jset_datetime()` and `journal_nonce()`.
- Declares journal pointer formatting, missing-range detection, datetime formatting, rewind reread, and journal read.

## Notable Details

`journal_nonce()` derives the journal encryption/checksum nonce from the journal sequence and `BCH_NONCE_JOURNAL`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.c

## Role

Implements journal space accounting, discard scheduling, pin management, reclaim flushing, reclaim thread lifecycle, targeted pin flushes, and reclaim diagnostics.

## Major Responsibilities

- Computes available journal space at discarded, clean-on-disk, clean, and total levels.
- Maintains journal watermarks for low space, low pin FIFO capacity, and write-buffer pressure.
- Advances dirty/discard indices and queues discard work.
- Updates `last_seq` as pin refcounts reach zero.
- Transfers journal replica references as entries become clean on disk.
- Drops replay pins as journal replay progresses.
- Sets, copies, drops, and flushes journal pins.
- Selects pins to flush by sequence and pin type.
- Runs direct/background reclaim and starts/stops the reclaim kthread.
- Flushes all pins, outstanding pins, or pins involving a specific device.
- Prints pin/reclaim debug state and timing stats.

## Space Accounting

`bch2_journal_space_available()` walks online journal devices, advances `dirty_idx` and `dirty_idx_ondisk` based on `last_seq` and `last_seq_ondisk`, computes per-replica available space, sets `JOURNAL_may_skip_flush`, updates the watermark, and sets `cur_entry_sectors` or `journal_full`.

## Pin/Reclaim Flow

Journal pins are organized per sequence into unflushed/flushed lists by type. `journal_flush_pins()` picks the oldest eligible pin, records `flush_in_progress`, calls its flush callback, moves it to the flushed list if still valid, and records timing by type.

`__bch2_journal_reclaim()` chooses `seq_to_flush` based on half-full journal buckets and pin FIFO pressure, forces at least one flush after reclaim delay or under pressure, includes key-cache dirty limits, and loops for background reclaim while useful work continues.

## Notable Details

- Reclaim will not flush unreplayed pins to avoid deadlocking journal replay.
- Discard work only issues block discards when changes are allowed and discard is enabled; it always advances discard indices after bucket cleanup.
- Shutdown pin flushing is type-ordered and intentionally avoids closing extra journal entries until pins are actually flushed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.h

## Role

Public interface and inline helpers for journal reclaim and pin tracking.

## Contents

- Defines `JOURNAL_PIN` default pin FIFO size.
- Provides `journal_reclaim_kick()`.
- Declares space accounting and watermark helpers.
- Defines `journal_pin_list_init()`, `journal_pin_active()`, and `journal_seq_pin()`.
- Declares last-seq updates, replay pin drops, pin set/copy/drop/flush helpers, discard work, reclaim start/stop, pin flushing, device-pin flushing, and diagnostics.

## Notable Details

`bch2_journal_pin_add()` only moves a pin to an older sequence, while `bch2_journal_pin_update()` only moves it to a newer sequence; both funnel through `bch2_journal_pin_set()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.c

## Role

Validates, formats, compacts, and sorts journal bucket superblock fields.

## Major Responsibilities

- Validates legacy `BCH_SB_FIELD_journal` bucket lists for nonzero, in-range, non-duplicate buckets.
- Formats legacy journal bucket lists.
- Validates `journal_v2` compact range entries for positive length, in-range coverage, non-overlap, and `UINT_MAX` total bucket count.
- Formats `journal_v2` ranges.
- Converts an explicit bucket array into compact `journal_v2` ranges with `bch2_journal_buckets_to_sb()`.
- Sorts journal buckets on clean mounts when needed and rewrites the superblock.

## Notable Details

`bch2_journal_buckets_to_sb()` deletes the legacy journal field and writes compact contiguous ranges to `journal_v2`. `bch2_sb_journal_sort()` is only allowed for clean, not-yet-RW filesystems.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.h

## Role

Header for journal superblock field helpers.

## Contents

- Inline count helper for legacy journal bucket arrays.
- Inline count helper for `journal_v2` range entries.
- Declares superblock field ops for both formats.
- Declares conversion-to-superblock and sorting helpers.

## Notable Details

Both count helpers derive element counts from variable-structure boundaries using `vstruct_end()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.c

## Role

Implements persisted journal sequence blacklisting and the runtime lookup table used during recovery and btree reads.

## Major Responsibilities

- Adds blacklisted sequence ranges to the superblock, merging overlapping/contiguous entries.
- Sets the `journal_seq_blacklist_v3` feature bit when adding entries.
- Builds an Eytzinger-sorted runtime table from the superblock field.
- Finds next blacklisted and next non-blacklisted sequence.
- Tests whether a sequence is blacklisted and marks an entry dirty if queried in dirty context.
- Returns the last blacklisted sequence.
- Validates and formats the superblock blacklist field.
- Garbage-collects blacklist entries that are neither dirty nor needed for oldest on-disk journal state.

## Notable Details

The blacklist exists so btree node updates carrying sequence numbers newer than durable journal entries are ignored after crash, and so the journal never reuses those sequence numbers before affected btree nodes are rewritten.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.h

## Role

Public interface for journal sequence blacklist operations.

## Contents

- Defines `blacklist_nr_entries()` for variable-size superblock fields.
- Declares next-blacklisted, next-nonblacklisted, membership, last-blacklisted, add, initialize, field ops, and GC helpers.

## Notable Details

Membership checks support a `dirty` parameter, letting callers mark blacklist ranges still actively needed by observed btree state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist_format.h

## Role

Defines the on-disk superblock format for journal sequence blacklist ranges.

## Contents

- `struct journal_seq_blacklist_entry` stores half-open `[start, end)` sequence ranges as little-endian u64s.
- `struct bch_sb_field_journal_seq_blacklist` embeds the generic superblock field header followed by variable entries.

## Notable Details

The implementation treats `end` as exclusive; validation rejects `start >= end`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/types.h

## Role

Defines the journal runtime and device data structures used by journal init, read, write, reclaim, and recovery.

## Major Structures

- `struct journal_buf`: one in-flight journal entry buffer with staged `jset`, target devices, write state, flush flags, sizing, and closure waiters.
- `struct journal_ringbuf`: four-slot reservation fastpath cache for current buffer/data pointers.
- `struct journal_entry_pin_list`: per-sequence pin lists and refcount.
- `struct journal_entry_pin`: pin object with flush callback and sequence.
- `struct journal_res`: held reservation metadata.
- `union journal_res_state`: 64-bit atomic reservation state packing current offset, ring index, and four refcounts.
- `struct journal`: filesystem-wide journal state, including reservations, flags, buffers, in-flight FIFO, sequence tracking, rewind ranges, pin FIFO, space accounting, write point, reclaim state, stats, and locks.
- `struct journal_device`: per-device journal bucket array, bucket sequence table, ring indices, bioset, discard work, and read state.
- `struct journal_start_info`: recovery-computed sequence window used to start the journal.

## Important Constants

- `JOURNAL_SEQ_MAX` limits usable sequence numbers to 56 bits because the btree write buffer uses high bits.
- `JOURNAL_STATE_BUF_NR` is four reservation ring slots.
- Journal entries range from 64 KiB to 4 MiB.
- Special `cur_entry_offset` sentinel values represent blocked, closed, and error states.

## Notable Details

`journal_start_info` documents the three recovery zones: replay `[last_seq, replay_end]`, blacklist `[replay_end + 1, cur_seq)`, and new writes from `cur_seq`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/types.h -->