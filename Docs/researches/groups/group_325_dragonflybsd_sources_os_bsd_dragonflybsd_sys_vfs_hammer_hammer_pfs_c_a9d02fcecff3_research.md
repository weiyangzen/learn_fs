# Group Research: group_325_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer_hammer_pfs_c_a9d02fcecff3

Scope: `Docs/research_subset_a.md`; source tree `sources/os/bsd/dragonflybsd`; subsystem `sys/vfs/hammer`.

This group covers HAMMER1 administrative ioctls for pseudo-filesystems, pruning, rebalancing, reblocking, recovery, UNDO/REDO logging, interruption checks, structural support routines, transaction/object-id allocation, and VFS mount/export glue.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_pfs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_pfs.c

Purpose: implements HAMMER pseudo-filesystem ioctl operations. PFS ids are mapped to localization bits, and most entry points accept an inode only as context for autodetecting a default PFS id.

Key entry points:
- `hammer_ioc_get_pseudofs()` autodetects the PFS, loads in-memory PFS state, reports current `hammer_pseudofs_data`, and for master PFSs refreshes `sync_end_tid` from `flush_tid1`.
- `hammer_ioc_set_pseudofs()` copies user-supplied PFS data into the in-core PFS, creates a root inode when switching/creating a master PFS, persists it, and wakes waiters on `sync_end_tid`.
- `hammer_ioc_upgrade_pseudofs()` unloads cached PFS state, rolls a slave back to `sync_end_tid + 1`, clears the slave flag, and saves it.
- `hammer_ioc_downgrade_pseudofs()` marks a master as slave and advances `sync_end_tid` to at least `flush_tid1`.
- `hammer_ioc_destroy_pseudofs()` rolls the PFS back with `trunc_tid == 0` and marks it deleted.
- `hammer_ioc_wait_pseudofs()` sleeps until either a slave PFS `sync_end_tid` or master `flush_tid1` has advanced past the requested value.
- `hammer_ioc_scan_pseudofs()` directly scans the root misc PFS record without using the cached PFS RB tree.

Important internals: `hammer_pfs_autodetect()` validates ids and user buffer size. `hammer_pfs_rollback()` performs a mirror-filtered backend B-tree scan over the PFS localization and applies rollback edits through `hammer_pfs_delete_at_cursor()`: records created at or after the truncation TID are destroyed, while records deleted at or after the truncation TID are undeleted by adjusting `delete_tid` to zero.

Concurrency and recovery behavior: long rollback scans call `hammer_signal_check()` and return ioctl interruption via `HAMMER_IOC_HEAD_INTR`; they also pause on metadata/UNDO pressure using flusher waits. Cursor retry handles `EDEADLK`. PFS upgrades/destroys intentionally unload cached PFS state before mutation.

Research notes: this file is the PFS state-control layer, not the root PFS record serializer itself. It relies heavily on common HAMMER cursor deletion semantics and mirror-filtered scans to make slave promotion safe after partial mirror syncs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_pfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_prune.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_prune.c

Purpose: implements the pruning ioctl that removes historical deleted records when their create/delete TIDs fall within retention windows supplied by userland.

Main flow: `hammer_ioc_prune()` validates the key range, rejects caller-supplied PFS localization bits, copies the prune element array from userland, derives scan localizations from the ioctl inode, and scans backward from `key_end` toward `key_beg`. Reverse iteration avoids creating overlapping records ahead of the scan when delete operations adjust B-tree boundaries.

Deletion decision: `prune_should_delete()` supports two modes. With `HAMMER_IOC_PRUNE_ALL`, any record with nonzero `delete_tid` is removed. Otherwise the caller supplies a descending list of prune windows, and a deleted record is removable only when `create_tid` and `delete_tid` fall within the same modulo bucket between `beg_tid` and `end_tid`.

Mutation behavior: deletions use `hammer_delete_at_cursor(... HAMMER_DELETE_DESTROY ...)` under the sync lock so the change remains within one flush group. Directory and non-directory record statistics are updated separately, and byte counts come from the delete call.

Extra cleanup: `prune_check_nlinks()` detects live inode records with zero link count, obtains and releases the inode, and lets inode reclamation clean dangling state that can result from crashes with deleted files still open.

Operational behavior: the loop honors read-only transition (`EROFS`), user interruption (`EINTR` converted to ioctl interrupt flag), B-tree deadlock retry, and flusher backpressure when metadata or UNDO space is tight. `key_cur` is normalized back to a type-only localization before returning to userland.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_prune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_rebalance.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_rebalance.c

Purpose: implements the B-tree rebalance ioctl. It repacks child node elements under internal nodes to reduce sparse nodes and delete excess children after pruning or other churn.

Top-level behavior: `hammer_ioc_rebalance()` validates caller ranges, clamps the requested saturation between half and full internal-node capacity, derives per-PFS or all-PFS localizations, and walks the B-tree forward with `HAMMER_CURSOR_REBLOCKING` so internal nodes are returned on the upward traversal. Leaf visits are collapsed to their last element because the parent/internal node is the object of interest.

Core algorithm: `rebalance_node()` upgrades the cursor, locks the parent, children, and grandchildren, copies locked on-disk nodes, counts all child elements, calculates a target average element count, and packs elements into earlier child nodes. If the average occupancy is below requested saturation, it reduces the desired child count and recomputes the average.

Metadata maintenance: while moving elements, the code updates mirror TIDs, parent internal-element boundaries, child parent pointers for moved internal elements, and live cursor tracking via `hammer_cursor_moved_element()`, `hammer_cursor_removed_node()`, and related helpers. Extra nodes beyond the new packed range are marked deleted in the copied node images and then synced with `hammer_btree_sync_copy()`.

Boundary helpers: `rebalance_closeout()` updates child counts, right-hand boundaries for internal children, and parent boundary base keys while preserving parent btype/internal metadata. `rebalance_parent_ptrs()` repoints a moved child node to its new parent and informs cursor tracking.

Operational behavior: rebalancing watches memory pressure (`vm_test_nominal()`), read-only transitions, user signals, metadata/UNDO pressure, and B-tree deadlocks. The operation is sync-lock protected only around actual node rebalancing, not the whole scan.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_rebalance.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_reblock.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_reblock.c

Purpose: implements HAMMER reblocking, which relocates records, data, and/or B-tree nodes out of fragmented big-blocks so the old big-blocks can become fully free.

Top-level behavior: `hammer_ioc_reblock()` validates object-id range and free threshold, maps a high `free_level` to emergency space checking, derives localizations for current PFS or all PFSs, and scans the B-tree. It optionally asks the scan to return internal nodes when `HAMMER_IOC_DO_BTREE` is set.

Decision logic: `hammer_reblock_helper()` first handles record data only for leaf record elements with nonzero `data_offset`. Record type maps to ioctl class flags: inodes/snapshots/config, directories/metadata records, or file data/database records. It then checks target volume filtering, accounts candidate bytes, queries free bytes in the current big-block, and relocates only when the big-block meets the threshold and is not the allocator's current big-block unless forced by threshold zero.

Data relocation: `hammer_reblock_data()` extracts existing data, allocates a new data block, copies the payload, recalculates the leaf CRC using the current filesystem version, invalidates cursor data cache before freeing the old block, updates `data_offset` and `data_crc` in the B-tree node, and releases the new buffer.

B-tree node relocation: `hammer_reblock_leaf_node()` and `hammer_reblock_int_node()` allocate a new node, copy the old node through `hammer_move_node()`, update parent/root references, update children parent pointers for internal nodes, inform cursor tracking, delete the old node, and replace the cursor node.

Operational behavior: the code carefully unlocks around vnode-cache uncaching and buffer-cache pressure, then retests cursor stability. It retries on `EWOULDBLOCK` after a sync and on `EDEADLK`, handles interrupts with ioctl flags, and pauses for metadata/UNDO pressure. Reblocking is sync-lock protected during individual relocation work.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_reblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_recover.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_recover.c

Purpose: implements mount-time recovery. Stage 1 replays raw UNDO records backward to restore metadata consistency. Stage 2 replays logical REDO records forward when REDO recovery is required.

Stage 1: `hammer_recover_stage1()` reads the root volume UNDO blockmap, validates FIFO indices, and for version 4+ filesystems discovers the real active FIFO range by scanning backward for the prior sequence number then forward until sequence discontinuity. It scans the active range backward, applies each UNDO via `hammer_recover_undo()`, and records the first backward-seen `HAMMER_REDO_SYNC` as the stage2 extended-range start. It updates root volume FIFO indices to the recovered range and flushes or discards recovered buffers depending on success and read-only mode.

UNDO execution: `hammer_recover_undo()` accepts only UNDO records, validates payload size and target offset, and restores bytes into either raw volume headers or raw metadata buffers without generating new UNDO. Recovered buffers/volumes are marked so the recovery flush routine can delay or discard writes safely.

Stage 2: `hammer_recover_stage2()` runs only on read-write mounts or read-only-to-read-write transition. It respects tunable `vfs.hammer.skip_redo`. It computes the nominal UNDO range and REDO extended range from `recover_stage2_offset`, backward-scans the extended-only area to collect `REDO_TERM_WRITE`/`REDO_TERM_TRUNC` records into an RB tree, then forward-scans the full extended range and executes `REDO_WRITE` or `REDO_TRUNC` records that do not have matching termination records.

REDO execution: `hammer_recover_redo_exec()` starts a transaction, finds the inode by object id/localization, obtains its vnode, and performs either `vn_rdwr()` for write payloads or `VOP_SETATTR()` for truncation. REDO recovery disables recursive REDO semantics through mount flags handled by the REDO generator.

FIFO scanning and validation: `hammer_recover_scan_rev()` and `hammer_recover_scan_fwd()` walk circular UNDO space while handling wraparound. Signature helpers verify head/tail signatures, alignment, record size, buffer-boundary containment, type/size agreement, and CRC for non-PAD records.

Flush handling: `hammer_recover_flush_buffers()` writes recovered buffers first, then volume headers, with the root volume header flushed last on final success. With `final < 0`, it clears error/modified state and discards recovered buffers for failed or read-only recovery teardown.

Risk surface: this file is the crash-consistency center for HAMMER. Sequence monotonicity, FIFO wrap detection, and the distinction between nominal UNDO range and extended REDO range are critical to avoiding replaying stale logical operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_redo.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_redo.c

Purpose: generates REDO records in the shared UNDO/REDO FIFO for HAMMER version 4+ fsync acceleration and crash recovery.

Main generator: `hammer_generate_redo()` appends one or more REDO records under `undo_lock`, wrapping the FIFO as needed and preformatting new FIFO buffers. It handles insufficient aligned space by writing PAD records, writes sequence-numbered and CRC-protected REDO records, appends a tail, and writes a dummy PAD up to the next alignment point so recovery can scan without trusting volume-header indices.

Inode tracking: for inode-related REDOs, the first active FIFO offset is stored in `ip->redo_fifo_start`, and the inode is inserted into `hmp->rb_redo_root` under `HAMMER_INODE_RDIRTY`. `redo_fifo_next` tracks the next earliest REDO while an inode is being flushed to the backend.

SYNC records: `hammer_generate_redo_sync()` emits `HAMMER_REDO_SYNC` containing the earliest active REDO FIFO offset. During REDO recovery it reuses the original recovery extended offset so a second crash can rerun the same logical REDOs. Normal UNDO generation forces at least one SYNC record into the nominal recovery span.

Flush hooks: `hammer_redo_fifo_start_flush()` clears `redo_fifo_next` as an inode begins backend flush. `hammer_redo_fifo_end_flush()` removes stale RDIRTY state, clears tracking when no dirty buffers remain, or reinserts the inode with `redo_fifo_start = redo_fifo_next`.

Research notes: this file mirrors much of the FIFO layout logic in `hammer_undo.c`; the difference is logical operation replay rather than raw block restoration. Correct RB ordering by earliest FIFO offset is essential because stage2 recovery uses the minimum active REDO offset.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_redo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_signal.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_signal.c

Purpose: provides a small helper for interruptible long-running HAMMER ioctl operations such as prune, rebalance, reblock, and PFS rollback.

Behavior: `hammer_signal_check()` yields the current LWKT thread on every call, then checks for pending actionable user signals only once every 100 calls via `hmp->check_interrupt`. It uses `CURSIG_NOBLOCK(curthread->td_lwp)` so it does not block or stop the thread while polling.

Return contract: returns `0` when work should continue and `EINTR` when a signal is pending. Callers commonly translate `EINTR` into an ioctl header interrupt flag and return success to userland so administrative tools can resume or report partial progress.

Research notes: the helper is intentionally lightweight and mount-scoped. Its throttled check avoids excessive signal polling inside tight B-tree scans while still keeping maintenance ioctls responsive.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_signal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_subs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_subs.c

Purpose: contains HAMMER structural locking, reference-count interlocks, sync-lock wrappers, and miscellaneous conversion/hash helpers shared across the filesystem.

Locking primitives: `hammer_lock_ex_ident()`, `hammer_lock_ex_try()`, `hammer_lock_sh()`, `hammer_lock_sh_try()`, `hammer_lock_upgrade()`, `hammer_lock_downgrade()`, `hammer_unlock()`, and `hammer_lock_status()` implement a compact shared/exclusive lock in `struct hammer_lock`. Exclusive locking is recursive for the owning thread; shared locking while owning exclusive is treated as a debug-critical case but allowed after incrementing the count.

Reference interlocks: `hammer_ref()`/`hammer_rel()` maintain structural references. `hammer_ref_interlock()`, `hammer_ref_interlock_true()`, `hammer_ref_interlock_done()`, `hammer_rel_interlock()`, `hammer_rel_interlock_done()`, `hammer_get_interlock()`, `hammer_try_interlock_norefs()`, and `hammer_put_interlock()` combine ref transitions with a serialized CHECK/LOCKED/WANTED protocol used by buffer, node, volume, and inode lifecycle paths.

Sync lock: `hammer_sync_lock_ex()`, `hammer_sync_lock_sh()`, `hammer_sync_lock_sh_try()`, and `hammer_sync_unlock()` wrap `hmp->sync_lock` and track transaction lock references. The comments define the invariant: metadata mutations under shared sync lock belong to the same flush group, while the flusher uses exclusive sync lock.

Miscellaneous helpers: the file maps HAMMER object types to vnode and directory-entry types, converts between HAMMER time and `timespec`, maps GUIDs/UUIDs, computes `fsid` device values, implements no-history deletion policy, parses snapshot/PFS TID strings, and chooses HAMMER block size/offset across the extended-buffer demarcation.

Directory hashing: `hammer_direntry_namekey()` implements legacy ALG0 and segmented ALG1 hashes. ALG1 hashes filename segments separated by punctuation into upper key bits and adds a full-name CRC component to reduce collisions; the function avoids zero and reserves positive key space for normal directory entries.

Research notes: this file defines low-level invariants assumed by every other file in the group. The custom ref interlock API is subtle: a return value of `1` means the caller owns a transition/check responsibility, not necessarily that the reference count stayed at zero or one.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_subs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_transaction.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_transaction.c

Purpose: manages lightweight HAMMER transaction setup/teardown and allocates transaction/object identifiers.

Transactions: `hammer_start_transaction()` creates a standard transaction with a referenced root volume, timestamp fields, and no TID until one is needed. `hammer_simple_transaction()` creates a read-only transaction with the same timestamp/root-volume setup. `hammer_start_transaction_fls()` is for the flusher thread, preallocates a TID, and starts with one sync-lock reference to reflect flusher serialization. `hammer_done_transaction()` releases the root volume, asserts expected sync-lock references, and waits for inode reclaim work when new inodes were created.

TID allocation: `hammer_alloc_tid()` normally advances `hmp->next_tid` linearly. In master-id mode it aligns allocations to `HAMMER_MAX_MASTERS` and ORs in the master id so transaction ids can be partitioned by master. The file notes HAMMER1 no longer supports multi-master clustering as of 2015, but the encoding remains.

Object-id allocation: `hammer_alloc_objid()` maintains a per-directory object-id cache. It allocates a bulk TID range, chooses a bit based on high bits of the directory entry namekey, and frees or recycles caches based on fill level. The goal is to distribute inode numbers while preserving some relation to directory-entry hash space.

Cache helpers: `ocp_allocbit()` finds and marks an available bit in the two-level bitmap. `hammer_clear_objid()` detaches a directory's cache and moves it to the front of the mount list. `hammer_destroy_objid_cache()` frees all object-id caches during mount teardown.

Research notes: transactions here are not heavyweight journaling objects; the actual persistence mechanism is the sync lock plus UNDO/REDO FIFO. This file supplies the monotonic identifiers that version HAMMER records and object ids.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_undo.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_undo.c

Purpose: manages the UNDO side of the shared UNDO/REDO FIFO and the recent-UNDO history cache.

Offset lookup: `hammer_undo_lookup()` converts a zone-3 UNDO offset into the underlying zone-2 buffer offset through the root volume's undo translation.

UNDO generation: `hammer_generate_undo()` ensures a REDO_SYNC exists for version 4+ filesystems, checks recent undo history to avoid duplicate coverage, locks the FIFO, verifies space, appends one or more UNDO records, and writes PAD records when alignment leaves no room for payload. Each UNDO record stores the target raw zone offset and a copy of original bytes; records have sequence numbers, tails, and CRCs.

FIFO formatting and upgrade: `hammer_format_undo()` preformats a new FIFO buffer with DUMMY records on every 512-byte alignment unit so recovery can detect stale or missed writes. `hammer_upgrade_undo_4()` converts pre-version-4 undo space by resetting first/next offsets and writing DUMMY entries with sequence numbers across the entire undo area.

History cache: `hammer_enter_undo_history()` stores recent offset/length ranges in an RB tree plus LRU list and returns `EALREADY` when a new request is fully covered by an existing undo. `hammer_clear_undo_history()` resets that cache.

Space accounting: `hammer_undo_used()`, `hammer_undo_space()`, and `hammer_undo_max()` compute FIFO usage using the in-core next offset and on-disk first offset, including space reserved from the previous flush. `hammer_undo_reclaim()` keeps the current append buffer resident and permits reclaim of other undo buffers.

Research notes: UNDO records are raw physical restorations replayed backward by recovery. The history cache is an optimization only; correctness still depends on generating the first UNDO before modifying any raw metadata bytes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_undo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vfsops.c

Purpose: registers HAMMER with the DragonFly VFS layer, exposes tunables/sysctls/statistics, and implements mount, unmount, root/vget, stat, sync, file-handle, and export operations.

Global controls: the file defines debug knobs, counters, dirty-buffer limits, record limits, REDO limits, fsync mode, noatime default, and SYSCTL entries under `vfs.hammer`. `hammer_vfs_init()` autosizes record and dirty-buffer limits and initializes reclaim limits.

Mount path: `hammer_vfs_mount()` handles both boot root mounts and normal mounts. It validates volume count and master id, allocates and initializes `hammer_mount`, lock refs, RB trees, tokens, volume lists, object-id/undo/reclaim lists, and root B-tree key bounds. It loads all volumes, checks root volume presence and volume completeness, installs vnode ops, caches the root blockmap, validates filesystem version, computes UNDO record limits, runs `hammer_recover_stage1()`, initializes fsid/stat fields, caches next TID and blockmap state, starts the flusher, obtains the root vnode, and runs `hammer_recover_stage2()` for read-write mounts.

Mount updates: read-only to read-write adjusts volume mode, flushes recovered buffers, runs stage2 recovery, refreshes blockmaps, and reloads inodes. Read-write to read-only reloads inodes, performs multiple flusher syncs, then adjusts volume mode.

Unmount/free: `hammer_vfs_unmount()` flushes vnodes and calls `hammer_free_hmp()`. The free path flushes dirty state, destroys inodes on critical error, asserts empty inode/flush structures, destroys the flusher, discards recovered buffers for read-only mounts, unloads buffers and volumes, destroys object-id caches and kmalloc pools, releases the filesystem token, and frees the mount.

VFS operations: `hammer_vfs_vget()` looks up an inode by object id and PFS localization and returns a locked vnode. `hammer_vfs_root()` vgets object id 1. `hammer_vfs_statfs()` and `hammer_vfs_statvfs()` report inode count and free blocks minus reserved space. `hammer_vfs_sync()` delegates to `hammer_sync_hmp()` unless panicking.

NFS/export support: `hammer_vfs_vptofh()` stores PFS id, object id, and as-of TID in file handles. `hammer_vfs_fhtovp()` reconstructs vnode lookups and can enforce root vnode PFS isolation for null-mounted PFS exports. `hammer_vfs_checkexp()` and `hammer_vfs_export()` integrate with DragonFly export controls.

Critical errors: `hammer_critical_error()` marks the mount critical, rate-limits a diagnostic, forces read-only mode by adjusting volume modes, records the error, and optionally enters the debugger.

Research notes: this file ties together nearly every other file in this group. The mount sequence is especially recovery-sensitive: stage1 runs before high-level B-tree use, while stage2 waits until the mount structure, flusher, and root vnode path are available.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_vfsops.c -->