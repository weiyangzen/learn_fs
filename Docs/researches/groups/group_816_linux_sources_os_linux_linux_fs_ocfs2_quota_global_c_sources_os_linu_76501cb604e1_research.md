# Group Research: group_816_linux_sources_os_linux_linux_fs_ocfs2_quota_global_c_sources_os_linu_76501cb604e1

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota_global.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/quota_global.c

`quota_global.c` implements OCFS2 operations over the cluster-wide global quota files. It bridges Linux generic quota callbacks with OCFS2’s qtree format, cluster inode locks, journaling, and per-node local quota files.

Main responsibilities:
- Defines qtree format operations for global dquots:
  - `ocfs2_global_disk2memdqb()` imports global quota records while preserving admin-set in-memory fields.
  - `ocfs2_global_mem2diskdqb()` serializes quota limits, usage, grace times, and OCFS2 use counts.
  - `ocfs2_global_is_id()` validates qtree entries against a dquot id.
- Validates and reads quota metadata blocks through `ocfs2_validate_quota_block()` and `ocfs2_read_quota_phys_block()`, including ECC validation.
- Implements direct quota file I/O through `ocfs2_quota_read()` and `ocfs2_quota_write()`, deliberately bypassing page cache because quota paths already rely on quota/cluster locks.
- Provides `ocfs2_lock_global_qf()` / `ocfs2_unlock_global_qf()` to lock the global quota inode, keep a shared global-info buffer head, and take `ip_alloc_sem` in read or write mode.
- Reads and writes global quota info headers with `ocfs2_global_read_info()`, `__ocfs2_global_write_info()`, and `ocfs2_global_write_info()`.
- Synchronizes local dquot deltas into the global qtree in `__ocfs2_sync_dquot()`, preserving grace-time semantics and clearing `DQ_LASTSET` fields after successful reconciliation.
- Periodically syncs active dquots using delayed work:
  - `qsync_work_fn()` scans active dquots without deadlocking unmount by using `down_read_trylock(&sb->s_umount)`.
  - `ocfs2_sync_dquot_helper()` locks the global quota file, starts a journal transaction, syncs the global dquot, and writes the local dquot.
- Implements generic `dquot_operations`:
  - `ocfs2_acquire_dquot()` reads or creates a global qtree entry, increments the OCFS2 use count, extends the global quota file before transaction start when needed, then creates a local quota entry.
  - `ocfs2_release_dquot()` decrements the global use count, releases local quota state, and defers work when called from the downconvert thread to avoid cluster-lock deadlocks.
  - `ocfs2_mark_dquot_dirty()` writes local changes or immediately syncs admin-set fields to the global file when safe.
  - `ocfs2_get_next_id()` enumerates ids from the global qtree.
  - `ocfs2_alloc_dquot()` / `ocfs2_destroy_dquot()` use the OCFS2 dquot slab cache.

Key invariants:
- Global quota file modification requires the global quota inode cluster lock, inode `i_rwsem`, `ip_alloc_sem`, and quota info lock.
- Quota writes require an existing journal transaction; missing transactions are treated as I/O errors.
- Allocation for new global quota file space is done before starting the transaction to preserve allocator lock ordering.
- Local and global quota structures are kept consistent by syncing global qtree state and then writing the node-local dquot entry.
- Last-reference release can be delayed from the downconvert thread because taking quota locks there could block cluster lock recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota_global.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota_local.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/quota_local.c

`quota_local.c` implements the per-slot local quota files used by OCFS2 nodes to accumulate quota deltas before syncing them to the global quota files. It owns local quota file layout, chunk bitmaps, local dquot allocation, and crash recovery.

Main responsibilities:
- Defines local quota layout helpers:
  - entries per block, blocks per chunk, chunk header block, dquot block, and byte offsets.
  - chunks contain a header bitmap plus one or more blocks of `ocfs2_local_disk_dqblk` entries.
- Provides `ocfs2_modify_bh()` as a small journaling wrapper for modifying local quota buffers.
- Reads quota blocks with `ocfs2_read_quota_block()`, validating file bounds and ECC through the shared quota validator.
- Validates quota file format in `ocfs2_local_check_quota_file()` for both local and global quota headers, magic values, and versions.
- Loads and releases in-memory chunk bitmap state with `ocfs2_load_local_quota_bitmaps()` and `ocfs2_release_local_quota_bitmaps()`.
- Implements quota crash recovery:
  - `ocfs2_begin_quota_recovery()` scans another slot’s local quota files after journal replay, recording non-empty chunk bitmaps in memory.
  - `ocfs2_recover_local_quota_file()` walks recorded local entries, gets the corresponding global dquot, applies local space/inode deltas, releases the dead node’s global dquot use count, and frees the local entry bitmap bit.
  - `ocfs2_finish_quota_recovery()` locks each recovered local quota file, replays needed deltas, and marks the file clean if it belongs to another slot.
- Implements local quota format operations:
  - `ocfs2_local_read_info()` allocates `ocfs2_mem_dqinfo`, reads global info first, locks the local quota inode, loads chunk bitmaps, records unclean-file recovery work, and marks the local file in-use by clearing `OLQF_CLEAN`.
  - `ocfs2_local_free_info()` checks all entries are free, releases lock resources, marks the local file clean when safe, and tears down private info.
  - `ocfs2_local_write_info()` persists local info fields.
- Writes local dquot deltas through `ocfs2_local_write_dquot()`, storing only differences from original global usage.
- Allocates and frees local dquot entries:
  - `ocfs2_find_free_entry()` searches chunk bitmaps.
  - `ocfs2_local_quota_add_chunk()` grows the local quota file by a new chunk header and data block.
  - `ocfs2_extend_local_quota_file()` adds a data block to the final chunk when possible.
  - `ocfs2_create_local_dquot()` reserves a free local entry, maps its physical block, initializes it, and sets the chunk bitmap bit.
  - `ocfs2_local_release_dquot()` clears the entry bit during global dquot release.

Key invariants:
- Local quota files are protected by their inode cluster lock and by `ip_alloc_sem` during entry allocation/growth.
- `OLQF_CLEAN` is cleared while a node is actively using a local quota file; unclean files trigger recovery.
- Recovery records bitmaps before replay, so local entries can be folded into global quota state even after node failure.
- Local entries store deltas, not full authoritative quota usage; global files remain the cluster-wide source of truth.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota_local.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/refcounttree.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/refcounttree.c

`refcounttree.c` implements OCFS2’s shared-extent reference count trees, copy-on-write, reflink creation, xattr CoW, and range remap helpers. It is the core of OCFS2’s reflink/refcount feature.

Main responsibilities:
- Maintains in-memory refcount tree objects:
  - `struct ocfs2_refcount_tree` instances are cached in `osb_rf_lock_tree`, keyed by refcount root block.
  - Each tree has kref lifetime management, an OCFS2 lock resource, an rw semaphore, metadata cache operations, and an LRU shortcut.
  - Generation checks in `ocfs2_lock_refcount_tree()` detect refcount block reuse and recreate stale in-memory lock objects safely.
- Validates and reads refcount blocks with signature, block number, fs generation, and ECC checks.
- Creates, attaches, and removes refcount trees:
  - `ocfs2_create_refcount_tree()` allocates a refcount root block and marks the inode `OCFS2_HAS_REFCOUNT_FL`.
  - `ocfs2_set_refcount_tree()` attaches another inode to an existing tree and increments root `rf_count`.
  - `ocfs2_remove_refcount_tree()` decrements `rf_count`, clears inode flags, and frees the root block when the last owner is gone.
  - `ocfs2_try_remove_refcount_tree()` removes empty trees only when data and externally stored xattrs are gone.
- Manages refcount records:
  - `ocfs2_get_refcount_rec()` finds a real or fake zero-refcount record covering a physical cluster range.
  - insert, split, merge, increase, and decrease paths keep records sorted, coalesce adjacent records with equal counts, and remove zero-count records.
  - Inline refcount roots expand into a refcount btree when record capacity is exhausted.
  - Leaf splitting sorts by low 32-bit cpos to find a btree split key, then restores full 64-bit ordering.
  - Empty leaf blocks are removed from the refcount btree and queued for deferred deallocation.
- Calculates metadata and journal credit needs for refcount changes, including worst-case record splitting and refcount tree expansion.
- Implements CoW:
  - `ocfs2_refcount_cal_cow_clusters()` chooses a CoW range, preferring boundaries up to `MAX_CONTIG_BYTES` for better I/O layout.
  - `ocfs2_lock_refcount_allocators()` reserves metadata and optional replacement data clusters.
  - `ocfs2_make_clusters_writable()` handles refcount 1 by clearing the refcount flag, and refcount >1 by allocating new clusters, copying data, replacing extent mappings, and decrementing old refcounts.
  - Data copying can use page-cache/folio mapping (`ocfs2_duplicate_clusters_by_page()`) or journaled buffer copying (`ocfs2_duplicate_clusters_by_jbd()`).
  - `ocfs2_refcount_cow()` loops over file extents and CoWs any refcounted range before write.
- Supports xattr refcounting:
  - `ocfs2_refcounted_xattr_delete_need()` estimates resources needed to delete refcounted xattr value extents.
  - `ocfs2_refcount_cow_xattr()` performs CoW on xattr value extent trees and supports post-refcount callbacks.
  - `ocfs2_attach_refcount_tree()` also attaches xattrs to the tree when a file becomes refcounted.
- Implements reflink creation:
  - `ocfs2_reflink_ioctl()` resolves source and target paths and dispatches to `ocfs2_vfs_reflink()`.
  - `ocfs2_reflink()` creates the target as an orphan first, reflinks data/xattrs, initializes security/ACL when not preserving attributes, then moves the orphan into the target directory.
  - `ocfs2_attach_refcount_tree()` ensures the source has a refcount tree and marks all existing extents refcounted.
  - `ocfs2_create_reflink_node()` attaches the target to the source tree, copies inline data or duplicates extent mappings, and increments refcounts.
  - `ocfs2_complete_reflink()` copies source attributes, size, dynamic features, and optionally ownership/mode/mtime.
- Implements remap helpers:
  - `ocfs2_reflink_remap_blocks()` prepares shared refcount-tree ownership between source and destination, converts destination inline data to extents when needed, and remaps a range.
  - `ocfs2_reflink_remap_extent()` punches destination ranges, marks source extents refcounted if necessary, inserts destination shared extents, and returns partial progress.
  - `ocfs2_reflink_update_dest()` grows destination size and updates timestamps after remap.
  - `ocfs2_reflink_inodes_lock()` / `ocfs2_reflink_inodes_unlock()` lock two inodes in stable order using VFS locks, OCFS2 rw locks, and inode cluster locks.

Key invariants:
- Refcount tree mutation requires the refcount cluster lock and tree semaphore.
- Refcount records describe physical clusters, while inode extent trees describe logical file clusters; the code carefully translates between them.
- Data extents are marked `OCFS2_EXT_REFCOUNTED` only after corresponding refcount records exist or are created in the same transaction.
- CoW must update data extents and decrease old refcounts atomically under journaling.
- Distinct refcount trees are not merged; range remap rejects source/destination pairs with different existing trees.
- Extent caches are truncated after refcount/CoW changes because cached physical mappings may be stale.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/refcounttree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/refcounttree.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/refcounttree.h

`refcounttree.h` declares OCFS2’s refcount tree data structure and public APIs for shared extents, CoW, reflink, and refcounted xattr handling.

Main contents:
- Defines `struct ocfs2_refcount_tree`, which combines:
  - rbtree membership keyed by root block number.
  - root block number and generation.
  - kref lifetime management.
  - rw semaphore and OCFS2 lock resource for cluster-visible serialization.
  - metadata caching fields: spinlock, `ocfs2_caching_info`, I/O mutex, and superblock pointer.
  - `rf_removed` to mark stale trees removed from the global cache.
- Declares tree lifecycle and locking:
  - `ocfs2_purge_refcount_trees()`
  - `ocfs2_lock_refcount_tree()`
  - `ocfs2_unlock_refcount_tree()`
- Declares refcount update and CoW APIs:
  - `ocfs2_increase_refcount()`
  - `ocfs2_decrease_refcount()`
  - `ocfs2_prepare_refcount_change_for_del()`
  - `ocfs2_refcount_cow()`
  - `ocfs2_add_refcount_flag()`
  - `ocfs2_remove_refcount_tree()`
  - `ocfs2_try_remove_refcount_tree()`
- Defines `struct ocfs2_post_refcount`, a callback hook allowing callers to perform extra journaled work inside refcount transactions.
- Declares xattr-specific refcount helpers:
  - `ocfs2_refcounted_xattr_delete_need()`
  - `ocfs2_refcount_cow_xattr()`
- Declares cluster duplication and writeback helpers:
  - `ocfs2_duplicate_clusters_by_page()`
  - `ocfs2_duplicate_clusters_by_jbd()`
  - `ocfs2_cow_sync_writeback()`
- Declares reflink interfaces:
  - ioctl path creation through `ocfs2_reflink_ioctl()`.
  - range remap through `ocfs2_reflink_remap_blocks()`.
  - paired inode locking/unlocking.
  - destination size update.

Key invariants:
- The header exposes refcount operations to allocation, xattr, ioctl, and file remap code while keeping the record-splitting implementation private to `refcounttree.c`.
- Callers that need extra journaled side effects use `ocfs2_post_refcount` so those changes share the same transaction as refcount updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/refcounttree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/reservations.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/reservations.c

`reservations.c` implements OCFS2 allocation reservation windows. Reservations track free bitmap regions per allocation context to improve locality and reduce fragmentation for local allocation and directory growth.

Main responsibilities:
- Maintains reservations in an rbtree ordered by window start, with an LRU list for fallback stealing.
- Uses a single static `resv_lock` spinlock to serialize all reservation map updates.
- Computes reservation window sizes from mount tunables:
  - regular reservations use `osb_resv_level`.
  - directory reservations use `osb_dir_resv_level`.
  - `ocfs2_dir_resv_allowed()` reports whether directory reservations are enabled.
- Initializes and tears down state:
  - `ocfs2_resv_init_once()` initializes a reservation object.
  - `ocfs2_resv_set_type()` marks temporary or directory reservations.
  - `ocfs2_resmap_init()` initializes a reservation map.
  - `ocfs2_resmap_restart()` clears existing reservations and binds the map to a new disk bitmap and length.
  - `ocfs2_resmap_uninit()` is currently a symmetry no-op.
- Discards reservations:
  - `ocfs2_resv_discard()` clears length/start/last-allocation tracking and removes the reservation from the rbtree and LRU.
  - `ocfs2_resmap_clear_all_resv()` discards every reservation during restart.
- Inserts reservations with overlap checks in `ocfs2_resv_insert()`.
- Finds free reservation windows:
  - `ocfs2_find_resv_lhs()` locates the reservation containing or immediately before a goal.
  - `ocfs2_resmap_find_free_bits()` scans a bitmap gap for the best contiguous free run up to the wanted length.
  - `__ocfs2_resv_find_window()` searches gaps around existing reservations.
  - `ocfs2_resv_find_window()` retries from the previous allocation goal and then from the beginning.
  - `ocfs2_cannibalize_resv()` steals all or part of the oldest LRU reservation when no fresh gap can satisfy the request.
- Exposes allocation-facing APIs:
  - `ocfs2_resmap_resv_bits()` returns a valid reservation window, creating one if the reservation is empty.
  - `ocfs2_resmap_claimed_bits()` records that a caller consumed bits from the front of the reservation and adjusts or discards the window.

Debug behavior:
- Under debugfs builds, `OCFS2_CHECK_RESERVATIONS` validates that rbtree windows are ordered, non-empty, inside bitmap bounds, non-overlapping, and cover only free disk bitmap bits.
- On validation failure, it dumps both rbtree and LRU state before `BUG()`.

Key invariants:
- Reservation windows never overlap.
- A claimed allocation must start at the reservation start.
- Temporary reservations avoid over-allocation by limiting wanted size to the current request.
- Reservation maps can be disabled globally by reservation level zero, in which case callers receive `-ENOSPC` and fall back to normal allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/reservations.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/reservations.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/reservations.h

`reservations.h` declares the data structures and APIs for OCFS2 allocation reservation windows.

Main contents:
- Defines reservation level bounds:
  - default `OCFS2_DEFAULT_RESV_LEVEL`
  - max `OCFS2_MAX_RESV_LEVEL`
  - min `OCFS2_MIN_RESV_LEVEL`
- Defines `struct ocfs2_alloc_reservation`:
  - rbtree node for ordered reservation map membership.
  - current window start and length.
  - last allocation start and length used as the next search goal.
  - LRU list node.
  - flags.
- Defines reservation flags:
  - `OCFS2_RESV_FLAG_INUSE`: reservation is linked into the rbtree.
  - `OCFS2_RESV_FLAG_TMP`: temporary reservation discarded after use.
  - `OCFS2_RESV_FLAG_DIR`: directory-specific reservation sizing.
- Defines `struct ocfs2_reservation_map`:
  - rbtree of reservations.
  - disk bitmap pointer used to verify free bits.
  - owning `ocfs2_super`.
  - bitmap length.
  - LRU list of reservation objects.
- Declares setup and type APIs:
  - `ocfs2_resv_init_once()`
  - `ocfs2_resv_set_type()`
  - `ocfs2_dir_resv_allowed()`
- Declares map lifecycle APIs:
  - `ocfs2_resmap_init()`
  - `ocfs2_resmap_restart()`
  - `ocfs2_resmap_uninit()`
- Declares allocation-facing APIs:
  - `ocfs2_resmap_resv_bits()` to obtain still-valid reservation bits or create a new window.
  - `ocfs2_resmap_claimed_bits()` to notify the reservation map that clusters were used.
  - `ocfs2_resv_discard()` to truncate and unlink a reservation.

Key invariants:
- `ocfs2_resmap_claimed_bits()` must be called whenever reserved bits are consumed so the map remains accurate.
- `ocfs2_resmap_restart()` invalidates existing reservations when the backing bitmap changes, such as during local allocation window slides.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/reservations.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/resize.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/resize.c

`resize.c` implements online OCFS2 volume resize support for extending the global bitmap, either by growing the last existing group or by adding a new group descriptor.

Main responsibilities:
- Handles backup superblock accounting:
  - `ocfs2_calc_new_backup_super()` finds backup superblock locations newly covered by the last group extension and sets or clears their bits in the group bitmap.
  - `update_backups()` writes updated superblock contents to each existing backup location.
  - `ocfs2_update_super_and_backups()` updates the primary superblock cluster count and best-effort backup superblocks; backup update failure is reported as non-fatal with an fsck recommendation.
- Extends the last global bitmap group:
  - `ocfs2_group_extend()` rejects emergency-readonly state, negative sizes, old/small bitmap formats requiring offline resize, and extensions beyond the current group’s capacity.
  - It locks the global bitmap inode, validates the dinode, reads the last group descriptor, starts a journal transaction, and calls `ocfs2_update_last_group_and_inode()`.
  - `ocfs2_update_last_group_and_inode()` increases group bit counts, free counts, contiguous-free tracking, chain totals, bitmap inode clusters/size, and accounts backup superblock bits as used.
  - It rolls back group descriptor fields if inode update journaling fails.
- Adds a new global bitmap group:
  - `ocfs2_group_add()` reads the new group descriptor from disk, validates it, links it into the requested chain, updates chain totals/free counts, bitmap totals/used counts, bitmap inode clusters/size, and superblocks.
  - `ocfs2_verify_group_and_input()` checks that the group is outside the current volume, in a valid chain, does not overflow cluster totals, is not larger than clusters-per-group, does not follow a partial last group, and maps to the expected cluster group block.
  - `ocfs2_check_new_group()` validates the group descriptor itself and compares chain, bit count, and free count against userspace input.

Key invariants:
- Resize operations are refused in OCFS2 emergency state.
- The global bitmap inode is locked with VFS inode mutex and OCFS2 inode cluster lock before modification.
- Old bitmap formats with smaller cluster-per-group layouts require offline resize.
- Adding a group is allowed only when the previous last group is full; otherwise callers must use group extend first.
- Superblock and backup updates happen after bitmap metadata updates; backup write failure is not treated as fatal to the resize transaction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/resize.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/resize.h

`resize.h` is the public header for OCFS2 online resize operations.

Main contents:
- Declares `ocfs2_group_extend(struct inode *inode, int new_clusters)`, which extends the filesystem into unused space at the end of the last existing global bitmap group.
- Declares `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`, which adds a new group descriptor to the global bitmap.

Key invariants:
- The header intentionally exposes only the two resize entry points; validation, backup superblock handling, and bitmap chain updates remain private to `resize.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/resize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/slot_map.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/slot_map.c

`slot_map.c` implements OCFS2 slot-map management. Slots associate mounted cluster nodes with per-slot resources such as journals and local quota/local allocation files.

Main responsibilities:
- Defines in-memory slot state:
  - `struct ocfs2_slot` records whether a slot is valid and which node number owns it.
  - `struct ocfs2_slot_info` stores slot-map format, backing inode, mapped buffer heads, slot count, and in-memory slot array.
- Supports old and extended on-disk formats:
  - old format stores `__le16` node numbers, using `OCFS2_INVALID_SLOT` for empty slots.
  - extended format stores explicit valid bits and 32-bit node numbers.
- Refreshes slot state:
  - `ocfs2_refresh_slot_info()` rereads all mapped slot-map blocks, validates them, and updates the in-memory slot array under `osb_lock`.
  - `ocfs2_update_slot_info_old()` and `ocfs2_update_slot_info_extended()` decode on-disk formats.
- Writes slot changes:
  - `ocfs2_update_disk_slot_old()` rewrites all old-format slots into the first block.
  - `ocfs2_update_disk_slot_extended()` updates the one extended-format entry containing the requested slot.
  - `ocfs2_update_disk_slot()` serializes the in-memory to disk copy under `osb_lock`, then writes the affected block.
- Initializes mapped slot buffers:
  - `ocfs2_slot_map_physical_size()` ensures the slot-map file is large enough for `max_slots`.
  - `ocfs2_map_slot_buffers()` maps logical slot-map blocks to physical blocks and reads them uncached.
  - `ocfs2_init_slot_info()` allocates flexible slot info, gets the slot-map system inode, maps buffers, and installs it in `osb`.
- Exposes lookup and slot lifecycle:
  - `ocfs2_node_num_to_slot()` maps a node number to its slot.
  - `ocfs2_slot_to_node_num_locked()` maps a slot to node number while caller holds `osb_lock`.
  - `ocfs2_find_slot()` refreshes slot info, reuses this node’s existing slot if present, otherwise chooses the preferred or first empty slot, writes it to disk, and sets `osb->slot_num`.
  - `ocfs2_clear_slot()` invalidates a specified slot and writes it.
  - `ocfs2_put_slot()` clears the mounted node’s slot, writes it, and frees slot info.
  - `ocfs2_free_slot_info()` releases buffers and the slot-map inode.

Key invariants:
- In-memory slot array mutation is protected by `osb_lock`.
- Slot-map file size is validated before mapping buffer heads.
- A failed disk write during slot acquisition invalidates the local in-memory slot to avoid later dismount overwriting a slot another node may have acquired.
- `ocfs2_put_slot()` frees the whole slot-info structure after clearing the local node’s slot.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/slot_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/slot_map.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/slot_map.h

`slot_map.h` declares the OCFS2 slot-map API used by mount, dismount, recovery, and per-slot resource code.

Main contents:
- Declares initialization and cleanup:
  - `ocfs2_init_slot_info()`
  - `ocfs2_free_slot_info()`
- Declares mount/dismount slot lifecycle:
  - `ocfs2_find_slot()` to acquire a slot for the local node.
  - `ocfs2_put_slot()` to release the local node’s slot and free slot information.
- Declares refresh and lookup helpers:
  - `ocfs2_refresh_slot_info()`
  - `ocfs2_node_num_to_slot()`
  - `ocfs2_slot_to_node_num_locked()`
- Declares `ocfs2_clear_slot()` for explicit slot invalidation.

Key invariants:
- `ocfs2_slot_to_node_num_locked()` requires caller-side locking, as indicated by its name and implementation.
- Format-specific slot-map details are private to `slot_map.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/slot_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stack_o2cb.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/stack_o2cb.c

`stack_o2cb.c` implements the OCFS2 stack plugin for the classic in-kernel o2cb cluster stack. It adapts OCFS2 stackglue operations to o2dlm, o2net, heartbeat, and nodemanager APIs.

Main responsibilities:
- Verifies at compile time that stackglue DLM lock mode constants match o2dlm `LKM_*` constants.
- Maps generic DLM lock flags to o2dlm flags in `flags_to_o2dlm()`.
- Maps o2dlm status codes to Linux errno values in `status_map` / `dlm_status_to_errno()`, preserving special meanings expected by OCFS2 dlmglue:
  - success as `0`
  - trylock failure as `-EAGAIN`
  - cancel-after-grant as `-EBUSY`
  - successful cancel as `-DLM_ECANCEL`
- Wraps o2dlm AST callbacks:
  - `o2dlm_lock_ast_wrapper()` dispatches grant ASTs to the active cluster protocol.
  - `o2dlm_blocking_ast_wrapper()` dispatches blocking ASTs.
  - `o2dlm_unlock_ast_wrapper()` maps status to errno and suppresses duplicate cancel-after-grant completion.
- Implements DLM operations:
  - `o2cb_dlm_lock()` calls `dlmlock()`.
  - `o2cb_dlm_unlock()` calls `dlmunlock()`.
  - `o2cb_dlm_lock_status()` reads status from the o2dlm lock status block.
  - `o2cb_dlm_lvb_valid()` always returns true because o2dlm zeroes lost LVB state rather than marking it invalid.
  - `o2cb_dlm_lvb()` returns the o2dlm LVB pointer.
  - `o2cb_dump_lksb()` dumps a lock by o2dlm lock id.
- Checks cluster readiness in `o2cb_cluster_check()`:
  - verifies this node is configured.
  - verifies heartbeat is active for this node.
  - compares heartbeat node map and o2net connected node map for up to 60 seconds.
  - reports nodes that are heartbeating but not reachable over o2net.
- Implements cluster connection lifecycle:
  - `o2cb_cluster_connect()` runs the cluster check, allocates private state, registers an eviction callback, computes the DLM domain key from CRC32 of the lockspace name, registers the DLM domain, stores negotiated protocol version, and registers eviction handling.
  - `o2cb_cluster_disconnect()` unregisters eviction callback and DLM domain, then frees private state.
  - `o2cb_cluster_this_node()` returns the configured local node number with range checks.
- Registers the plugin:
  - `o2cb_stack_ops` provides stackglue callbacks.
  - `o2cb_stack` is named `"o2cb"`.
  - module init/exit register and unregister with `ocfs2_stack_glue`.

Key invariants:
- OCFS2 does not join an o2cb lockspace until heartbeat and o2net connectivity agree for all heartbeating nodes.
- o2dlm eviction callbacks drive OCFS2 recovery callbacks for dead nodes.
- The DLM domain key must be stable across all nodes mounting the same domain, so it is derived from the shared connection name.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stack_o2cb.c -->