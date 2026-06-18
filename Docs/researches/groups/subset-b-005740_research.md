# subset-b-005740 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota_global.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/quota_global.c

## Purpose
`quota_global.c` implements OCFS2 operations over the clustered global quota files. It bridges the VFS quota core, the generic qtree quota format, OCFS2 journaling, and OCFS2 cluster locks so user/group quota limits and aggregate usage can be shared safely across mounted nodes.

## Important APIs, types, and functions
The file exports the qtree format adapter `ocfs2_global_ops`, physical quota I/O helpers `ocfs2_validate_quota_block`, `ocfs2_read_quota_phys_block`, `ocfs2_quota_read`, and `ocfs2_quota_write`, global quota locking helpers `ocfs2_lock_global_qf` and `ocfs2_unlock_global_qf`, info operations `ocfs2_global_read_info` and `ocfs2_global_write_info`, the synchronization primitive `__ocfs2_sync_dquot`, deferred drop worker `ocfs2_drop_dquot_refs`, and the VFS `dquot_operations` table `ocfs2_quota_operations`. Central state is `struct ocfs2_mem_dqinfo`, its embedded qtree info, global quota inode pointer, qinfo lock resource, delayed sync work, and cached global quota inode buffer.

## Control Flow
Quota enablement calls `ocfs2_global_read_info`, which opens the global system inode, locks it shared, reads the global info block under the quota-info lock, initializes qtree geometry, and schedules periodic sync work. Reads and writes bypass page cache and translate logical quota offsets through `ocfs2_extent_map_get_blocks`; writes require an active journal transaction and update inode size/version metadata. `ocfs2_acquire_dquot` exclusively locks the global quota file, reads or creates the qtree entry, increments the clustered use count, extends the global file if a new qtree path is needed, then creates the node-local dquot entry. `ocfs2_mark_dquot_dirty` writes local deltas normally, but synchronizes immediately to the global file when administrator-set fields need cluster-wide visibility. `ocfs2_release_dquot` decrements global use count and releases the local slot entry, deferring work if called from the downconvert thread.

## State and Persistence
Persistent state lives in global user/group quota system files: qtree blocks, global quota info, disk dquot records, use counts, limits, usage, and grace times. Runtime state tracks original local usage in `struct ocfs2_dquot`, dirty `DQ_LASTSET` bits, delayed sync cadence, global inode lock nesting count, and the `dquot_drop_list`. Global changes are journaled and guarded by OCFS2 inode, allocation, and qinfo cluster locks.

## Dependencies and Integration Points
The file depends on Linux quota/qtree code, OCFS2 system files, extent maps, inode cluster locks, qinfo DLM locks, journaling, metadata ECC, workqueues, and local quota helpers from `quota_local.c`. It plugs into superblock quota callbacks via `quota_read`, `quota_write`, and `dquot_operations`.

## Risks and Test Signals
High-risk areas are lock ordering between `dqio_sem`, dquot locks, inode cluster locks, `ip_alloc_sem`, and qinfo locks; extending qtree files outside transactions; delayed sync during unmount; downconvert-thread deferral; and preserving administrator-set quota fields while merging usage deltas. Test signals include multi-node quota limit updates, first acquire of a previously nonexistent ID, release of last reference, periodic sync under active I/O, quota disable while sync work is pending, qtree block allocation failure, recovery after node death, and fault injection around journal credit exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota_global.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota_local.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/quota_local.c

## Purpose
`quota_local.c` manages per-slot OCFS2 local quota files. Local files record this node's quota usage deltas and dquot references so ordinary filesystem operations can update quota state cheaply, then synchronize or recover those deltas into the clustered global quota files.

## Important APIs, Types, and Functions
The public entry points are `ocfs2_begin_quota_recovery`, `ocfs2_finish_quota_recovery`, `ocfs2_free_quota_recovery`, `ocfs2_local_write_dquot`, `ocfs2_create_local_dquot`, `ocfs2_local_release_dquot`, and `ocfs2_quota_format`. Internal helpers define the local-file layout (`ol_quota_entries_per_block`, `ol_chunk_blocks`, `ol_quota_chunk_block`, `ol_dqblk_off`), modify quota blocks transactionally (`ocfs2_modify_bh`), validate both local and global headers, load chunk bitmaps, extend the local quota file, and recover dirty chunks from crashed slots.

## Control Flow
Quota activation calls `ocfs2_local_read_info`: it allocates `ocfs2_mem_dqinfo`, reads global info, locks the local quota inode, reads the local header, loads chunk headers into memory, captures recovery data if the local file was not marked clean, and marks the file dirty for active use. Creating a dquot tries to reserve a free bitmap entry, extends the last chunk or creates a new chunk if necessary, records physical block location, writes the local dquot delta entry, then marks the bitmap bit. Local writes update `dqb_spacemod` and `dqb_inodemod` from current usage minus the globally synchronized origins. Release clears the chunk bitmap bit within the caller's transaction. Recovery first snapshots dirty chunk bitmaps for a failed slot, then later locks the local quota file, replays each recorded local delta into the matching global dquot, releases the crashed node's global dquot reference, clears local bits, and marks the recovered file clean.

## State and Persistence
Local quota files persist an info block, per-chunk bitmap headers, and `ocfs2_local_disk_dqblk` delta records. In memory, `ocfs2_mem_dqinfo` owns loaded chunk headers, local info buffers, dirty/clean flags, block and chunk counts, and optional recovery lists. `OLQF_CLEAN` is the key persistence signal for whether local deltas require replay after a crash.

## Dependencies and Integration Points
The file integrates with the Linux quota format layer through `quota_format_ops`, with `quota_global.c` for global reads/writes and dquot release, with OCFS2 system-file lookup for per-slot quota inodes, and with journaling, inode locks, metadata validation, and extent mapping. Recovery is tied into OCFS2 journal replay and slot recovery.

## Risks and Test Signals
Risks include bitmap/header divergence, partial local-file extension, unclean shutdown with stale chunk snapshots, holding or missing `ip_alloc_sem` around quota-file growth, incorrect signedness when replaying deltas, and marking a live local file clean. Test signals include quota enable/disable cycles, exhaustion of local chunk entries, extending local files across chunks, crash recovery of dirty local quota files, concurrent dquot create/release, corrupt header detection, and recovery races where another node already holds the local quota lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.c

## Purpose
`refcounttree.c` implements OCFS2 shared-extent reference counting, copy-on-write, reflink creation, reflink range remapping, and refcounted xattr handling. It maintains on-disk refcount blocks that map physical cluster ranges to reference counts and coordinates those records with inode extent flags.

## Important APIs, Types, and Functions
The main runtime types are `struct ocfs2_refcount_tree`, declared in the header and cached in `osb->osb_rf_lock_tree`, and `struct ocfs2_cow_context`, which carries data/refcount extent trees, allocators, deallocation context, duplication callbacks, and post-refcount hooks. Important exported functions include `ocfs2_lock_refcount_tree`, `ocfs2_unlock_refcount_tree`, `ocfs2_purge_refcount_trees`, `ocfs2_increase_refcount`, `ocfs2_decrease_refcount`, `ocfs2_prepare_refcount_change_for_del`, `ocfs2_refcount_cow`, `ocfs2_refcount_cow_xattr`, `ocfs2_add_refcount_flag`, `ocfs2_remove_refcount_tree`, `ocfs2_try_remove_refcount_tree`, `ocfs2_reflink_ioctl`, `ocfs2_reflink_remap_blocks`, `ocfs2_reflink_inodes_lock`, `ocfs2_reflink_inodes_unlock`, and `ocfs2_reflink_update_dest`.

## Control Flow
Refcount tree lookup uses an in-memory rb-tree plus LRU pointer, reads the root block for generation, initializes a DLM lock resource, and generation-checks after locking so stale trees are removed and recreated. A new tree is allocated by `ocfs2_create_refcount_tree`, which claims one metadata block, initializes an inline root `ocfs2_refcount_block`, sets `OCFS2_HAS_REFCOUNT_FL`, and records `i_refcount_loc`. Refcount updates locate the containing record or hole, then change, insert, split, merge, expand inline roots into b-tree roots, split leaf refcount blocks, and remove empty leaves. COW computes a bounded cluster hunk, locks the refcount tree, reserves metadata/data, allocates replacement clusters only for records with refcount greater than one, duplicates data through page cache or JBD buffers, clears the inode extent's refcount flag, decreases physical refcounts, and runs deferred deallocations. Reflink attaches a refcount tree to the source, creates an orphan target inode, duplicates inline data or extent mappings, increments refcounts, copies xattrs, updates destination metadata, and finally moves the orphan into the target directory. Range remap ensures both inodes share a tree, punches the destination range, marks source extents refcounted if needed, and maps shared extents into the destination.

## State and Persistence
Persistent state includes refcount root/leaf blocks, refcount records, generation numbers, suballocator ownership, inode `i_refcount_loc`, inode dynamic flags, extent `OCFS2_EXT_REFCOUNTED` bits, and shared xattr value trees. Runtime state includes kref-managed tree locks, metadata caches, lock resources, allocator contexts, page-cache state during COW, and cached deallocation queues. Journal transactions bracket every on-disk mutation.

## Dependencies and Integration Points
This file sits at the intersection of OCFS2 extent allocation, suballocation, inode and xattr code, DLM lock resources, metadata caching, journaling, quota charging, page-cache writeback, VFS permissions, security/ACL initialization, and fsnotify. It also enforces superblock refcount feature availability before using shared-extent behavior.

## Risks and Test Signals
Risks are high: refcount record split/merge corruption, low-32-bit b-tree indexing of 64-bit physical cluster positions, stale cached tree generations, insufficient journal credits for worst-case splits, COW interacting with dirty page cache, incorrect deallocation when refcount reaches one or zero, and reflink lock ordering across two inodes. Test signals include inline-root expansion, leaf split and empty-leaf removal, repeated reflink/unlink/COW cycles across nodes, xattr COW and delete, range remap with holes and unwritten extents, two-inode reflink lock ordering, crash recovery after partial COW, ENOSPC during allocator reservation, and fsck validation of refcount blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.h

## Purpose
`refcounttree.h` declares the OCFS2 refcount tree interface used by inode, xattr, truncate, write, and reflink paths. It exposes the in-memory tree lock/cache structure and the operations required to mutate shared extents safely.

## Important APIs, Types, and Functions
`struct ocfs2_refcount_tree` contains rb-tree linkage, root block number, generation, kref lifetime, local rw semaphore, DLM lock resource, removal flag, metadata-cache lock, `ocfs2_caching_info`, I/O mutex, and superblock pointer. `struct ocfs2_post_refcount` lets callers attach extra journal credits and a callback to run inside COW or add-refcount transactions. Declarations cover tree lock/unlock/purge, refcount increase/decrease, COW for inode data and xattrs, duplicate-by-page/JBD helpers, writeback sync, adding refcount flags, removing tree ownership, reflink ioctl/remap helpers, double-inode lock helpers, and destination size update.

## Control Flow
Callers lock a tree with `ocfs2_lock_refcount_tree`, perform record or extent changes through the exported helpers, then release with `ocfs2_unlock_refcount_tree`. File write paths use `ocfs2_refcount_cow` before modifying shared data. Truncate/delete paths prepare credits and decrease physical refcounts. Xattr code uses the xattr-specific COW and delete-need helpers. Reflink and clone operations use the inode lock helpers and remap/update functions to share physical extents.

## State and Persistence
The header itself has no persistent state, but it defines the runtime object that protects persistent refcount blocks. Its API assumes callers already hold the relevant inode locks and pass journal handles, metadata allocators, buffer heads, and deallocation contexts according to the implementation's lock ordering.

## Dependencies and Integration Points
It depends on OCFS2 core types, buffer heads, JBD handles, extent trees, cached deallocation contexts, and inode/xattr structures defined elsewhere. It is included by OCFS2 allocation, file, inode, xattr, and reflink paths that need shared-extent behavior.

## Risks and Test Signals
Interface risks include callers forgetting to hold the refcount tree lock, underestimating `ocfs2_post_refcount.credits`, using page duplication where JBD duplication is required, or mixing inodes that point to different refcount trees. Test signals are compile coverage of all call sites, lockdep for lock/unlock pairing, reflink range tests, xattr COW tests, and ENOSPC paths where prepared credits or metadata reservations are too small.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/refcounttree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/reservations.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/reservations.c

## Purpose
`reservations.c` implements allocation reservation windows for OCFS2 bitmap allocators. Reservations give inodes or temporary callers a preferred contiguous range of free bits in a local allocation bitmap, improving locality and reducing repeated bitmap searches.

## Important APIs, Types, and Functions
The public API includes `ocfs2_dir_resv_allowed`, `ocfs2_resv_init_once`, `ocfs2_resv_set_type`, `ocfs2_resmap_init`, `ocfs2_resv_discard`, `ocfs2_resmap_restart`, `ocfs2_resmap_uninit`, `ocfs2_resmap_resv_bits`, and `ocfs2_resmap_claimed_bits`. Internal helpers manage rb-tree insertion/removal, LRU movement, reservation search, free-bit scanning, cannibalizing older reservations, and optional debug validation. The global `resv_lock` serializes all reservation maps.

## Control Flow
Each reservation map is initialized with an OCFS2 superblock and later restarted with a disk bitmap and bitmap length. When allocation asks for reserved bits, `ocfs2_resmap_resv_bits` creates a window if the reservation is empty, sizing it from `osb_resv_level`, directory reservation level, or the requested temporary length. Search starts near the previous allocation, scans gaps between rb-tree windows for clear disk bits, retries from zero, and finally cannibalizes the oldest LRU reservation if no free gap is found. After allocation succeeds, `ocfs2_resmap_claimed_bits` shrinks or discards the consumed left side of the reservation and records the last allocation as the next search goal.

## State and Persistence
Reservation state is entirely in memory: rb-tree windows, per-reservation start/length, last allocation, flags, and LRU list membership. It references the current disk bitmap but does not persist anything to disk. Restarting a map discards all windows because the bitmap window has changed.

## Dependencies and Integration Points
It depends on Linux rbtrees/lists/bitops and OCFS2 bitmap bit helpers. It integrates with local allocation and suballocation code that owns the actual on-disk bitmap and calls the reservation API before and after claiming bits.

## Risks and Test Signals
Risks include stale `m_disk_bitmap` after local-alloc window movement, overlap in rb-tree windows, cannibalizing a reservation still expected by a caller, off-by-one range handling at bitmap end, global spinlock contention, and disabled reservation levels returning `-ENOSPC` as a control signal. Test signals include sequential file growth locality, temporary reservations, directory reservation policy, map restart while reservations exist, full bitmap behavior, LRU cannibalization, debug reservation validation, and allocation at the last bit of the bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/reservations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/reservations.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/reservations.h

## Purpose
`reservations.h` defines the public reservation-window data structures and APIs used by OCFS2 allocation code to reserve ranges in allocation bitmaps.

## Important APIs, Types, and Functions
The header defines reservation level bounds (`OCFS2_DEFAULT_RESV_LEVEL`, `OCFS2_MAX_RESV_LEVEL`, `OCFS2_MIN_RESV_LEVEL`), `struct ocfs2_alloc_reservation`, flags `OCFS2_RESV_FLAG_INUSE`, `OCFS2_RESV_FLAG_TMP`, and `OCFS2_RESV_FLAG_DIR`, and `struct ocfs2_reservation_map`. The API covers initialization, type assignment, directory-reservation eligibility, discard, map init/restart/uninit, lookup of reservable bits, and notification that bits were claimed.

## Control Flow
Allocators embed or allocate `ocfs2_alloc_reservation`, initialize it once, optionally set temporary or directory type flags, then call `ocfs2_resmap_resv_bits` to receive a candidate start/length. Once the allocator actually claims bits in the disk bitmap, it calls `ocfs2_resmap_claimed_bits` so the reservation can be shortened or moved in LRU order. When the allocation context ends or the bitmap changes, callers discard or restart reservations.

## State and Persistence
The structures are runtime-only. A reservation map points at a disk bitmap buffer and records the bitmap length, but the reservation windows themselves are not written to disk. `r_last_start` and `r_last_len` guide future placement after successful allocations.

## Dependencies and Integration Points
The header depends on Linux rbtrees and OCFS2 superblock definitions. It is consumed by allocator code that owns local allocation windows and by inode allocation contexts that want locality hints.

## Risks and Test Signals
Risks include misuse of flags outside `OCFS2_RESV_TYPES`, calling claimed-bits with a start different from the reservation start, failing to discard reservations when allocator state is destroyed, and stale disk bitmap pointers after local alloc slides. Test signals are allocation tests with reservations disabled/enabled, temporary reservation one-shot behavior, directory reservations, map restart coverage, and lockdep/KASAN around reservation lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/reservations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/resize.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/resize.c

## Purpose
`resize.c` implements OCFS2 online volume growth for the global bitmap. It can extend the final existing cluster group or add a new group descriptor, updating bitmap chains, group descriptors, the global bitmap inode, the primary superblock, and backup superblocks.

## Important APIs, Types, and Functions
The exported entry points are `ocfs2_group_extend` and `ocfs2_group_add`. Important helpers include `ocfs2_calc_new_backup_super`, `ocfs2_update_last_group_and_inode`, `update_backups`, `ocfs2_update_super_and_backups`, `ocfs2_check_new_group`, and `ocfs2_verify_group_and_input`. The code manipulates `struct ocfs2_dinode`, `struct ocfs2_chain_list`, `struct ocfs2_chain_rec`, `struct ocfs2_group_desc`, and userspace-provided `struct ocfs2_new_group_input`.

## Control Flow
`ocfs2_group_extend` validates the request, locks the global bitmap system inode, verifies the bitmap geometry supports online resize, reads the last group descriptor, ensures the new clusters fit in that group, starts a transaction, grows the group bit count and free count, marks any newly covered backup superblock bits allocated, updates chain totals and bitmap inode size/cluster count, and finally writes the superblock/backups. `ocfs2_group_add` reads a prepared group descriptor from the newly available disk region, validates the descriptor and input against chain order and size limits, links the new group into the selected chain, updates chain and bitmap totals, grows inode size, and writes superblock backups.

## State and Persistence
Persistent mutations include global bitmap group descriptors, chain records, bitmap inode `i_clusters`, bitmap totals/used/free counts, primary superblock cluster count, and backup superblock copies. The in-memory bitmap inode cluster count and VFS size are updated under `ip_lock`. Resize work is journaled for bitmap metadata, while superblock backup writes are attempted after metadata changes and treated as repairable by fsck if they fail.

## Dependencies and Integration Points
The file depends on global bitmap system-file lookup, inode cluster locks, OCFS2 journaling, group descriptor validation, suballocator helpers, backup-superblock layout, and emergency read-only state checks. It is invoked by OCFS2 resize ioctl/control paths that pass either a group extension count or a validated new-group input.

## Risks and Test Signals
Risks include accepting malformed group descriptors, overflow in cluster totals, extending a non-full last group through the wrong path, backup superblock bitmap accounting mistakes, partial superblock backup updates, and chain linking rollback after journal access failure. Test signals include online grow by final-group extension, adding groups to existing and next-free chains, backup-superblock feature enabled/disabled, old-small-disk rejection, invalid group input fuzzing, emergency read-only behavior, and fsck after injected backup write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/resize.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/resize.h

## Purpose
`resize.h` declares the OCFS2 online resize entry points for extending the current last group or adding a new bitmap group.

## Important APIs, Types, and Functions
The header exposes `ocfs2_group_extend(struct inode *inode, int new_clusters)` and `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`. `ocfs2_new_group_input` is defined in OCFS2 disk-format headers and carries the prepared group block, target chain, total clusters, and free clusters.

## Control Flow
Resize callers include this header and choose `ocfs2_group_extend` when the current final group can absorb additional clusters, or `ocfs2_group_add` when a fully prepared new group descriptor must be linked into the global bitmap chain.

## State and Persistence
The header has no state. The declared functions persist changes to global bitmap metadata and superblock cluster counts through the implementation in `resize.c`.

## Dependencies and Integration Points
It depends on declarations of `struct inode` and `struct ocfs2_new_group_input` from surrounding OCFS2/Linux headers. It is part of the filesystem control-plane interface used by resize ioctl code.

## Risks and Test Signals
Risks are primarily interface misuse: passing a negative extension, calling group-add before userspace has initialized the on-disk group descriptor, or using extend when the last group is already full. Test signals are compile coverage for resize callers and online resize tests that exercise both declared paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/resize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.c

## Purpose
`slot_map.c` manages the OCFS2 slot map, which assigns mounted cluster nodes to filesystem slots. Slots select per-node system files such as journals and local quota files, so the slot map is a core mount/unmount and recovery coordination structure.

## Important APIs, Types, and Functions
The file defines private `struct ocfs2_slot` and flexible `struct ocfs2_slot_info`. Public functions are `ocfs2_init_slot_info`, `ocfs2_free_slot_info`, `ocfs2_find_slot`, `ocfs2_put_slot`, `ocfs2_refresh_slot_info`, `ocfs2_node_num_to_slot`, `ocfs2_slot_to_node_num_locked`, and `ocfs2_clear_slot`. Internal helpers update old and extended on-disk formats, validate slot-map blocks, map slot-map buffers through the extent map, and write slot changes back to disk.

## Control Flow
Mount initialization allocates slot info sized to `max_slots`, opens the slot-map system inode, computes the required physical size for old or extended format, maps and reads each backing block, then stores the structure on the superblock. `ocfs2_find_slot` refreshes in-memory state from disk, reuses an existing slot for the node if present or chooses the preferred/first free slot, updates `osb->slot_num`, and writes the corresponding disk block. `ocfs2_put_slot` refreshes the map, invalidates the node's slot on disk, resets `slot_num`, and frees slot info. `ocfs2_refresh_slot_info` rereads all mapped blocks, relying on super-lock callers to have serialized disk updates.

## State and Persistence
Persistent state is the slot-map system file, either an old array of 16-bit node numbers or an extended array with valid bits and 32-bit node numbers. Runtime state is `osb->slot_info`, cached buffer heads, `si_slots[]`, `si_blocks`, format flag, and `osb->slot_num`. Updates are protected by `osb_lock` locally and written through `ocfs2_write_block`.

## Dependencies and Integration Points
It depends on system-file lookup, extent mapping, buffer-head I/O, heartbeat/mount coordination, superblock locking, and OCFS2 disk format helpers. Slot numbers feed journal selection, local quota file selection, recovery, and node-to-slot lookups elsewhere in OCFS2.

## Risks and Test Signals
Risks include stale slot data if refresh is skipped, lost slot invalidation on write failure, old-format truncation of large node numbers, insufficient slot-map file size, and mount races when a node finds its previous slot still allocated. Test signals include mount/unmount across multiple nodes, preferred slot reuse, no-free-slot behavior, extended slot-map files, slot clear during recovery, write failure rollback of `osb->slot_num`, and validation of bad slot-map block numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.h

## Purpose
`slot_map.h` declares the OCFS2 slot-map lifecycle and lookup API used by mount, unmount, recovery, and node coordination code.

## Important APIs, Types, and Functions
The header declares initialization and teardown (`ocfs2_init_slot_info`, `ocfs2_free_slot_info`), slot acquisition/release (`ocfs2_find_slot`, `ocfs2_put_slot`), refresh (`ocfs2_refresh_slot_info`), node/slot translation (`ocfs2_node_num_to_slot`, `ocfs2_slot_to_node_num_locked`), and explicit clearing (`ocfs2_clear_slot`).

## Control Flow
Mount code initializes slot info, refreshes or finds a slot, then other subsystems query node-to-slot mappings. Unmount calls `ocfs2_put_slot` to invalidate the disk slot and free cached slot state. Recovery paths can refresh or clear slot records when a node leaves.

## State and Persistence
The header owns no state. The implementation persists slot ownership in the slot-map system file and stores the active slot in `struct ocfs2_super`.

## Dependencies and Integration Points
It depends on `struct ocfs2_super` and is included by OCFS2 superblock, heartbeat, recovery, quota, and journal code that needs slot identity or mapping.

## Risks and Test Signals
Risks are API misuse around locking: `ocfs2_slot_to_node_num_locked` requires `osb_lock`, while lookup helpers manage locking internally. Test signals include lockdep on lookup paths, mount/unmount lifecycle tests, and recovery tests clearing slots for departed nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stack_o2cb.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/stack_o2cb.c

## Purpose
`stack_o2cb.c` implements the OCFS2 stack plugin for the classic in-kernel O2CB cluster stack. It adapts OCFS2 stackglue operations to o2dlm locks, o2net connectivity checks, heartbeat node maps, and o2dlm eviction notifications.

## Important APIs, Types, and Functions
The file defines private `struct o2dlm_private`, plugin instance `o2cb_stack`, and operation table `o2cb_stack_ops`. Key functions map lock modes and flags (`mode_to_o2dlm`, `flags_to_o2dlm`), translate `enum dlm_status` through `status_map`, wrap lock/blocking/unlock AST callbacks, implement lock/unlock/status/LVB helpers, check cluster readiness in `o2cb_cluster_check`, connect/disconnect domains, handle evictions, and report this node's number.

## Control Flow
Module init registers the `o2cb` stack plugin with stackglue. On mount, `o2cb_cluster_connect` verifies that the local node is configured, heartbeat is active, and o2net has connected to all heartbeating nodes, waiting up to sixty seconds for maps to stabilize. It allocates private state, registers an eviction callback, computes a DLM key from the domain name, joins/registers the o2dlm domain, negotiates protocol version, stores the lockspace, and registers eviction handling. Lock operations translate generic OCFS2 DLM flags/modes and call `dlmlock`/`dlmunlock`; AST wrappers route callbacks back to the connection protocol. Disconnect unregisters eviction callbacks, leaves the DLM domain, and frees private state.

## State and Persistence
State is runtime-only: the plugin registration, per-connection private eviction callback, o2dlm lockspace pointer, negotiated protocol version, and lock status blocks. Cluster membership comes from heartbeat and network maps, not from this file. No filesystem metadata is persisted here.

## Dependencies and Integration Points
It depends on O2CB node manager, heartbeat, TCP networking, o2dlm APIs, crc32, module infrastructure, and OCFS2 stackglue. Eviction callbacks call OCFS2 recovery handlers, so this plugin is the bridge from cluster node death to filesystem recovery.

## Risks and Test Signals
Risks include incomplete status-to-errno mapping, AST ordering around cancel-after-grant, racing heartbeat/network maps during connect, leaking private state on failed domain registration, incorrect DLM key/name agreement across nodes, and eviction callbacks during disconnect. Test signals include mount with unconfigured node, heartbeat without o2net connectivity, multi-node lock mode/flag conversions, trylock/cancel/unlock AST behavior, LVB access, protocol negotiation mismatch, node eviction triggering recovery, and module unload after failed or successful connects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stack_o2cb.c -->
