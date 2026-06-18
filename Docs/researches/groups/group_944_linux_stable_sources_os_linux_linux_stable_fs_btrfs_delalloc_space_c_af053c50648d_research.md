# Group Research: group_944_linux_stable_sources_os_linux_linux_stable_fs_btrfs_delalloc_space_c_af053c50648d

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation data and metadata space accounting. It is the reservation layer used before dirty buffered data, direct I/O allocations, ordered extents, checksum items, and extent-tree updates become fully committed filesystem metadata.

Key responsibilities:
- Reserve and release data bytes in `space_info->bytes_may_use`.
- Reserve and release qgroup data and metadata space.
- Maintain per-inode delayed allocation metadata reserve state through `inode->block_rsv`.
- Track `inode->outstanding_extents` and `inode->csum_bytes`.
- Convert reservation ownership between prealloc/qgroup metadata accounting and transaction accounting.
- Handle zoned data relocation using a special data-relocation subgroup.

Important functions:
- `data_sinfo_for_inode()` selects normal data space info, except zoned data relocation roots use `BTRFS_SUB_GROUP_DATA_RELOC`.
- `btrfs_alloc_data_chunk_ondemand()` aligns requested bytes and reserves data bytes with the correct flush mode.
- `btrfs_check_data_free_space()` reserves data bytes and qgroup data ranges, rolling back both on failure.
- `btrfs_free_reserved_data_space_noquota()` drops data bytes from `bytes_may_use` without qgroup handling.
- `btrfs_free_reserved_data_space()` aligns the range, frees data reservation, and frees qgroup data reservation.
- `btrfs_calculate_inode_block_rsv_size()` recomputes the inode block reserve size from outstanding extents and checksum leaves.
- `calc_inode_reservations()` calculates metadata and qgroup reservation sizes for a new dirty range.
- `btrfs_delalloc_reserve_metadata()` pre-reserves metadata/qgroup space, updates `outstanding_extents` and `csum_bytes`, then adds bytes to the inode block reserve.
- `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the reserve, and releases excess metadata.
- `btrfs_delalloc_release_extents()` releases the temporary outstanding-extents accounting taken during reservation.
- `btrfs_delalloc_shrink_extents()` adjusts outstanding extent count when a previously reserved range shrinks.
- `btrfs_delalloc_reserve_space()` combines data and metadata reservation for delayed allocation.
- `btrfs_delalloc_release_space()` releases both metadata and data reservations.

Concurrency and invariants:
- `inode->lock` protects `outstanding_extents`, `csum_bytes`, and block reserve size recalculation.
- `block_rsv->lock` protects block reserve size and qgroup reservation fields.
- Reservation order is deliberate: qgroup metadata, metadata bytes, inode counters, then block reserve bytes.
- `btrfs_is_testing()` bypasses actual block reserve release in test contexts.
- All data reservation lengths are sectorsize-aligned.

Error handling:
- Data reservation failure returns immediately.
- Qgroup data reservation failure frees data bytes and the extent changeset.
- Metadata reservation failure frees qgroup prealloc.
- Combined reservation failure frees data/qgroup reservations and resets the caller changeset pointer.

Role in Btrfs:
This file is central to ENOSPC correctness for delayed allocation. It bridges user writes, qgroup limits, ordered extents, checksums, and metadata insertion costs before actual extent and checksum items are written.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.h

This header declares the delayed allocation reservation API used by Btrfs write, direct I/O, extent, and cleanup paths.

Exported API groups:
- Data reservation:
  - `btrfs_alloc_data_chunk_ondemand()`
  - `btrfs_check_data_free_space()`
  - `btrfs_free_reserved_data_space()`
  - `btrfs_free_reserved_data_space_noquota()`
- Combined delalloc reservation:
  - `btrfs_delalloc_reserve_space()`
  - `btrfs_delalloc_release_space()`
- Metadata-only reservation:
  - `btrfs_delalloc_reserve_metadata()`
  - `btrfs_delalloc_release_metadata()`
- Outstanding extent accounting:
  - `btrfs_delalloc_release_extents()`
  - `btrfs_delalloc_shrink_extents()`

Types are forward-declared to keep the interface light:
- `struct extent_changeset`
- `struct btrfs_inode`
- `struct btrfs_fs_info`

Role in Btrfs:
The header exposes the public reservation contract for code that dirties data or creates ordered extents. Callers must pair reserve and release functions carefully, especially when qgroup changesets are involved.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.c

This file implements delayed inode and delayed directory-index item handling. It batches inode item updates and directory index insert/delete operations so metadata modifications can be deferred, merged, and flushed later through transaction or async worker paths.

Major concepts:
- A `btrfs_delayed_node` exists per inode and is cached in both the inode and root xarray.
- Delayed insertion and deletion items are stored in separate cached rbtrees by directory index.
- Dirty inode updates are stored in `node->inode_item`.
- Nodes are linked into global delayed-root lists for background processing.
- Ref tracking is optionally enabled under `CONFIG_BTRFS_DEBUG`.

Initialization:
- `btrfs_delayed_inode_init()` creates the delayed-node slab cache.
- `btrfs_delayed_inode_exit()` destroys it.
- `btrfs_init_delayed_root()` initializes counters, locks, wait queue, and node lists.

Delayed node lifetime:
- `btrfs_get_delayed_node()` looks up an existing node from the inode cache or root xarray and handles races with refcount zeroing.
- `btrfs_get_or_create_delayed_node()` allocates, initializes, reserves an xarray slot, and publishes a new node.
- `btrfs_release_delayed_node()` and `btrfs_release_prepared_delayed_node()` requeue or dequeue nodes depending on pending item count, then drop references.
- `btrfs_remove_delayed_node()` removes the inode-cache reference during eviction.

Delayed item management:
- `btrfs_alloc_delayed_item()` allocates flexible-array delayed items.
- `__btrfs_add_delayed_item()` inserts into insertion or deletion rbtree and increments global delayed item count.
- `__btrfs_remove_delayed_item()` removes from rbtree and decrements delayed item count.
- `finish_one_item()` updates item sequence and wakes waiters when thresholds are crossed.

Metadata reservation:
- `btrfs_delayed_item_reserve_metadata()` migrates transaction reservation into `fs_info->delayed_block_rsv`.
- `btrfs_delayed_item_release_metadata()` releases delayed-item metadata bytes.
- Insertions reserve by delayed-node leaf batches rather than per item.
- `btrfs_delayed_inode_reserve_metadata()` reserves or migrates metadata for delayed inode item updates.
- `btrfs_delayed_inode_release_metadata()` releases or converts qgroup metadata reservations.

Flushing delayed items:
- `btrfs_insert_delayed_item()` batches contiguous delayed directory index insertions into one leaf when possible.
- `btrfs_insert_delayed_items()` flushes all delayed insertion items for a node.
- `btrfs_batch_delete_items()` batches adjacent deletion items found in the same leaf.
- `btrfs_delete_delayed_items()` flushes all delayed deletion items for a node.
- `__btrfs_update_delayed_inode()` writes the delayed inode item and optionally deletes the last inode ref/extref.
- `__btrfs_commit_inode_delayed_items()` performs insertions, deletions, records the root in transaction, then updates the inode.

Execution paths:
- `btrfs_run_delayed_items()` flushes all delayed items for transaction commit.
- `btrfs_run_delayed_items_nr()` flushes a bounded number.
- `btrfs_commit_inode_delayed_items()` flushes delayed items for one inode.
- `btrfs_commit_inode_delayed_inode()` commits only the delayed inode item through a joined transaction.
- `btrfs_balance_delayed_items()` schedules background work when delayed item counts cross thresholds.
- `btrfs_async_run_delayed_root()` runs delayed work from the delayed worker queue.

Directory entry APIs:
- `btrfs_insert_delayed_dir_index()` creates a delayed insertion item containing a `btrfs_dir_item` payload.
- `btrfs_delete_delayed_dir_index()` cancels a pending insertion when possible, otherwise queues a deletion.
- `btrfs_inode_delayed_dir_index_count()` exports delayed directory index counter state to the inode.

Readdir and logging:
- `btrfs_readdir_get_delayed_items()` collects delayed insertions/deletions for directory iteration and upgrades inode locking to serialize list use.
- `btrfs_readdir_delayed_dir_index()` emits delayed insertion entries.
- `btrfs_should_delete_dir_index()` filters entries shadowed by delayed deletions.
- `btrfs_log_get_delayed_items()` and `btrfs_log_put_delayed_items()` collect delayed items for directory logging while avoiding duplicate log-list membership.

Inode update helpers:
- `fill_stack_inode_item()` snapshots VFS inode fields into a Btrfs inode item.
- `btrfs_fill_inode()` restores inode fields from a delayed inode item.
- `btrfs_delayed_update_inode()` queues or refreshes a delayed inode item.
- `btrfs_delayed_delete_inode_ref()` queues delayed deletion of a single inode ref, except during log recovery.

Cleanup:
- `btrfs_kill_delayed_inode_items()` kills delayed items for one inode.
- `btrfs_kill_all_delayed_nodes()` kills all nodes for a root.
- `btrfs_destroy_delayed_inodes()` kills all delayed nodes in the filesystem delayed-root list.
- `btrfs_assert_delayed_root_empty()` warns if delayed nodes remain.

Concurrency:
- `delayed_node->mutex` protects rbtrees, delayed inode state, delayed item lists, batch-size counters, and node item count.
- `delayed_root->lock` protects node lists and delayed-root counters.
- Root `delayed_nodes` xarray is protected by `xa_lock()`.
- Delayed item reference counts protect temporary readdir/logging list ownership.

Role in Btrfs:
This file amortizes high-frequency directory and inode metadata changes. It reduces btree churn during creates, deletes, renames, inode updates, logging, and transaction commits while preserving precise metadata reservation accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.h

This header defines delayed inode and delayed directory-item data structures plus their public APIs.

Core structures:
- `enum btrfs_delayed_item_type`
  - `BTRFS_DELAYED_INSERTION_ITEM`
  - `BTRFS_DELAYED_DELETION_ITEM`
- `struct btrfs_delayed_node`
  - Per-inode delayed metadata node.
  - Tracks inode id, root, reserved bytes, insertion/deletion rbtrees, mutex, delayed inode item, refs, item count, directory index counter, list flags, batching state, and debug ref trackers.
- `struct btrfs_delayed_item`
  - Rbtree item for delayed directory index insertion/deletion.
  - Contains index key offset, tree/readdir/log list links, reserved bytes, parent delayed node, refcount, type, logged state, payload length, and flexible data payload.

Flags:
- `BTRFS_DELAYED_NODE_IN_LIST`
- `BTRFS_DELAYED_NODE_INODE_DIRTY`
- `BTRFS_DELAYED_NODE_DEL_IREF`

Public API:
- Initialization and teardown:
  - `btrfs_delayed_inode_init()`
  - `btrfs_delayed_inode_exit()`
  - `btrfs_init_delayed_root()`
- Directory index operations:
  - `btrfs_insert_delayed_dir_index()`
  - `btrfs_delete_delayed_dir_index()`
  - `btrfs_inode_delayed_dir_index_count()`
- Running delayed work:
  - `btrfs_run_delayed_items()`
  - `btrfs_run_delayed_items_nr()`
  - `btrfs_balance_delayed_items()`
  - `btrfs_commit_inode_delayed_items()`
  - `btrfs_commit_inode_delayed_inode()`
- Inode update/delete:
  - `btrfs_delayed_update_inode()`
  - `btrfs_fill_inode()`
  - `btrfs_delayed_delete_inode_ref()`
- Cleanup:
  - `btrfs_remove_delayed_node()`
  - `btrfs_kill_delayed_inode_items()`
  - `btrfs_kill_all_delayed_nodes()`
  - `btrfs_destroy_delayed_inodes()`
- Readdir/logging support:
  - `btrfs_readdir_get_delayed_items()`
  - `btrfs_readdir_put_delayed_items()`
  - `btrfs_should_delete_dir_index()`
  - `btrfs_readdir_delayed_dir_index()`
  - `btrfs_log_get_delayed_items()`
  - `btrfs_log_put_delayed_items()`

Debug support:
- Under `CONFIG_BTRFS_DEBUG`, delayed node reference tracker directories and references are allocated, freed, printed, and quarantined.
- Without debug config, tracker helpers compile to no-ops.

Role in Btrfs:
The header is the contract for deferred inode and directory-index metadata batching. It exposes enough state for transaction, inode eviction, readdir, and logging code while keeping implementation details in `delayed-inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.c

This file implements delayed back-reference tracking for Btrfs extents. It queues extent refcount changes, merges compatible operations, maintains reservation accounting, tracks qgroup dirty extents, and supplies ordered ref heads to extent-tree processing.

Purpose:
- Avoid deep recursive extent-tree updates while modifying btrees.
- Batch and merge frequent backref updates.
- Keep accurate delayed ref, csum deletion, qgroup, and reserved extent accounting until transaction commit.

Slab caches:
- `btrfs_delayed_ref_head_cachep`
- `btrfs_delayed_ref_node_cachep`
- `btrfs_delayed_extent_op_cachep`

Reservation management:
- `btrfs_check_space_for_delayed_refs()` compares delayed-ref reserve size against delayed reserve plus global reserve.
- `btrfs_delayed_refs_rsv_release()` releases metadata reservation for delayed refs and pending csum deletions.
- `btrfs_update_delayed_refs_rsv()` transfers bytes from a transaction-local delayed reserve into the filesystem delayed-ref reserve.
- `btrfs_inc/dec_delayed_refs_rsv_bg_inserts()` account block group item insertions.
- `btrfs_inc/dec_delayed_refs_rsv_bg_updates()` account block group item updates.
- `btrfs_zoned_cap_metadata_reservation()` caps delayed-ref reservation on zoned filesystems.
- `btrfs_delayed_refs_rsv_refill()` reserves metadata bytes up to one delayed-ref item unit and handles races with other refillers.

Ref comparison and merging:
- `comp_data_refs()` compares data refs by objectid and file-relative offset.
- `comp_refs()` compares ref type, parent/ref root, data ref payload, and optionally sequence.
- `tree_insert()` inserts into a delayed-ref head rbtree.
- `merge_ref()` merges adjacent equivalent refs, canceling opposite add/drop operations when possible.
- `btrfs_merge_delayed_refs()` merges metadata refs that are not held back by tree mod log sequence requirements.
- `btrfs_check_delayed_seq()` detects refs that must wait behind the current tree mod log lowest sequence.

Ref head selection:
- Delayed ref heads are tracked in `delayed_refs->head_refs` xarray indexed by bytenr shifted by sectorsize bits.
- `btrfs_select_ref_head()` selects the next non-processing head, marks it processing, updates ready counters and scan start, then locks the head mutex.
- `btrfs_unselect_ref_head()` clears processing and requeues readiness.
- `btrfs_delete_ref_head()` removes a head from the xarray and updates counters.
- `btrfs_select_delayed_ref()` prefers add refs from `ref_add_list` before drops to avoid deleting an extent item before pending additions are applied.

Adding refs:
- `init_delayed_ref_head()` initializes aggregate head state, ref_mod, reserved bytes, extent-op state, data/system flags, metadata level, and qgroup record fields.
- `add_delayed_ref_head()` inserts or updates a head, handles qgroup trace record insertion, pending csum accounting, and head counters.
- `init_delayed_ref_common()` initializes an individual delayed ref node from `struct btrfs_ref`.
- `btrfs_init_tree_ref()` initializes metadata ref details and qgroup skip policy.
- `btrfs_init_data_ref()` initializes data ref details and qgroup skip policy.
- `add_delayed_ref()` allocates node/head/qgroup record, reserves xarray slots, inserts the head and node under lock, updates delayed-ref reserve, emits tracepoints, and posts qgroup trace records.
- `btrfs_add_delayed_tree_ref()` wraps metadata refs.
- `btrfs_add_delayed_data_ref()` wraps data refs.
- `btrfs_add_delayed_extent_op()` queues a head-only extent operation update.

Lookup helpers:
- `btrfs_find_delayed_ref_head()` loads a head by bytenr under delayed-root lock.
- `btrfs_find_delayed_tree_ref()` searches a head for an add ref matching a metadata root/parent pair.

Cleanup:
- `btrfs_put_delayed_ref()` releases node refcounts.
- `btrfs_destroy_delayed_refs()` destroys all remaining delayed refs during transaction abort/cleanup. It drops nodes, frees extent ops, deletes heads, handles must-insert-reserved pinning, cleans accounting, and destroys qgroup extent records.
- `btrfs_delayed_ref_init()` creates caches.
- `btrfs_delayed_ref_exit()` destroys caches.

Concurrency:
- `delayed_refs->lock` protects xarrays, head counters, pending csums, flags, and scan position.
- Each head has a mutex for processing serialization.
- Each head also has a spinlock protecting its rbtree and add-list.
- Locking carefully handles the race where a head disappears while waiting for its mutex.

Role in Btrfs:
This file is core transaction infrastructure for extent reference consistency. It ensures COW extent allocation/free/reference updates can be queued safely, merged, accounted, and replayed against the extent tree without corrupting refcounts or exhausting metadata reserves unexpectedly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.h

This header defines delayed extent-reference data structures, reservation helpers, and the API used by extent-tree and transaction code.

Core enums:
- `enum btrfs_delayed_ref_action`
  - `BTRFS_ADD_DELAYED_REF`
  - `BTRFS_DROP_DELAYED_REF`
  - `BTRFS_ADD_DELAYED_EXTENT`
  - `BTRFS_UPDATE_DELAYED_HEAD`
- `enum btrfs_delayed_ref_flags`
  - `BTRFS_DELAYED_REFS_FLUSHING`
- `enum btrfs_ref_type`
  - `BTRFS_REF_NOT_SET`
  - `BTRFS_REF_DATA`
  - `BTRFS_REF_METADATA`

Reference payloads:
- `struct btrfs_data_ref`
  - Referring inode objectid and file-relative offset.
- `struct btrfs_tree_ref`
  - Tree block level.

Core structures:
- `struct btrfs_delayed_ref_node`
  - Individual delayed ref operation in a head rbtree.
  - Tracks bytenr, length, sequence, ref root, parent, refcount, ref_mod, action, key type, and data/tree payload.
- `struct btrfs_delayed_extent_op`
  - Pending extent item key/flag updates.
- `struct btrfs_delayed_ref_head`
  - Per-extent aggregate state and processing lock.
  - Tracks total/current ref_mod, reserved bytes, owning root, level, data/system flags, processing/tracked state, extent op, and per-head rbtree/list.
- `struct btrfs_delayed_ref_root`
  - Transaction-level delayed refs state.
  - Tracks head refs, dirty extents, counters, pending csums, flags, scan position, and qgroup skip root.
- `struct btrfs_ref`
  - Generic ref initializer used by callers before queueing delayed refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` calculates metadata reservation for delayed refs and doubles it when free-space tree updates are needed.
- `btrfs_calc_delayed_ref_csum_bytes()` calculates metadata needed for csum deletion.
- `btrfs_alloc_delayed_extent_op()` and `btrfs_free_delayed_extent_op()` manage extent-op cache objects.
- `btrfs_ref_head_to_space_flags()` maps a ref head to data/system/metadata block group flags.
- `btrfs_put_delayed_ref_head()` drops head references.
- `btrfs_delayed_ref_unlock()` unlocks a head mutex.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose owner/offset fields by ref kind.
- `btrfs_ref_type()` maps generic refs to Btrfs extent-tree key types.

Public API:
- Initialization:
  - `btrfs_delayed_ref_init()`
  - `btrfs_delayed_ref_exit()`
- Generic ref setup:
  - `btrfs_init_tree_ref()`
  - `btrfs_init_data_ref()`
- Queueing:
  - `btrfs_add_delayed_tree_ref()`
  - `btrfs_add_delayed_data_ref()`
  - `btrfs_add_delayed_extent_op()`
- Processing:
  - `btrfs_merge_delayed_refs()`
  - `btrfs_find_delayed_ref_head()`
  - `btrfs_delete_ref_head()`
  - `btrfs_select_ref_head()`
  - `btrfs_unselect_ref_head()`
  - `btrfs_select_delayed_ref()`
  - `btrfs_check_delayed_seq()`
  - `btrfs_find_delayed_tree_ref()`
- Reservation:
  - `btrfs_delayed_refs_rsv_release()`
  - `btrfs_update_delayed_refs_rsv()`
  - block-group insert/update reserve increment/decrement helpers
  - `btrfs_delayed_refs_rsv_refill()`
  - `btrfs_check_space_for_delayed_refs()`
- Cleanup:
  - `btrfs_put_delayed_ref()`
  - `btrfs_destroy_delayed_refs()`

Role in Btrfs:
This header is the delayed-ref contract for transaction and extent-tree code. It encodes how extent reference mutations are represented before they are applied to persistent extent metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dev-replace.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/dev-replace.c

This file implements Btrfs device replacement. It copies existing extents from a source device to a target device while the filesystem remains writable, duplicates new writes during the replacement window, persists replace state, and swaps the target into the filesystem at completion.

Design:
- Existing committed extents are copied by scrub.
- New writes are duplicated to both source and target via mapping logic outside this file.
- NOCOW hazards are handled by marking block groups read-only/to-copy where needed.
- Completion swaps source and target device identities and mapping-tree references.
- Cancel, suspend, and resume paths preserve or clean persistent replace state.

Initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device root.
- Missing or corrupt replace items initialize the state to `NEVER_STARTED`, unless a replace target device is found, which is treated as filesystem inconsistency.
- Active `STARTED` or `SUSPENDED` states resolve source and target devices and set target geometry/state.

Target setup:
- `btrfs_init_dev_replace_tgtdev()` opens the target block device writable, checks zoned compatibility, rejects devices already in the filesystem, checks size, allocates a `btrfs_device`, initializes geometry/accounting, gets zone info, and links it into `fs_devices`.

Persistent state:
- `btrfs_run_dev_replace()` writes in-memory replace state back to the device tree during transaction commit.
- It creates or rewrites the dev-replace item, stores source devid, state, read mode, timestamps, error counters, and cursors.

Zoned block-group handling:
- `mark_block_group_to_copy()` marks block groups that have source-device extents with `BLOCK_GROUP_FLAG_TO_COPY` on zoned filesystems.
- `btrfs_finish_block_group_to_copy()` clears the flag once the last relevant stripe on the source device is copied.

Start path:
- `btrfs_dev_replace_start()` resolves the source device, rejects active swapfile usage, commits pending transactions for stable device byte counters, initializes the target, marks block groups to copy, sets replace state to `STARTED`, adds sysfs device state, waits ordered roots, commits the replace item, runs scrub over the source device, then calls finishing.
- `btrfs_dev_replace_by_ioctl()` validates ioctl arguments and source/target names before calling start.

Finishing path:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount, verifies `STARTED`, flushes delalloc and ordered roots, repeatedly commits until source post-commit work is clear, locks device list and chunk mutex, sets final state, and either cleans up on scrub failure or performs the swap.
- On success it:
  - Copies allocation state from source to target.
  - Updates all chunk maps to point source stripes at target.
  - Swaps devids and UUIDs.
  - Copies byte accounting.
  - Assigns active device replacement.
  - Adds target to alloc list and rw device count.
  - Blocks new bios during source removal.
  - Removes source from filesystem metadata.
  - Updates sysfs entries.
  - Scratches source superblocks if writable.
  - Commits superblocks and frees source device.

Mapping tree update:
- `btrfs_dev_replace_update_device_in_mapping_tree()` walks the chunk mapping rbtree under `chunk_mutex` and `mapping_tree_lock`, replacing source device pointers with target device pointers.

Status:
- `btrfs_dev_replace_progress()` returns progress in per-mille.
- `btrfs_dev_replace_status()` fills ioctl status fields with state, timestamps, errors, and progress.

Cancel/suspend/resume:
- `btrfs_dev_replace_cancel()` cancels active scrub or cleans up suspended replace state and commits cancellation.
- `btrfs_dev_replace_suspend_for_unmount()` changes `STARTED` to `SUSPENDED` and marks state for writeback.
- `btrfs_resume_dev_replace_async()` resumes started/suspended replace in a kernel thread if the target is present and no conflicting exclusive operation is running.
- `btrfs_dev_replace_kthread()` resumes scrub from `committed_cursor_left`, finishes replacement, and releases exclusive operation state.
- `btrfs_dev_replace_is_ongoing()` reports active/suspended replace as ongoing even if target is missing.

Bio synchronization:
- `btrfs_rm_dev_replace_blocked()` sets filesystem replacing state and waits for in-flight replace-protected bios to drain.
- `btrfs_rm_dev_replace_unblocked()` clears the blocked state and wakes waiters.
- `btrfs_bio_counter_inc_blocked()`, `btrfs_bio_counter_sub()`, and `btrfs_bio_counter_dec()` protect bio submission during replace device removal/swap.

Concurrency:
- `dev_replace->rwsem` protects replace state fields.
- `dev_replace->lock_finishing_cancel_unmount` serializes finish, cancel, and unmount suspension.
- `fs_devices->device_list_mutex`, `fs_info->chunk_mutex`, and `mapping_tree_lock` protect device and chunk mapping changes.
- A percpu bio counter gates device removal against in-flight I/O.

Role in Btrfs:
This file implements online device migration/replacement with persistent crash-resumable state, scrub-based copying, write duplication, and careful final device identity swap.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dev-replace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dev-replace.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/dev-replace.h

This header declares the Btrfs device replacement interface.

Public API:
- Lifecycle and persistence:
  - `btrfs_init_dev_replace()`
  - `btrfs_run_dev_replace()`
  - `btrfs_resume_dev_replace_async()`
  - `btrfs_dev_replace_suspend_for_unmount()`
- Ioctl-facing operations:
  - `btrfs_dev_replace_by_ioctl()`
  - `btrfs_dev_replace_status()`
  - `btrfs_dev_replace_cancel()`
- State helpers:
  - `btrfs_dev_replace_is_ongoing()`
  - `btrfs_finish_block_group_to_copy()`
- Bio synchronization:
  - `btrfs_bio_counter_inc_blocked()`
  - `btrfs_bio_counter_sub()`
  - `btrfs_bio_counter_dec()`

Forward declarations keep this interface independent of full structure definitions:
- `btrfs_ioctl_dev_replace_args`
- `btrfs_fs_info`
- `btrfs_trans_handle`
- `btrfs_dev_replace`
- `btrfs_block_group`
- `btrfs_device`

Role in Btrfs:
The header exposes replace control, status, resume, block-group progress, and bio-counter primitives to transaction, ioctl, scrub, mapping, and unmount paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dev-replace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dir-item.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision checking, matching, and deletion. Directory names and xattrs are keyed by CRC32C name hash and can store multiple colliding names inside one btree item.

Insertion:
- `insert_with_overflow()` inserts an empty item for a hash key or extends an existing item on hash collision. It rejects exact duplicate names and returns a pointer to the newly reserved sub-item area.
- `btrfs_insert_xattr_item()` inserts an xattr as a `BTRFS_XATTR_ITEM_KEY`, validates maximum xattr size, initializes the dir-item payload, and writes name/data bytes.
- `btrfs_insert_dir_item()` inserts the name-hash directory item and queues the directory index item through `btrfs_insert_delayed_dir_index()`, except for the tree root. Encrypted directories mark the file type with `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` searches a btree key and then scans the item payload for the requested name.
- `btrfs_lookup_dir_item()` looks up a directory entry by name hash and name.
- `btrfs_lookup_dir_index_item()` looks up a directory index entry by index and name.
- `btrfs_search_dir_index_item()` scans directory index keys for a matching name.
- `btrfs_lookup_xattr()` looks up xattr items by name hash and name.

Collision handling:
- `btrfs_check_dir_item_collision()` checks whether a hash key already has the exact name, has enough room for another colliding name, or would overflow a leaf.
- Return meanings:
  - `0`: safe to insert.
  - `-EEXIST`: exact name already exists.
  - `-EOVERFLOW`: hash collision item lacks room.
  - Other negative errors from search/allocation.

Matching:
- `btrfs_match_dir_item_name()` walks all packed `btrfs_dir_item` entries inside a single btree item and compares name lengths and name bytes using extent-buffer accessors.

Deletion:
- `btrfs_delete_one_dir_name()` deletes a packed dir-item entry. If it is the only sub-item, it deletes the btree item; otherwise it memmoves later sub-items down and truncates the item.

Data layout:
- Directory and xattr entries use `struct btrfs_dir_item` followed by name bytes and optional data bytes.
- Name hash is `crc32c((u32)~1, name, len)` via the header helper.

Role in Btrfs:
This file handles the low-level packed directory/xattr item format. It works with delayed inode code for directory index insertion while directly managing name-hash items in the subvolume tree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dir-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dir-item.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/dir-item.h

This header declares Btrfs directory item and xattr item helpers.

Public API:
- Directory insertion and collision:
  - `btrfs_check_dir_item_collision()`
  - `btrfs_insert_dir_item()`
- Directory lookup:
  - `btrfs_lookup_dir_item()`
  - `btrfs_lookup_dir_index_item()`
  - `btrfs_search_dir_index_item()`
- Directory deletion/matching:
  - `btrfs_delete_one_dir_name()`
  - `btrfs_match_dir_item_name()`
- Xattr insertion/lookup:
  - `btrfs_insert_xattr_item()`
  - `btrfs_lookup_xattr()`

Hash helper:
- `btrfs_name_hash()` computes CRC32C with seed `~1`, returning the hash used as the key offset for directory and xattr name-hash items.

Role in Btrfs:
The header exposes the packed dir-item/xattr-item primitives used by inode, directory, rename, xattr, and delayed directory-index code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/dir-item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/direct-io.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O using iomap. It handles direct read/write mapping, extent locking, ordered extents, NOCOW/prealloc writes, COW allocation, fallback to buffered I/O, bio submission, and completion.

Private structures:
- `struct btrfs_dio_data`
  - Tracks submitted byte count, data reservation changeset, current ordered extent, whether data space was reserved, and whether NOCOW succeeded.
- `struct btrfs_dio_private`
  - Stores file offset and byte count for a bio, followed by embedded `struct btrfs_bio`.
- `btrfs_dio_bioset`
  - Bioset used for direct I/O bios.

Range locking:
- `lock_extent_direct()` takes the DIO extent lock before the regular extent lock.
- It waits for conflicting ordered extents and rejects or falls back if page cache invalidation cannot be guaranteed.
- NOWAIT paths return `-EAGAIN` instead of blocking.
- DIO reads avoid waiting for buffered ordered extents in cases that could deadlock.

Direct extent creation:
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates an ordered extent marked direct.
- `btrfs_new_extent_direct()` reserves a new on-disk extent for COW direct writes, retrying zoned allocation after zone finish events.

Direct write block mapping:
- `btrfs_get_blocks_direct_write()` decides between NOCOW/prealloc and COW:
  - NOCOW/prealloc path reserves metadata only, creates ordered extent, and marks `nocow_done`.
  - COW path requires data space reserved before locking, reserves metadata, allocates a new extent, and releases excess metadata if allocation is shorter than requested.
- It releases temporary outstanding extent reservations after ordered extent creation.
- It updates `i_size` under the extent lock for extending writes.

Iomap begin/end:
- `btrfs_dio_iomap_begin()`:
  - Handles NOWAIT restrictions.
  - Caps read length for checksum array sizing.
  - Flushes async compressed pages when needed.
  - Pre-reserves data space for blocking writes before range locking.
  - Locks the DIO/extent range.
  - Looks up extent maps.
  - Falls back for inline or compressed extents.
  - Avoids partial NOWAIT I/O over multiple extents.
  - Performs write-specific mapping/allocation.
  - Fills `struct iomap`.
  - Releases extent locks appropriately while keeping read DIO locks until completion.
- `btrfs_dio_iomap_end()`:
  - Unlocks holes for reads.
  - Handles short submission by finishing/canceling unwritten ordered write ranges or unlocking unread ranges.
  - Drops ordered extent refs and frees data reservation changesets.

Bio completion/submission:
- `btrfs_dio_end_io()` logs bio errors, finishes ordered extents for writes, unlocks DIO extents for reads, restores bio private pointer, and completes iomap bio.
- `btrfs_extract_ordered_extent()` splits ordered extents for partial submitted writes and splits extent maps for non-NOCOW writes.
- `btrfs_dio_submit_io()` initializes `btrfs_bio`, records range, updates submitted bytes, extracts/splits ordered extent for writes, and submits via `btrfs_submit_bbio()`.

Read/write wrappers:
- `btrfs_dio_read()` calls `iomap_dio_rw()` with partial and fsblock-aligned flags.
- `btrfs_dio_write()` calls `__iomap_dio_rw()` with the same direct-I/O flags.

Alignment validation:
- `check_direct_IO()` requires file offset and iterator alignment to sectorsize.
- `check_direct_read()` also rejects duplicate iovec base addresses for direct reads.

Direct write policy:
- `btrfs_direct_write()`:
  - Uses NOWAIT try-locking when requested.
  - Uses shared inode locking only for within-EOF writes that cannot drop security bits.
  - Falls back to buffered writes for duplicated data profiles other than RAID0/SINGLE, because user buffers can change during mirror writes.
  - Falls back to buffered writes if alignment fails or data checksums are enabled.
  - Disables iov page faults during DIO to avoid mmap self-deadlocks, then faults pages and retries on `-EFAULT`.
  - For fallback buffered writes, writes data, flushes/waits it, advances position, and invalidates page cache so subsequent direct reads see persisted data.

Direct read policy:
- `btrfs_direct_read()`:
  - Returns 0 when fsverity is active or direct-read checks fail.
  - Takes shared inode lock.
  - Disables page faults and iov faults during DIO to avoid extent-lock deadlocks.
  - Faults destination pages and retries on partial progress or `-EFAULT`.
  - Returns accumulated bytes read.

Initialization:
- `btrfs_init_dio()` initializes the DIO bioset.
- `btrfs_destroy_dio()` exits the bioset.

Role in Btrfs:
This file is the bridge between Linux iomap direct I/O and Btrfs COW semantics. Its main complexity is preventing stale reads and deadlocks while preserving Btrfs ordered extent, checksum, NOCOW, page-cache, and reservation invariants.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/direct-io.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/direct-io.h

This header declares the Btrfs direct I/O interface.

Public API:
- Initialization:
  - `btrfs_init_dio()`
  - `btrfs_destroy_dio()`
- File operations:
  - `btrfs_direct_write()`
  - `btrfs_direct_read()`

Forward declarations:
- `struct kiocb`
- `struct iov_iter` is used by prototypes through included kernel type context.

Role in Btrfs:
The header exposes direct read/write entry points and bioset lifecycle hooks to the broader filesystem code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/direct-io.h -->