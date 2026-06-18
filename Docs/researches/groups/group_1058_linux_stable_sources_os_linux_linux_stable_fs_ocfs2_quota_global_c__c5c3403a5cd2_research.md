# Group Research: group_1058_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_quota_global_c__c5c3403a5cd2

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota_global.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota_global.c

Purpose: Implements OCFS2 operations over cluster-wide global quota files: qtree serialization, physical quota block I/O, global quota info updates, periodic local-to-global sync, and Linux quota operation hooks.

Read coverage: complete file read, 1051 lines.

Key responsibilities:
- Converts OCFS2 global on-disk dquot records to/from generic `struct dquot`.
- Provides `ocfs2_global_ops` for qtree quota format operations.
- Validates quota metadata ECC trailers and reads quota blocks by physical block number.
- Implements `ocfs2_quota_read()` and `ocfs2_quota_write()` using extent maps and direct buffer-head I/O, bypassing page cache.
- Coordinates global quota file locking through `ocfs2_lock_global_qf()` / `ocfs2_unlock_global_qf()`.

Major logic:
- `ocfs2_global_read_info()` opens the relevant global system quota inode, initializes `ocfs2_mem_dqinfo`, reads qtree header state, initializes qinfo lock resources, and schedules delayed quota sync work.
- `__ocfs2_global_write_info()` persists grace periods, sync interval, qtree block counts, free block, and free entry state.
- `__ocfs2_sync_dquot()` merges local dquot deltas with the global record, preserves admin-set fields, adjusts grace timers, updates origin counters, changes use count on freeing, writes the qtree record, and may release unused global records.
- `qsync_work_fn()` periodically scans active dquots while avoiding `s_umount` deadlock with `down_read_trylock()`.
- `ocfs2_acquire_dquot()` reads or creates a global qtree entry, increments global use count, preallocates global quota file space if needed, then creates the corresponding local quota entry.
- `ocfs2_release_dquot()` drops global and local references, with delayed handling when called from the downconvert thread.

Concurrency and risks:
- The file documents strict lock ordering among transactions, `dqio_sem`, dquot locks, global quota inode locks, qinfo locks, and local quota inode locks.
- `ocfs2_quota_write()` requires an active transaction and enough credits.
- New global quota entries may need file extension before transaction start because allocator locking ranks above transaction start.
- Last-reference dquot release cannot safely take quota locks from the downconvert thread, so it queues delayed reference dropping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota_global.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota_local.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota_local.c

Purpose: Implements OCFS2 node-local quota files. These files store per-node quota deltas and use chunk bitmaps so quota state can be recovered after a node crash and folded into the global quota file.

Read coverage: complete file read, 1318 lines.

Key responsibilities:
- Defines local quota chunk/block/entry offset helpers.
- Validates local and global quota file magic/version during quota enable.
- Loads local quota chunk bitmaps into memory and releases them on quota shutdown.
- Writes local quota info headers and local dquot delta records.
- Creates and releases per-node local dquot entries.
- Performs quota recovery for crashed slots.

Major logic:
- `ocfs2_modify_bh()` wraps a small journal transaction around a buffer-head mutation callback.
- `ocfs2_read_quota_block()` reads logical quota file blocks and validates quota ECC, refusing reads beyond file size as corruption.
- `ocfs2_begin_quota_recovery()` scans a crashed slot’s local quota files after journal replay and records chunks with allocated entries.
- `ocfs2_finish_quota_recovery()` locks the crashed local quota file, replays pending local deltas into global quota records, then marks recovered files clean when appropriate.
- `ocfs2_local_read_info()` initializes `ocfs2_mem_dqinfo`, reads global and local quota headers, loads chunk bitmaps, queues self-recovery if the local file was dirty, and marks the local file in-use.
- `ocfs2_local_free_info()` checks that all local entries were freed, marks the file clean if safe, releases global lock resources, unlocks the local quota inode, and frees memory.

Allocation behavior:
- `ocfs2_find_free_entry()` searches loaded chunk bitmaps for a free local dquot slot.
- `ocfs2_local_quota_add_chunk()` extends an empty/full local quota file by adding a chunk header and first entry block.
- `ocfs2_extend_local_quota_file()` adds an entry block to the last chunk until full, then creates a new chunk.
- `ocfs2_create_local_dquot()` allocates a bitmap slot, records local file offset and physical block in `ocfs2_dquot`, writes the initial local delta record, and marks the slot allocated.

Risks:
- Local quota files are intentionally dirty while mounted; clean marking is withheld if entries remain allocated or recovery was aborted.
- Recovery must drop the crashed node’s global use count while applying its local space/inode deltas.
- Chunk bitmap corruption can make free count and actual free bits disagree, returning `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota_local.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.c

Purpose: Implements OCFS2 refcount trees, copy-on-write, reflink creation/remapping, refcounted xattr handling, and shared extent reference-count mutation.

Read coverage: complete file read, 4806 lines.

Key structures:
- `struct ocfs2_cow_context` bundles inode, target COW range, data extent tree, refcount tree/root, allocators, deferred deallocation, optional xattr object, and cluster duplication callbacks.
- Refcount trees are cached in `osb->osb_rf_lock_tree`, keyed by root block number, with an LRU pointer for repeated lookup.
- Refcount records store physical cluster positions, cluster counts, and reference counts; roots can be inline record lists or extent-tree roots pointing to leaf refcount blocks.

Major areas:
- Tree lifetime: validates refcount blocks, caches `ocfs2_refcount_tree` objects, locks via DLM plus local `rf_sem`, detects root-block generation reuse, creates new roots, attaches inodes to existing roots, decrements root use count, and frees unused roots.
- Record mutation: locates records or holes, inserts/splits/merges records, increases/decreases refcounts, expands inline roots into leaf-backed trees, splits full leaves, and removes empty leaf blocks.
- COW: computes COW ranges near `MAX_CONTIG_BYTES` boundaries, reserves metadata/data allocators, clears refcount flags when refcount is one, allocates replacement clusters when refcount is greater than one, duplicates data, updates extent trees, and decrements old refcounts.
- Xattrs: applies similar refcount and COW logic to xattr value roots, using journaled block duplication and optional post-refcount callbacks.
- Reflink: attaches source inodes to refcount trees, marks existing data/xattr extents refcounted, creates reflink targets, duplicates inline data or extent lists, copies xattrs, completes inode metadata, and moves orphan-created targets into the destination directory.
- Remap: supports range remapping when source and destination share one refcount tree, punches destination ranges, maps shared extents, and updates refcounts.

Concurrency and dependencies:
- Uses OCFS2 DLM refcount locks, local rwsem `rf_sem`, metadata cache locking, inode cluster locks, VFS inode locks, `ip_alloc_sem`, `ip_xattr_sem`, and ordered double-inode locking.
- All on-disk refcount, extent, dinode, and xattr changes are journaled with explicit credit calculation and metadata allocator reservations.
- Depends heavily on OCFS2 extent-tree helpers, suballocators, truncate-log/deferred deallocation, xattrs, quota accounting, page cache, writeback, inode security, namei, and symlink helpers.

Risks:
- Refcount root block reuse is guarded by generation checks; missing this would make locks protect stale metadata.
- Split logic depends on 64-bit record ordering while btree indexing uses low 32-bit positions.
- COW invalidates extent maps after attempted replacement because both success and partial failure can stale cached mappings.
- Reflink does not merge different refcount trees; that case returns `-EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.h

Purpose: Declares OCFS2 refcount tree state and public APIs for COW, reflink, refcount adjustment, xattr refcounting, and reflink inode locking.

Read coverage: complete file read, 127 lines.

Key contents:
- Defines `struct ocfs2_refcount_tree`, the in-memory cached refcount-tree object keyed by root block number.
- The structure embeds rb-tree linkage, root block number, generation, kref, local rwsem, cluster lock resource, removal flag, metadata cache state, cache spinlock, I/O mutex, and superblock pointer.
- Declares tree lock/unlock/purge APIs.
- Declares refcount mutation APIs: increase, decrease, prepare-for-delete credit calculation, add refcount flag, remove tree, and try-remove tree.
- Declares COW and duplication APIs for file data and xattr data.
- Defines `struct ocfs2_post_refcount`, allowing callers to run extra journaled work inside a refcount transaction.
- Declares reflink ioctl, block remap, destination-size update, and double-inode lock helpers.

Risks:
- The header exposes transaction-coupled interfaces that require callers to pass correct handles, alloc contexts, cached deallocation contexts, and already-locked metadata.
- `ocfs2_post_refcount` makes transaction credit accounting caller-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/refcounttree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/reservations.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/reservations.c

Purpose: Implements in-memory allocation reservation windows for OCFS2 bitmap allocation, improving locality by reserving free ranges per allocation context.

Read coverage: complete file read, 824 lines.

Key responsibilities:
- Maintains non-overlapping reservation windows in an rb-tree and an LRU list.
- Sizes reservation windows from mount reservation levels, with separate sizing for directory reservations.
- Validates reservation invariants under debug builds.
- Finds free bitmap gaps not covered by existing reservations.
- Discards, restarts, cannibalizes, and updates reservations as allocation windows are consumed.

Major logic:
- `ocfs2_resmap_init()` initializes an empty reservation map tied to an `ocfs2_super`.
- `ocfs2_resmap_restart()` clears all current windows and attaches a new disk bitmap/length, typically when the local allocation window changes.
- `ocfs2_resv_insert()` inserts a non-overlapping reservation into the rb-tree and appends it to the LRU.
- `ocfs2_find_resv_lhs()` finds the reservation containing or immediately before a goal bit.
- `ocfs2_resmap_find_free_bits()` scans a bitmap gap for the best free run up to the wanted length.
- `ocfs2_resv_find_window()` tries to place a reservation near the last allocation, retries from zero, and finally cannibalizes the oldest reservation if no gap is available.
- `ocfs2_resmap_resv_bits()` returns a valid reserved range to the allocator, allocating a new window if needed.
- `ocfs2_resmap_claimed_bits()` trims or removes a reservation after bits are allocated and records the most recent allocation for future placement.

Risks:
- Reservation windows must never overlap each other or allocated disk bitmap bits.
- Temporary reservations avoid over-allocation by requesting only the caller’s needed length.
- Cannibalization can shrink or remove older reservations to make progress.
- Disabled reservations return `-ENOSPC`, so callers must fall back to non-reserved allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/reservations.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/reservations.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/reservations.h

Purpose: Declares OCFS2 allocation reservation structures, flags, tuning bounds, and reservation-map APIs.

Read coverage: complete file read, 144 lines.

Key contents:
- Defines reservation level bounds: `OCFS2_DEFAULT_RESV_LEVEL`, `OCFS2_MAX_RESV_LEVEL`, and `OCFS2_MIN_RESV_LEVEL`.
- Defines `struct ocfs2_alloc_reservation` with rb-tree node, current window start/length, last allocation start/length, LRU list node, and flags.
- Defines flags for in-use windows, temporary windows, and directory reservations.
- Defines `struct ocfs2_reservation_map` with rb-tree root, disk bitmap pointer, owning superblock, bitmap length, and LRU list.
- Declares initialization, type setting, discard, restart, uninit, reserve-bits, and claimed-bits APIs.

Important behavior:
- `ocfs2_resmap_restart()` discards existing reservations when a new bitmap is supplied.
- `ocfs2_resmap_resv_bits()` may allocate a window if the reservation is empty.
- `ocfs2_resmap_claimed_bits()` must be called when allocation bits are consumed so reservation state can be trimmed consistently.

Risks:
- Reservation objects are caller-owned while the map stores their rb/list links.
- `cstart` passed to `ocfs2_resmap_claimed_bits()` is expected to match the reservation start returned earlier.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/reservations.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/resize.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/resize.c

Purpose: Implements OCFS2 online volume growth by extending the final cluster group or adding a new group descriptor to the global bitmap.

Read coverage: complete file read, 598 lines.

Key responsibilities:
- Extends the last bitmap group when the new space still fits in that group.
- Adds a new bitmap group descriptor and links it into the correct chain.
- Updates the global bitmap inode, chain records, group descriptor free counts, filesystem cluster totals, and backup superblocks.
- Validates new group descriptors and user-provided resize input before journaling metadata changes.

Major logic:
- `ocfs2_calc_new_backup_super()` identifies backup superblock positions that newly fall inside an extended group and marks or clears those bits in the group bitmap.
- `ocfs2_update_last_group_and_inode()` journals updates to the last group descriptor and global bitmap inode, including free-bit totals, backup-super reservations, contiguous-free-bit summary, `i_clusters`, and `i_size`.
- `update_backups()` writes updated superblock contents to backup superblock locations below the new cluster count.
- `ocfs2_update_super_and_backups()` updates the primary superblock last and logs backup-super write failures as nonfatal fsck-repairable conditions.
- `ocfs2_group_extend()` locks the global bitmap inode, validates that the last group can be extended, reads the last group descriptor, journals the group/inode update, and updates superblocks.
- `ocfs2_check_new_group()` validates an on-disk group descriptor against the requested chain, cluster count, and free count.
- `ocfs2_verify_group_and_input()` rejects groups inside the current volume, bad chains, overflow, groups larger than `cl_cpg`, invalid free counts, partially full last groups, and invalid group block numbers.
- `ocfs2_group_add()` reads the provided new group descriptor, verifies it, links it into the chosen chain, updates chain totals and global bitmap inode totals, then updates superblocks.

Concurrency and risks:
- Resize operations lock and cluster-lock the global bitmap inode before modifying bitmap chains.
- Emergency filesystem state returns `-EROFS`.
- Old/small group layouts are rejected and require offline resize.
- Superblock backup update failure is not fatal to the resize but requires `fsck.ocfs2`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/resize.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/resize.h

Purpose: Declares OCFS2 online resize entry points.

Read coverage: complete file read, 16 lines.

Key contents:
- Include guard `OCFS2_RESIZE_H`.
- Declares `ocfs2_group_extend(struct inode *inode, int new_clusters)`.
- Declares `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`.

Role:
- This is the public internal header used by OCFS2 resize callers to extend the last existing group or add a new bitmap group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/resize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/slot_map.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/slot_map.c

Purpose: Implements OCFS2 slot-map management, mapping cluster node numbers to per-mount filesystem slots and keeping the in-memory slot table synchronized with the slot-map system file.

Read coverage: complete file read, 542 lines.

Key structures:
- `struct ocfs2_slot` stores validity and node number for one slot.
- `struct ocfs2_slot_info` tracks old vs extended slot-map format, mapped slot-map inode, buffer heads, slot count, slots per block, and flexible array of slot records.

Major logic:
- Supports both old `__le16` slot maps and extended slot maps with valid bits and 32-bit node numbers.
- `ocfs2_refresh_slot_info()` rereads all mapped slot-map blocks and rebuilds the in-memory table under `osb_lock`.
- `ocfs2_update_disk_slot()` writes the in-memory slot state back to the correct slot-map block.
- `ocfs2_slot_map_physical_size()` verifies that the slot-map system file is large enough for `max_slots`.
- `ocfs2_map_slot_buffers()` maps logical slot-map blocks through the extent map, reads them with validation, and stores buffer heads.
- `ocfs2_init_slot_info()` allocates slot info, opens the slot-map system inode, maps buffers, and installs it on `osb`.
- `ocfs2_find_slot()` refreshes slot info, reuses this node’s existing slot if present, otherwise chooses the preferred empty slot or first empty slot, records it in memory, and writes it to disk.
- `ocfs2_put_slot()` invalidates this node’s slot, writes the update, and frees slot info during dismount.
- `ocfs2_clear_slot()` invalidates an arbitrary slot and persists it.

Concurrency and risks:
- In-memory slot table updates are protected by `osb_lock`.
- Disk writes use buffer-head writes against the slot-map inode cache.
- If slot write fails during mount, the slot is invalidated in memory to avoid overwriting another node’s valid slot during dismount.
- Slot-map block validation rejects suspicious block numbers below the primary superblock block number.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/slot_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/slot_map.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/slot_map.h

Purpose: Declares OCFS2 slot-map lifecycle and lookup APIs.

Read coverage: complete file read, 28 lines.

Key contents:
- Declares `ocfs2_init_slot_info()` and `ocfs2_free_slot_info()`.
- Declares mount/dismount slot APIs: `ocfs2_find_slot()` and `ocfs2_put_slot()`.
- Declares `ocfs2_refresh_slot_info()` for rereading slot state from disk.
- Declares node/slot lookup helpers: `ocfs2_node_num_to_slot()` and `ocfs2_slot_to_node_num_locked()`.
- Declares `ocfs2_clear_slot()`.

Role:
- This header exposes the slot-map services used by OCFS2 mount, recovery, and node-to-slot resolution code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/slot_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stack_o2cb.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/stack_o2cb.c

Purpose: Implements the OCFS2 stack plugin for the classic `o2cb` cluster stack, adapting OCFS2 stackglue operations to o2dlm, o2net, heartbeat, and nodemanager APIs.

Read coverage: complete file read, 439 lines.

Key responsibilities:
- Maps generic OCFS2 DLM lock modes and flags to o2dlm lock modes and flags.
- Maps o2dlm status values to Linux errno values with special unique mappings required by dlmglue.
- Wraps lock, blocking, and unlock AST callbacks so o2dlm can call OCFS2 stack protocol callbacks.
- Provides lock, unlock, status, LVB access, LVB validity, and lock dump operations.
- Verifies cluster readiness before joining a DLM domain.
- Registers and unregisters DLM eviction callbacks to trigger OCFS2 recovery.
- Registers the `o2cb` stack plugin at module load and unregisters it at module unload.

Major logic:
- Compile-time checks assert that OCFS2 DLM mode constants match o2dlm `LKM_*` mode constants.
- `flags_to_o2dlm()` translates OCFS2 `DLM_LKF_*` flags into o2dlm `LKM_*` flags.
- `dlm_status_to_errno()` translates o2dlm statuses; `DLM_NOTQUEUED`, `DLM_CANCELGRANT`, and `DLM_CANCEL` retain special semantics.
- `o2dlm_unlock_ast_wrapper()` suppresses `DLM_CANCELGRANT` because the grant AST will handle the granted lock.
- `o2cb_cluster_check()` confirms this node is configured, heartbeating, and connected via o2net to all heartbeating nodes, waiting up to 60 seconds for maps to stabilize.
- `o2cb_cluster_connect()` runs the cluster check, allocates private state, installs an eviction callback, computes a CRC32 DLM key from the domain name, registers the DLM domain, negotiates protocol version, and records the lockspace.
- `o2cb_cluster_disconnect()` unregisters eviction callbacks, frees private state, and unregisters the DLM domain.
- `o2cb_cluster_this_node()` returns the local nodemanager node number.

Risks:
- Cluster check is explicitly racy but improves diagnostics before `dlm_register_domain()`.
- Status mapping must remain aligned with `dlmapi.h` and dlmglue expectations.
- Eviction callbacks directly invoke OCFS2 recovery handling for the evicted node.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/stack_o2cb.c -->