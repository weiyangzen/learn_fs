# Group Research: group_323_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer_hammer_curso_9d06585edc1d

Research scope: `Docs/research_subset_a.md`, covering `sources/os/bsd/dragonflybsd` as part of OS/VFS and local filesystem kernel sources.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.c

## Role

Implements HAMMER B-tree cursor lifecycle, navigation, lock upgrading/downgrading, deadlock recovery, and live cursor adjustment during B-tree mutation. A `hammer_cursor` is not just an iterator; it is a tracked mutable handle that other B-tree maintenance operations may adjust while the cursor is unlocked.

## Major Entry Points

- `hammer_init_cursor()` initializes a cursor from an optional node cache or the filesystem root B-tree node, with throttling for frontend readers when the backend flusher is under reclaim pressure.
- `hammer_done_cursor()` releases parent/node/data/inode/memory-record references and waits out deadlock recovery references.
- `hammer_normalize_cursor()` repairs cursors left with `node == NULL` by moving up to the parent.
- `hammer_cursor_upgrade()`, `hammer_cursor_upgrade_node()`, `hammer_cursor_downgrade()` handle shared-to-exclusive lock transitions.
- `hammer_cursor_upgrade2()` and `hammer_cursor_downgrade2()` upgrade/downgrade two cursors while accounting for shared nodes, used by deduplication.
- `hammer_cursor_seek()`, `hammer_cursor_up()`, `hammer_cursor_up_locked()`, and `hammer_cursor_down()` reposition cursors in the B-tree.
- `hammer_unlock_cursor()`, `hammer_lock_cursor()`, and `hammer_recover_cursor()` implement tracked unlock/relock deadlock recovery.
- Mutation callbacks such as `hammer_cursor_replaced_node()`, `hammer_cursor_removed_node()`, `hammer_cursor_split_node()`, `hammer_cursor_moved_element()`, `hammer_cursor_parent_changed()`, `hammer_cursor_deleted_element()`, and `hammer_cursor_inserted_element()` keep unlocked tracked cursors coherent across B-tree restructuring.
- `hammer_push_cursor()` and `hammer_pop_cursor()` duplicate/restore a cursor for nested operations.
- `hammer_cursor_invalidate_cache()` drops cached data buffers before underlying storage is freed or repointed.

## Implementation Notes

- Cursor initialization may delay non-flusher transactions via time-domain multiplexing when reclaimed inode pressure is high and the flusher is running.
- Cursor parent information is loaded through `hammer_load_cursor_parent()`, which also establishes left/right B-tree bounds from parent elements or root sentinels.
- Lock upgrades record failed nodes in `deadlk_node`; cleanup later waits on that node so retry loops do not race immediately back into the same deadlock.
- Tracked cursors are inserted into `node->cursor_list` while unlocked. B-tree structural operations walk those lists and adjust cursor node references, indices, and leaf pointers.
- A removed element sets `HAMMER_CURSOR_TRACKED_RIPOUT`; relocking clears `ATEDISK` and sets `RETEST` so iteration does not skip the successor.
- Node removal during recovery can set `HAMMER_CURSOR_ITERATE_CHECK`, explicitly telling iteration code the cursor may now sit outside the original search range.
- `hammer_cursor_moved_element()` has special handling for cursors pointing at parent separators when a first child element moves, preventing mirror/write iteration from losing its place.
- Data buffer invalidation is important because cached cursor buffers can prevent buffer-cache invalidation when deduplication or block freeing changes the underlying block.

## Dependencies

Uses HAMMER node refs/locks, B-tree parent lookup, root volume lookup, node cache refs, transaction state, inode locks, memory-record refs, flusher pressure state, and TAILQ cursor tracking on nodes.

## Research Notes

This file is central to HAMMER’s concurrent B-tree correctness. Its core invariant is that active cursors either hold node locks or are explicitly tracked so structural mutations can rewrite their location before they are relocked.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.h

## Role

Defines the `hammer_cursor` structure and cursor flags used by HAMMER B-tree lookup, iteration, insertion, pruning, reblocking, mirroring, and in-memory/on-disk record merge scans.

## Main Data Structures

- `struct hammer_cursor` stores the active transaction, parent/current B-tree nodes, node indices, deadlock recovery references, key range, B-tree bounds, data/leaf pointers, flags, inode context, and current in-memory record.
- `struct hammer_cmirror` extends cursor scans with a `mirror_tid` filter and skipped internal-node bounds for mirror optimization.

## Important Fields

- `parent`, `parent_index`, `node`, and `index` identify the current B-tree position.
- `left_bound` and `right_bound` represent inherited node bounds; the right bound is range-exclusive.
- `key_beg`, `key_end`, and `asof` define lookup or iteration constraints.
- `data_buffer`, `leaf`, and `data` expose extracted on-disk or in-memory record payloads.
- `ip` and `iprec` connect cursors to inode-local merged scans.
- `deadlk_node` and `deadlk_rec` allow cleanup or recovery paths to wait for deadlocked nodes/records after releasing normal cursor state.

## Flag Groups

- Extraction/control flags include `HAMMER_CURSOR_GET_DATA`, `HAMMER_CURSOR_BACKEND`, `HAMMER_CURSOR_INSERT`, and delete visibility controls.
- Iteration state flags include `ATEDISK`, `ATEMEM`, `DISKEOF`, `MEMEOF`, `RETEST`, and `LASTWASMEM`.
- Snapshot and mirroring flags include `ASOF`, `CREATE_CHECK`, and `MIRROR_FILTERED`.
- Maintenance flags include `PRUNING`, `REBLOCKING`, `TRACKED`, `TRACKED_RIPOUT`, `ITERATE_CHECK`, and `NOSWAPCACHE`.

## Helper Macros

- `hammer_cursor_inmem(cursor)` tests whether the current leaf comes from the cursor’s in-memory record.
- `hammer_cursor_ondisk(cursor)` is the inverse condition, identifying on-disk B-tree state.

## Research Notes

The header documents an important design rule: cursors are tracking structures, and unrelated B-tree operations may modify them while they are not holding exclusive node locks. This is the contract implemented by `hammer_cursor.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_dedup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_dedup.c

## Role

Implements the HAMMER deduplication ioctl path for replacing one duplicate data block reference with another while updating blockmap reference accounting.

## Main Entry Point

- `hammer_ioc_dedup()` receives two B-tree leaf descriptors from userspace, validates both records, compares their data, adjusts blockmap accounting, frees the second block reference, and repoints the second leaf to the first data offset.

## Control Flow

- Requires filesystem version `HAMMER_VOL_VERSION_FIVE` or newer because version 5 allows dedup accounting through signed `bytes_free`.
- Initializes `cursor1`, looks up the first element, and extracts data.
- Initializes `cursor2`, looks up the second element, and extracts data.
- Validates both leaves point to data zones, not metadata zones.
- Requires both data offsets to be in the same HAMMER zone and both data lengths to match.
- Performs a byte-by-byte `bcmp()` before modifying metadata.
- Acquires the shared sync lock and upgrades both cursors together with `hammer_cursor_upgrade2()`, which handles shared nodes correctly.
- Calls `hammer_blockmap_dedup()` on the first block to increment/rebalance dedup accounting.
- Invalidates cursor2’s cached data buffer before freeing its old data block, then calls `hammer_blockmap_free()`.
- Modifies cursor2’s B-tree leaf `data_offset` to point at cursor1’s data block.
- Downgrades both cursors, releases the sync lock, and cleans up cursors.

## Error and Status Semantics

- Unsupported filesystem version returns `EOPNOTSUPP`.
- Lookup/extract/upgrade failures return errors so userspace can retry candidates later.
- Invalid zones set `HAMMER_IOC_DEDUP_INVALID_ZONE` and return success.
- Data mismatch, zone mismatch, or length mismatch set `HAMMER_IOC_DEDUP_CMP_FAILURE` and return success.
- Blockmap underflow sets `HAMMER_IOC_DEDUP_UNDERFLOW` and returns success.
- Other blockmap errors propagate.

## Pressure Handling

After cursor cleanup, the function waits/kicks the flusher while metadata pressure or undo exhaustion is above background thresholds. This avoids deadlocking the buffer cache during bulk dedup runs.

## Research Notes

This is a compact ioctl implementation, but it relies heavily on cursor correctness, blockmap accounting, and buffer invalidation. The ordering around `hammer_cursor_invalidate_cache()` before freeing cursor2’s old block is a key safety detail.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_dedup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_disk.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_disk.h

## Role

Defines the HAMMER1 on-disk format: fixed sizes, offset encoding, zones, blockmaps, UNDO/REDO FIFO records, volume headers, record/object types, inode payloads, directory entries, PFS metadata, snapshots, and config records.

## Format Foundations

- HAMMER uses 16 KiB filesystem buffers through `HAMMER_BUFSIZE`.
- File data at or beyond the 1 MiB demarc uses 64 KiB xbufs.
- Per-volume storage uses 52 offset bits; per-filesystem logical capacity is 60 bits, with top offset bits used for zones.
- `hammer_tid_t` is a 64-bit transaction id, usually synchronized to time.
- `hammer_off_t` is a 64-bit encoded address containing zone, optional volume number, and offset.

## Zone Encoding

The header defines zones for raw volume, raw buffer, undo, freemap, B-tree, metadata, large data, small data, and unavailable space. Helper macros test zone type, encode/decode zone and volume bits, and translate addresses into zone-2/raw-buffer addressing.

Important zone behavior:

- Zones 8 through 15 are record/data/meta classifications but usually carry a zone-2 physical address.
- The freemap is the only full two-layer blockmap user.
- Data-zone helpers distinguish large and small data by data length.

## Big-Block and Blockmap Layout

- HAMMER big-blocks are 8 MiB.
- The blockmap is a two-layer map: layer1 has 18 bits of fanout, layer2 has 19 bits, and big-block offset contributes 23 bits, totaling 60 bits.
- `struct hammer_blockmap` stores physical offset, first/next/alloc offsets, and CRC.
- `struct hammer_blockmap_layer1` tracks free big-block count and layer2 location.
- `struct hammer_blockmap_layer2` tracks zone, append offset, signed `bytes_free`, and CRC.
- Version 5 changed `bytes_free` to signed to allow deduplication to drive accounting below zero.

## UNDO/REDO FIFO

- FIFO entries use `hammer_fifo_head` and `hammer_fifo_tail` with signatures, type, aligned size, sequence number, and CRC.
- Version 4 reduced undo alignment to 512 bytes so each sector has a header and recovery can identify missing sectors.
- `hammer_fifo_undo` records raw metadata updates.
- `hammer_fifo_redo` records logical file writes/truncates for fast fsync semantics.
- REDO flags include write, truncation, write/trunc termination, and sync markers.
- Recovery semantics distinguish backward UNDO processing from forward REDO replay and REDO termination filtering.

## Volume Header

`struct hammer_volume_ondisk` contains:

- HAMMER signature, physical volume layout offsets, filesystem UUIDs, label, volume number/count, version, CRC, flags, and root volume id.
- Root-volume-only statistics such as big-block counts, inode count, B-tree root offset, and next transaction id.
- Cached blockmaps for all zones.
- The direct undo FIFO big-block array.

Version constants define minimum, default, work-in-progress, and maximum supported formats. Version notes include directory entry layout, snapshot layout, undo/flush changes, dedup, directory hash algorithm changes, and faster CRC support.

## Record and Object Types

Record types include inode, data, directory entry, DB, extended attributes, fixed attributes, PFS management, snapshot management, and cleanup config. Object types map HAMMER objects to directory, regular file, DB file, FIFO, device, symlink, PFS root, and socket semantics.

## Inode and Namespace Data

- `struct hammer_inode_data` stores version, mode, flags, device ids, ctime, parent object id, uid/gid UUIDs, object type, capability flags, link count, size, inline symlink space, mtime, and atime.
- `HAMMER_INODE_CRCSIZE` excludes mtime and atime from the inode data CRC, enabling special timestamp update paths.
- Directory entries store target object id, localization, and non-null-terminated name bytes.
- Symlink overflow data uses fixed records.
- Directory localization can use inode-localized entries depending on inode capability flags.

## PFS, Snapshot, and Config Records

- `struct hammer_pseudofs_data` stores mirror sync TIDs/timestamps, shared and unique UUIDs, flags, label, snapshot path, and prune policy.
- PFS flags distinguish slave and deleted states.
- HAMMER supports up to 65,536 pseudo-filesystems.
- Snapshot records store a TID key, timestamp, label, and reserved fields.
- Config records store cleanup configuration text and are not mirrored.

## Research Notes

This header is the durable HAMMER1 ABI. Most higher-level code in this group depends on these constants for locking, flushing, dedup accounting, recovery, and object interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_flusher.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_flusher.c

## Role

Implements HAMMER’s dependency flusher: a master thread sequences flush groups, slave threads flush dirty inodes, and finalization synchronizes data, UNDO/REDO, volume headers, metadata, and delayed frees.

## Thread Model

- `hammer_flusher_create()` starts one master thread and `HAMMER_MAX_FLUSHERS` slave threads.
- `hammer_flusher_destroy()` shuts down the master, then drains and stops idle slaves.
- `hammer_flusher_master_thread()` owns sequence advancement, loose I/O cleanup, group flushing, completion wakeups, and idle waiting.
- `hammer_flusher_slave_thread()` scans the current flush group’s RB tree and calls `hammer_flusher_flush_inode()` for available inodes.

## Flush Group APIs

- `hammer_flusher_sync()` closes pending groups and waits for completion.
- `hammer_flusher_async()` closes groups up to a target group, signals the master, and returns the relevant sequence number.
- `hammer_flusher_async_one()` flushes the current/next flushable group or creates a dummy sequence for FIFO/metadata-only work.
- `hammer_flusher_wait()` sleeps until a sequence number is complete.
- `hammer_flusher_running()` reports whether pending sequence numbers remain.
- `hammer_flusher_wait_next()` combines async-one and wait.

## Core Flush Flow

`hammer_flusher_flush()` processes one sequence number:

- Finds the next flush group matching `done + 1`.
- Starts a flusher transaction.
- If undo space is already too low, finalizes a dummy cycle first to move undo FIFO state forward.
- Assigns the flush group and transaction copy to all ready slaves.
- Waits until every slave returns to the ready list.
- Calls `hammer_flusher_finalize()` for final synchronization.
- Removes the flush group when its tree is empty.
- Runs metadata/FIFO-only finalization when there is work but no inode group.
- Clears delayed reservations whose safe sequence has arrived.

## Inode Flush Worker

`hammer_flusher_flush_inode()`:

- Uses `HAMMER_INODE_SLAVEFLUSH` to prevent multiple slaves from flushing the same inode concurrently.
- Cleans loose I/O and waits for VM pressure to become nominal.
- Calls `hammer_sync_inode()`.
- Treats `EWOULDBLOCK` as a normal retry condition and converts other errors into serious inode sync errors through completion handling.
- Calls `hammer_sync_inode_done()`.
- Finalizes when undo space is below emergency level or metadata dirty space exceeds the configured limit.

## Finalization

`hammer_flusher_finalize()` performs the durability sequence:

- Serializes finalization with `finalize_lock`.
- Flushes dirty data buffers first.
- Takes the sync lock exclusively before metadata/UNDO-sensitive operations.
- On final cycles, copies cached blockmaps into the root volume and generates undo-protected modifications.
- Saves the undo append point, flushes UNDOs, and updates on-disk undo FIFO pointers when needed.
- Updates and flushes `vol0_next_tid` without undo so TIDs are not reused after rollback.
- For pre-version-4 filesystems, waits for I/O because recovery depends on the volume header update.
- Flushes metadata asynchronously after undo is safe.
- On final cycles, advances cached undo `first_offset`, clears undo history, advances flush TID state, and clears redo sync state.

## Pressure and Work Detection

- `hammer_flusher_undo_exhausted()` reports undo space below a quarter threshold chosen by caller.
- `hammer_flusher_meta_limit()` and `hammer_flusher_meta_halflimit()` guard dirty metadata pressure.
- `hammer_flusher_haswork()` checks dirty inodes, dirty volume/undo/data/meta roots, and pending undo FIFO synchronization.
- `hammer_flush_dirty()` repeatedly syncs while work remains, with a max-count escape.

## Research Notes

This file coordinates HAMMER’s crash-consistency protocol. The key design is that metadata can flush asynchronously only after corresponding UNDO state is durable enough for recovery, while data writes are handled separately because HAMMER does not overwrite file data in the same way.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_flusher.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_inode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_inode.c

## Role

Implements HAMMER in-memory inode caching, vnode association, inode creation/loading, pseudo-filesystem metadata caching, inode dirtying, dependency-aware flush setup, backend inode synchronization, deletion, reclaim throttling, and unmount cleanup.

## Inode Indexes

- `hammer_ino_rb_compare()` orders cached inodes by localization, object id, and as-of TID.
- `hammer_redo_rb_compare()` orders inodes by redo FIFO start.
- Lookup helpers support exact lookup, all-history scanning for one object, and PFS-localization scanning.
- `hammer_pfs_rb_compare()` indexes cached PFS metadata by localization.
- RB generators create inode and PFS trees plus special lookup support for `hammer_inode_info`.

## Vnode Lifecycle

- `hammer_vop_inactive()` recycles zero-link inodes quickly and queues dirty state before reclaim pressure grows.
- `hammer_vop_reclaim()` breaks vnode/inode association under the inode lock, marks reclaim state, clears vnode dirty state, and releases the inode.
- `hammer_get_vnode()` creates or reacquires a vnode for a referenced inode, sets vnode type/ops, device aliases, root flags, and VM object sizing for regular files.
- `hammer_inode_dirty()` marks the vnode dirty when inode mod flags are present.

## Inode Lookup and Creation

- `hammer_get_inode()` first checks the RB cache, then loads the inode record from the B-tree using directory node-cache hints, copies leaf/data into memory, initializes per-inode B-tree caches, and attaches PFS metadata.
- `hammer_get_dummy_inode()` creates a read-only dummy FIFO inode for broken directory entries without marking it as on-disk.
- `hammer_find_inode()` returns only cached, non-dummy inodes.
- `hammer_create_inode()` creates a new in-memory inode, allocates an object id or PFS root id, initializes inode leaf/data, inherits nohistory/nodump flags, assigns uid/gid UUIDs, sets directory capability flags by filesystem version, and inserts the inode into the cache.
- `hammer_free_inode()` releases node caches, reclaim state, object-id cache, PFS refs, and memory.

## Pseudo-Filesystem Handling

- `hammer_load_pseudofs()` loads or creates an in-memory PFS record. PFS records are stored under the real root inode, not the PFS root inode.
- `hammer_save_pseudofs()` replaces an in-memory PFS record by marking any in-memory old record deleted and adding a new general record.
- `hammer_mkroot_pseudofs()` creates a root directory inode for a PFS if absent and increments its link count.
- `hammer_unload_pseudofs()` tries several flush cycles to detach all inodes for a localization, returning `ENOTEMPTY` if users still hold files.
- `hammer_rel_pseudofs()` removes cached PFS metadata once its lock refs drop to zero.

## Dirtying and Timestamp Updates

- `hammer_modify_inode()` sets inode dirty flags, reserves inode space accounting, marks transactions with `HAMMER_TRANSF_NEWINODE` on first dirty transition, and updates vnode dirty state.
- `hammer_update_atime_quick()` can update in-memory atime without the filesystem token when the inode already has pending ATIME state.
- `hammer_update_itimes()` updates on-disk atime/mtime in place. MTIME uses UNDO; ATIME-only updates use no-undo modification because mtime/atime are outside the inode CRC region.

## Flush Group Setup

- `hammer_flush_inode()` assigns dirty inodes to flush groups, creates new groups when necessary, closes overfull groups, and handles IDLE/SETUP/FLUSH states.
- `hammer_setup_parent_inodes()` and `hammer_setup_parent_inodes_helper()` walk directory-entry dependencies upward so a child inode is only flushed when it has valid namespace connectivity.
- Recursion is capped at depth 20 to avoid kernel stack blowout; unresolved dependencies set `CONN_DOWN` and `REFLUSH`.
- `hammer_flush_inode_core()` transitions an inode into `HAMMER_FST_FLUSH`, snapshots frontend inode state into backend `sync_*` fields, moves eligible records into the flush group, handles truncation state, and auto-closes large groups.

## Record Dependency Handling

- `hammer_setup_child_callback()` scans an inode’s in-memory record tree and decides which records can join the current flush group.
- Idle records can flush immediately.
- Setup records represent dependencies, commonly directory adds/deletes tied to target inodes.
- Directory adds can force target inode flushing so the target becomes visible in the same group.
- Overfull groups trigger reflush/resignal to avoid exhausting UNDO space.
- Already flushing directory records can belong to older groups and still count as effectively flushed for the current group.

## Backend Sync

`hammer_sync_inode()` is the core backend flusher path:

- Initializes a cursor using inode data-cache hints.
- Computes the link count that should be synchronized by accounting for directory records in or out of the current flush group.
- Processes pending truncation by deleting on-media data beyond the aligned truncation point.
- Emits REDO termination for truncations when version 4+ redo state exists.
- Syncs in-memory records through `hammer_sync_record_callback()`.
- Re-seeks toward the cached inode node when possible before updating inode metadata.
- Deletes auxiliary records and marks the inode deleted when link count is zero, records are gone, and deletion is pending.
- Writes initial or replacement inode records through `hammer_update_inode()`.
- Uses `hammer_update_itimes()` for timestamp-only updates when possible.
- Reports critical errors through `hammer_critical_error()`.

## Record Sync Details

- `hammer_sync_record_callback()` processes only records in the inode’s current flush group.
- It sets backend interlock flags so frontend deletion state cannot change unsafely.
- Frontend-deleted directory adds are converted into delete-on-disk records when needed.
- New records receive the transaction TID and create timestamp.
- REDO data records generate `HAMMER_REDO_TERM_WRITE` when committed.
- `EDEADLK` restarts cursor state.
- High metadata pressure or severe VM paging temporarily unlocks the cursor, finalizes the flusher, and relocks the cursor.

## Completion, Deletion, and Reclaim

- `hammer_sync_inode_done()` merges backend `sync_flags` back to frontend state, handles `WOULDBLOCK`, removes completed inodes from flush groups, wakes waiters, schedules reflushes, clears reservations, and releases clean idle inodes.
- `hammer_wait_inode()` waits for FLUSH or signaled SETUP state and forces async flushing if the group is not yet closed.
- `hammer_inode_unloadable_check()` marks zero-link, non-read-only inodes as deleting and truncates buffers to zero.
- `hammer_test_inode()` triggers pending reflush after dependency resolution.
- `hammer_destroy_inode_callback()` forcibly tears down in-memory records and flush state during critical-error unmount cleanup.
- `hammer_reload_inode()` updates cached inode read-only flags when mount state changes.

## Reclaim Throttling

- `hammer_inode_wakereclaims()` clears reclaim accounting and wakes blocked reclaim waiters.
- `hammer_inode_waitreclaims()` throttles inode creation/loading when too many detached dirty inodes accumulate, using per-process pressure history.
- `hammer_inode_inostats()` maintains a small loose set-associative per-pid statistic with decay over ticks.
- Disabled `hammer_inode_waithard()` shows an older harder flush-wait recovery mechanism.

## Research Notes

This file is the main bridge between HAMMER’s VFS-facing inode/vnode model and its copy-on-write historical B-tree storage. The most important behavior is dependency-aware flushing: directory entries, target inodes, link counts, truncations, REDO/UNDO state, and inode records are all synchronized as a group without violating visibility or crash-recovery invariants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_inode.c -->