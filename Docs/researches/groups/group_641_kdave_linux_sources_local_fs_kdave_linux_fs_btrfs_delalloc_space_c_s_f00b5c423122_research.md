# Group Research: group_641_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_delalloc_space_c_s_f00b5c423122

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/kdave-linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation space accounting for buffered/direct writes, covering both data-space reservations and metadata/qgroup reservations needed for future file extent and checksum items.

Core responsibilities:
- Reserve data bytes against `space_info->bytes_may_use` before dirtying ranges.
- Free data reservations on error or unused ranges.
- Reserve per-inode metadata in `inode->block_rsv` based on `outstanding_extents` and `csum_bytes`.
- Coordinate qgroup data and metadata prealloc reservations.
- Maintain the temporary `outstanding_extents` accounting lifecycle around delalloc, ordered extents, and completion.

Key mechanisms:
- `data_sinfo_for_inode()` selects normal data space info, except zoned data relocation uses the relocation data subgroup.
- `btrfs_alloc_data_chunk_ondemand()` aligns bytes to sectorsize and reserves data bytes, using the free-space-inode flush policy when needed.
- `btrfs_check_data_free_space()` reserves data bytes first, then qgroup data range reservation; failure unwinds both.
- `btrfs_free_reserved_data_space_noquota()` only frees `bytes_may_use`, for contexts that cannot use accurate qgroup reservation handling.
- `btrfs_free_reserved_data_space()` aligns the range, frees data bytes, and releases qgroup data reservation records.
- `btrfs_calculate_inode_block_rsv_size()` recalculates the inode block reserve size from `outstanding_extents`, inode update metadata, checksum leaves, and qgroup metadata estimate.
- `calc_inode_reservations()` computes an upfront reservation for a new write operation, intentionally over-reserving rather than letting many inodes accumulate partial reservations.
- `btrfs_delalloc_reserve_metadata()` reserves qgroup metadata and metadata bytes, then updates `outstanding_extents` and `csum_bytes` before adding bytes to `inode->block_rsv`.
- `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the reservation, and releases excess block reserve space.
- `btrfs_delalloc_release_extents()` drops the temporary outstanding extent count that was held during reservation.
- `btrfs_delalloc_shrink_extents()` adjusts outstanding extent count when a previously reserved range shrinks.
- `btrfs_delalloc_reserve_space()` combines data and metadata reservation for delalloc.
- `btrfs_delalloc_release_space()` releases metadata and data reservation together.

Important invariants:
- Ranges are sectorsize aligned before reservation/free.
- Metadata accounting updates `inode->outstanding_extents` and `inode->csum_bytes` under `inode->lock`.
- `btrfs_delalloc_reserve_metadata()` must be paired with `btrfs_delalloc_release_extents()` once the caller’s temporary reservation responsibility has moved to delalloc or ordered extent state.
- `qgroup_free` distinguishes error cleanup from normal conversion into transaction-scoped qgroup metadata accounting.

Cross-file relationships:
- Used by direct I/O write setup in `direct-io.c`.
- Depends on block reserve helpers from `block-rsv.h`, space reservation from `space-info.h`, qgroup APIs from `qgroup.h`, and inode accounting from `btrfs_inode.h`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.h

This header exposes the delalloc data and metadata reservation API implemented by `delalloc-space.c`.

Declared API groups:
- Data reservation:
  - `btrfs_alloc_data_chunk_ondemand()`
  - `btrfs_check_data_free_space()`
  - `btrfs_free_reserved_data_space()`
  - `btrfs_free_reserved_data_space_noquota()`
- Combined delalloc reservation:
  - `btrfs_delalloc_reserve_space()`
  - `btrfs_delalloc_release_space()`
- Metadata reservation:
  - `btrfs_delalloc_reserve_metadata()`
  - `btrfs_delalloc_release_metadata()`
  - `btrfs_delalloc_release_extents()`
  - `btrfs_delalloc_shrink_extents()`

Design notes:
- Forward declares `extent_changeset`, `btrfs_inode`, and `btrfs_fs_info`.
- The API makes qgroup range tracking explicit through `struct extent_changeset **reserved` on reservation and `struct extent_changeset *reserved` on release.
- `btrfs_delalloc_reserve_metadata()` accepts separate logical and disk byte counts, which matters for compressed or otherwise transformed writes.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.c

This file implements delayed inode and delayed directory index item handling. It batches inode item updates, inode ref deletion, and directory index insert/delete operations so they can be flushed later through transaction processing or async workers.

Core data model:
- A `btrfs_delayed_root` tracks global delayed nodes and item counts.
- A `btrfs_delayed_node` is per inode, cached in the inode and indexed by root xarray.
- Each delayed node owns two rbtrees:
  - `ins_root` for delayed directory index insertions.
  - `del_root` for delayed directory index deletions.
- Items are ordered by directory index offset and can also be temporarily linked into readdir/logging lists.

Initialization and lifetime:
- `btrfs_delayed_inode_init()` creates the delayed node slab cache.
- `btrfs_init_delayed_root()` initializes global counters, lock, waitqueue, and node lists.
- `btrfs_get_delayed_node()` retrieves an existing node from inode cache or root xarray, handling races with node removal via `refcount_inc_not_zero()`.
- `btrfs_get_or_create_delayed_node()` allocates, initializes, reserves xarray storage, and installs a node.
- `btrfs_release_delayed_node()` requeues or dequeues based on pending item count, drops the caller ref, erases from the xarray on final ref, and frees the slab object.

Delayed item handling:
- `btrfs_alloc_delayed_item()` creates variable-length delayed items with inline data.
- `__btrfs_add_delayed_item()` inserts into the insertion or deletion rbtree and increments delayed item counters.
- `btrfs_release_delayed_item()` removes an item from its rbtree if present and frees it on last ref.
- `finish_one_item()` decrements global delayed item count and wakes waiters when thresholds/batches are crossed.

Metadata reservation:
- Delayed item insertion metadata is migrated from the transaction reservation to `fs_info->delayed_block_rsv`.
- Deletion items track `bytes_reserved` per item.
- Insertion items instead track reserved leaves in the delayed node using `index_item_leaves` and `curr_index_batch_size`.
- Delayed inode updates reserve one metadata update unit and track it in `node->bytes_reserved`.
- Release paths either free qgroup metadata or convert it depending on whether cleanup is error-like or normal transaction conversion.

Flush path:
- `btrfs_insert_delayed_item()` batches consecutive dir index insertion items into one leaf-sized insert where possible.
- During log replay, batching is restricted to continuous keys only.
- `btrfs_delete_delayed_items()` looks up delayed deletion keys and batch-deletes consecutive matching items from the leaf.
- `__btrfs_update_delayed_inode()` writes the delayed inode item to the tree and optionally deletes the final inode ref/extref for delayed iref deletion.
- `__btrfs_commit_inode_delayed_items()` runs insertions, deletions, records the root in the transaction, then updates the inode.
- `btrfs_run_delayed_items()` and `btrfs_run_delayed_items_nr()` flush global delayed nodes with `fs_info->delayed_block_rsv`.
- `btrfs_commit_inode_delayed_items()` flushes one inode’s delayed node.
- `btrfs_commit_inode_delayed_inode()` commits only the delayed inode item for eviction-style paths.

Async balancing:
- Thresholds:
  - `BTRFS_DELAYED_BACKGROUND` = 128
  - `BTRFS_DELAYED_WRITEBACK` = 512
  - `BTRFS_DELAYED_BATCH` = 16
- `btrfs_balance_delayed_items()` queues background work when pending delayed items exceed thresholds.
- `btrfs_async_run_delayed_root()` joins transactions and drains prepared delayed nodes from worker context.
- Waiters are woken using `items_seq` and delayed item count thresholds.

Directory index operations:
- `btrfs_insert_delayed_dir_index()` builds an inline `btrfs_dir_item`, inserts it into the node’s insertion rbtree, and reserves/reuses delayed item leaf metadata.
- `btrfs_delete_delayed_dir_index()` first tries to remove a not-yet-flushed insertion; otherwise it creates a deletion item.
- `btrfs_inode_delayed_dir_index_count()` copies the delayed node index counter back to the inode.

Readdir support:
- `btrfs_readdir_get_delayed_items()` collects delayed insertions and deletions up to a last index, taking extra item refs.
- It upgrades the inode lock from shared to exclusive to serialize use of `readdir_list`.
- `btrfs_readdir_delayed_dir_index()` emits delayed insertion items through `dir_emit()`.
- `btrfs_should_delete_dir_index()` checks whether an on-disk index should be suppressed by a delayed deletion.
- `btrfs_readdir_put_delayed_items()` drops item refs and downgrades the inode lock back to shared.

Delayed inode content:
- `fill_stack_inode_item()` snapshots VFS/Btrfs inode metadata into a stack-format inode item.
- `btrfs_fill_inode()` restores inode fields from a dirty delayed inode item if present.
- `btrfs_delayed_update_inode()` creates or updates delayed inode state and increments global delayed item accounting.
- `btrfs_delayed_delete_inode_ref()` marks final inode ref deletion for async handling, except during log recovery.

Cleanup:
- `__btrfs_kill_delayed_node()` removes pending insertion/deletion items, releases metadata, clears delayed inode/iref state.
- `btrfs_kill_delayed_inode_items()` handles one inode.
- `btrfs_kill_all_delayed_nodes()` walks the root xarray in batches and kills all nodes.
- `btrfs_destroy_delayed_inodes()` drains all delayed nodes from fs shutdown/transaction cleanup.
- `btrfs_assert_delayed_root_empty()` warns if delayed nodes remain.

Logging support:
- `btrfs_log_get_delayed_items()` gathers delayed items for directory logging, skipping already logged/listed items.
- `btrfs_log_put_delayed_items()` marks gathered items as logged and drops refs.
- These functions deliberately avoid normal node release/requeue semantics because logging is not mutating delayed item state.

Important locking:
- Root delayed lists use `delayed_root->lock`.
- Per-node rbtrees and dirty inode state use `delayed_node->mutex`.
- The root xarray uses `xa_lock`.
- The code avoids holding tree paths while releasing delayed nodes to prevent lock ordering deadlocks.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.h

This header defines delayed inode/directory item data structures and exports the delayed inode API.

Key structures:
- `enum btrfs_delayed_item_type`
  - `BTRFS_DELAYED_INSERTION_ITEM`
  - `BTRFS_DELAYED_DELETION_ITEM`
- `struct btrfs_delayed_node`
  - Identifies one inode by `inode_id` and `root`.
  - Tracks pending item count, delayed inode bytes reserved, index counter, and flags.
  - Owns insertion/deletion rbtrees.
  - Has node/prepared list links for global flush queues.
  - Tracks insertion leaf reservation state with `curr_index_batch_size` and `index_item_leaves`.
  - Includes debug-only reference tracking fields.
- `struct btrfs_delayed_item`
  - Rbtree node plus directory index offset.
  - Temporary list links for batch tree operations, readdir, and logging.
  - Per-item metadata reservation for deletion items.
  - Type, logged flag, data length, and flexible inline data.

Flags:
- `BTRFS_DELAYED_NODE_IN_LIST`
- `BTRFS_DELAYED_NODE_INODE_DIRTY`
- `BTRFS_DELAYED_NODE_DEL_IREF`

Exported operations:
- Delayed root lifecycle: `btrfs_init_delayed_root()`.
- Directory index insert/delete/query: `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, `btrfs_inode_delayed_dir_index_count()`.
- Flush and balancing: `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_balance_delayed_items()`, `btrfs_commit_inode_delayed_items()`.
- Inode update/fill/ref deletion: `btrfs_delayed_update_inode()`, `btrfs_fill_inode()`, `btrfs_delayed_delete_inode_ref()`, `btrfs_commit_inode_delayed_inode()`.
- Cleanup: `btrfs_remove_delayed_node()`, `btrfs_kill_delayed_inode_items()`, `btrfs_kill_all_delayed_nodes()`, `btrfs_destroy_delayed_inodes()`.
- Readdir and log integration helpers.
- Slab lifecycle: `btrfs_delayed_inode_init()`, `btrfs_delayed_inode_exit()`.

Debug support:
- Under `CONFIG_BTRFS_DEBUG`, delayed node references can be tracked with `ref_tracker`.
- When debug tracking is disabled, the helpers compile to no-ops.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-inode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.c

This file implements Btrfs delayed back reference tracking. It queues extent reference count changes and extent operations for later processing, reducing immediate extent-tree churn and avoiding deep update chains during btree modifications.

Core data model:
- Delayed ref heads are stored in an xarray keyed by logical bytenr shifted by `sectorsize_bits`.
- Each head represents one extent and owns an rbtree of delayed ref nodes.
- Ref nodes are sorted by ref type, parent/root identity, data ref fields, and sequence.
- Add refs are also linked into `ref_add_list` to prioritize additions before drops.
- Dirty qgroup extent records are tracked in a separate xarray.

Reservation accounting:
- `btrfs_check_space_for_delayed_refs()` compares delayed refs reserve size against delayed refs plus global reserve.
- `btrfs_delayed_refs_rsv_release()` drops delayed ref and csum deletion reservation units.
- `btrfs_update_delayed_refs_rsv()` moves pending per-transaction delayed ref/csum reservation demand into `fs_info->delayed_refs_rsv`, preferentially taking bytes from `trans->delayed_rsv`.
- Block group insert/update helpers adjust delayed refs reserve size for block group item operations.
- `btrfs_delayed_refs_rsv_refill()` reserves metadata bytes up to one delayed ref unit at a time and handles racing refillers.
- Zoned filesystems cap delayed refs reservation to half of usable metadata space via `btrfs_zoned_cap_metadata_reservation()`.

Comparison and merging:
- `comp_data_refs()` compares data refs by inode objectid and offset.
- `comp_refs()` compares full delayed ref identity.
- `tree_insert()` inserts into the per-head rbtree.
- `merge_ref()` collapses adjacent compatible refs with opposite or same actions, dropping zero-mod refs.
- `btrfs_merge_delayed_refs()` skips data refs, respects tree mod log sequence constraints, and repeatedly merges metadata refs.
- `btrfs_check_delayed_seq()` prevents running refs still needed by tree-mod-log readers.

Head selection:
- `btrfs_select_ref_head()` scans `head_refs` from `run_delayed_start`, skips processing heads, marks a selected head processing, decrements ready count, and locks the head mutex.
- `btrfs_unselect_ref_head()` clears processing and returns the head to ready state.
- `btrfs_delete_ref_head()` removes a head from xarray tracking and adjusts global counts.
- `btrfs_select_delayed_ref()` chooses add refs first, then the first rbtree ref.

Insertion:
- `init_delayed_ref_common()` initializes a ref node from generic `struct btrfs_ref`, including tree mod sequence for fs trees.
- `init_delayed_ref_head()` initializes the head, ref count delta, reserved bytes, data/system flags, level, qgroup record fields, and `must_insert_reserved` state.
- `add_delayed_ref_head()` inserts or updates a head, traces qgroup extent records, updates csum deletion reservation demand for data drops, and tracks head counts.
- `insert_delayed_ref()` inserts a ref node or merges it into an existing matching node.
- `add_delayed_ref()` allocates node/head/qgroup record, reserves xarray entries, initializes state, inserts both head and node under delayed refs lock, updates reserve accounting, and posts qgroup tracing.
- `btrfs_add_delayed_tree_ref()` and `btrfs_add_delayed_data_ref()` are typed wrappers.
- `btrfs_add_delayed_extent_op()` attaches delayed extent operation updates to an existing or new head without adding an individual ref.

Reference/query helpers:
- `btrfs_init_tree_ref()` initializes metadata refs and qgroup skip policy.
- `btrfs_init_data_ref()` initializes data refs and qgroup skip policy.
- `btrfs_find_delayed_ref_head()` looks up a head under delayed refs lock.
- `btrfs_find_delayed_tree_ref()` checks whether a matching tree ref add exists under a head.
- `btrfs_put_delayed_ref()` releases delayed ref node refs.

Abort cleanup:
- `btrfs_destroy_delayed_refs()` walks all heads, locks each, drops every pending ref node, frees delayed extent ops, deletes heads, and handles special accounting for `must_insert_reserved`.
- If a reserved extent was never inserted, cleanup may pin bytes in the block group and call `btrfs_error_unpin_extent_range()`.
- Qgroup extent records are destroyed after delayed refs are drained.

Slab lifecycle:
- `btrfs_delayed_ref_init()` creates slab caches for heads, nodes, and delayed extent ops.
- `btrfs_delayed_ref_exit()` destroys them.

Important invariants:
- `delayed_refs->lock` protects xarrays and global counts.
- `head->lock` protects the per-head rbtree and add list.
- `head->mutex` serializes running refs for a single extent.
- Add refs run before drop refs to avoid transient deletion of extent items that still need new refs.
- Xarray keys use shifted bytenr to fit 32-bit indexes better and produce denser index space.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.h

This header defines the delayed ref structures, enums, inline helpers, and exported delayed ref API.

Key enums:
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

Key structures:
- `struct btrfs_data_ref`
  - Stores inode objectid and data offset identity for extent data refs.
- `struct btrfs_tree_ref`
  - Stores tree block level for metadata refs.
- `struct btrfs_delayed_ref_node`
  - Represents one queued add/drop ref.
  - Carries bytenr, length, sequence, ref root, parent, ref mod, action, type, and data/tree identity.
- `struct btrfs_delayed_extent_op`
  - Holds delayed extent item key/flag updates.
- `struct btrfs_delayed_ref_head`
  - Represents all queued operations for one extent.
  - Holds mutex, ref tree, add list, extent op, total/current ref mods, owning root, reserved bytes, level, and processing/tracking flags.
- `struct btrfs_delayed_ref_root`
  - Tracks head refs and dirty qgroup extent records in xarrays.
  - Maintains counts, pending checksum bytes, flags, run cursor, and qgroup skip root.
- `struct btrfs_ref`
  - Generic input descriptor used to create delayed data or metadata refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` estimates metadata reservation for delayed refs, doubling when free-space-tree updates are required.
- `btrfs_calc_delayed_ref_csum_bytes()` estimates csum deletion metadata.
- `btrfs_alloc_delayed_extent_op()` / `btrfs_free_delayed_extent_op()` manage extent op slab objects.
- `btrfs_ref_head_to_space_flags()` maps a head to data/system/metadata block group flags.
- `btrfs_put_delayed_ref_head()` releases head refs.
- `btrfs_delayed_ref_unlock()` unlocks a selected head.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose type-dependent identity fields.
- `btrfs_ref_type()` maps generic ref fields to Btrfs backref item key type.

Exported API:
- Slab lifecycle: `btrfs_delayed_ref_init()`, `btrfs_delayed_ref_exit()`.
- Generic ref initialization: `btrfs_init_tree_ref()`, `btrfs_init_data_ref()`.
- Queueing: `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, `btrfs_add_delayed_extent_op()`.
- Selection/lookup: `btrfs_find_delayed_ref_head()`, `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_find_delayed_tree_ref()`.
- Reservation accounting: delayed refs reserve release/update/refill and block-group insert/update helpers.
- Cleanup: `btrfs_delete_ref_head()`, `btrfs_destroy_delayed_refs()`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/delayed-ref.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.c

This file implements Btrfs online device replacement: copying all existing extents from a source device to a target while duplicating new writes so the filesystem can remain mounted read-write.

High-level model:
- New writes are duplicated to source and target while replacement is active.
- Existing extents are copied using the scrub machinery.
- NOCOW hazards are avoided by marking block groups read-only/`TO_COPY` where needed, especially on zoned filesystems.
- Completion swaps source and target devices in mapping structures and device metadata.

Initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device tree.
- If the item is missing/corrupt, it initializes state as never started unless a dangling replace target exists.
- For active/suspended replacement, it resolves source and target devices, validates degraded/missing-device rules, and marks target as replace target/in metadata.
- Stored state includes source devid, read mode, state, timestamps, errors, cursors, and validity/writeback flags.

Target device setup:
- `btrfs_init_dev_replace_tgtdev()` opens the target path writeable, verifies zoned compatibility, rejects devices already in the filesystem, checks size, allocates a Btrfs device with special devid `BTRFS_DEV_REPLACE_DEVID`, initializes geometry/accounting, loads zone info, and links it into the device list.
- Errors close the opened block device file.

On-disk state writeback:
- `btrfs_run_dev_replace()` is called during transaction commit.
- It inserts or updates the device replace item in the device tree when `item_needs_writeback` is set.
- The function writes all mutable replace state under `dev_replace->rwsem`.

Zoned/block-group copy markers:
- `mark_block_group_to_copy()` scans source device extents from the commit root and marks corresponding block groups with `BLOCK_GROUP_FLAG_TO_COPY` on zoned filesystems.
- It waits out pending device updates by committing transactions before scanning.
- `btrfs_finish_block_group_to_copy()` clears `TO_COPY` only after the last stripe for that source device is copied.

Starting replacement:
- `btrfs_dev_replace_start()` resolves the source device, rejects active swapfile usage, commits current transaction to update device totals, creates target device, marks copy block groups, sets replace state to started, adds sysfs entry, waits ordered roots, commits the replace item, then runs scrub from offset 0 over the source device.
- After scrub, it calls `btrfs_dev_replace_finishing()`.
- Failure before scrub destroys the target replace device.

Ioctl entry:
- `btrfs_check_replace_dev_names()` validates nul-terminated source/target names.
- `btrfs_dev_replace_by_ioctl()` validates read-from-source mode, starts replacement, stores result, and maps normal/scrub-in-progress results to ioctl success.

Finishing:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount with `lock_finishing_cancel_unmount`.
- It verifies state is still started, flushes delalloc and waits ordered roots, then loops committing transactions until source device post-commit list is empty.
- It locks device list and chunk mutex to prevent super writes and new source allocations.
- On scrub success:
  - Updates target allocation state from source.
  - Rewrites mapping tree stripes from source device to target device.
  - Sets state finished, clears replacement pointers, swaps devids and UUIDs, transfers size/usage fields, updates active-device assignment, puts target on allocation list, increments rw device count, blocks bios, removes/free source, updates sysfs, scratches old superblocks, and commits superblock writeback.
- On scrub failure:
  - Sets state canceled, destroys target, unblocks bios, and returns the scrub error.

Mapping update:
- `btrfs_dev_replace_update_device_in_mapping_tree()` walks the chunk mapping rb tree under write lock and replaces stripe device pointers from source to target.
- `btrfs_set_target_alloc_state()` mirrors `CHUNK_ALLOCATED` bits from source to target extent state.

Status/progress:
- `btrfs_dev_replace_progress()` reports 0, 1000, or cursor-derived progress in thousandths.
- `btrfs_dev_replace_status()` fills ioctl status fields from in-memory state.

Cancel/suspend/resume:
- `btrfs_dev_replace_cancel()` rejects read-only mounts, handles not-started states, cancels active scrub for started state, or performs direct cleanup for suspended state.
- `btrfs_dev_replace_suspend_for_unmount()` changes started state to suspended and marks item writeback.
- `btrfs_resume_dev_replace_async()` resumes started/suspended replacements, verifies target block device exists, starts an exclusive dev-replace op, and spawns `btrfs-devrepl`.
- `btrfs_dev_replace_kthread()` resumes scrub from `committed_cursor_left`, then finishes replacement and releases exclusive op.

Ongoing/bio coordination:
- `btrfs_dev_replace_is_ongoing()` treats started and suspended states as ongoing even with missing target.
- `btrfs_rm_dev_replace_blocked()` sets filesystem replace state and waits for the percpu bio counter to drain.
- `btrfs_rm_dev_replace_unblocked()` clears the state and wakes waiters.
- `btrfs_bio_counter_sub()` subtracts bio counter and wakes waiters.
- `btrfs_bio_counter_inc_blocked()` increments unless replacement removal is blocking; if blocked, it waits and retries.

Important locking:
- `dev_replace->rwsem` protects mutable replace state.
- `lock_finishing_cancel_unmount` serializes finish, cancel, and unmount suspension.
- `device_list_mutex` and `chunk_mutex` protect device list and chunk allocation/mapping consistency during final swap.
- `mapping_tree_lock` protects chunk map updates.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.h

This header exports the Btrfs device replacement API.

Declared operations:
- Lifecycle/state:
  - `btrfs_init_dev_replace()`
  - `btrfs_run_dev_replace()`
  - `btrfs_dev_replace_is_ongoing()`
- User operations:
  - `btrfs_dev_replace_by_ioctl()`
  - `btrfs_dev_replace_status()`
  - `btrfs_dev_replace_cancel()`
- Mount/unmount/resume:
  - `btrfs_dev_replace_suspend_for_unmount()`
  - `btrfs_resume_dev_replace_async()`
- Zoned/block-group completion:
  - `btrfs_finish_block_group_to_copy()`
- Bio drain coordination:
  - `btrfs_bio_counter_inc_blocked()`
  - `btrfs_bio_counter_sub()`
  - Inline `btrfs_bio_counter_dec()` wrapper.

Design notes:
- Uses forward declarations for ioctl args, fs info, transaction handle, device replace state, block group, and device.
- Marks `btrfs_dev_replace_is_ongoing()` as `__pure`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dir-item.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision detection, matching, and deletion. It handles Btrfs’ packed directory item format, where multiple names with the same hash may share one tree item.

Insertion:
- `insert_with_overflow()` attempts `btrfs_insert_empty_item()`.
- On `-EEXIST`, it checks for an exact name collision inside the packed item; if absent, it extends the item and returns a pointer to the newly appended subitem.
- `btrfs_insert_xattr_item()` inserts an xattr item keyed by `BTRFS_XATTR_ITEM_KEY` and name hash, writes empty location key, flags `BTRFS_FT_XATTR`, name length, data length, transaction id, name, and value.
- It enforces `BTRFS_MAX_XATTR_SIZE()`.
- `btrfs_insert_dir_item()` inserts the name-hash `BTRFS_DIR_ITEM_KEY` entry and then, except in the tree root, queues the secondary `BTRFS_DIR_INDEX_KEY` insertion through delayed inode code.
- Encrypted directories OR in `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` does a tree search with mode-dependent insert length and COW flag, then scans the packed item for a matching name.
- `btrfs_lookup_dir_item()` looks up by directory objectid and name hash.
- `btrfs_lookup_dir_index_item()` looks up by directory objectid and explicit index offset.
- `btrfs_search_dir_index_item()` iterates all directory index items for a directory and returns the first matching name.
- `btrfs_lookup_xattr()` looks up xattr packed items by name hash.

Collision detection:
- `btrfs_check_dir_item_collision()` verifies whether inserting a name would collide exactly, overflow the leaf, or fit into an existing hash bucket.
- Returns:
  - `0` when safe.
  - `-EEXIST` for exact name match.
  - `-EOVERFLOW` when the packed item cannot fit another entry.
  - Other negative errors from lookup.

Packed item scanning:
- `btrfs_match_dir_item_name()` walks subitems inside the current tree item using each subitem’s name and data lengths.
- It compares name length and `memcmp_extent_buffer()` content.

Deletion:
- `btrfs_delete_one_dir_name()` deletes one packed dir/xattr subitem.
- If the subitem is the whole tree item, it deletes the item.
- Otherwise it memmoves the following bytes over the removed subitem and truncates the item.

Cross-file relationships:
- Secondary directory index insert/delete batching is in `delayed-inode.c`.
- Hashing helper is declared inline in `dir-item.h`.
- Uses Btrfs accessors for endian-safe item field reads/writes.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dir-item.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dir-item.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/dir-item.h

This header declares directory/xattr item helpers and defines the Btrfs name hash helper.

Exported operations:
- Collision and insertion:
  - `btrfs_check_dir_item_collision()`
  - `btrfs_insert_dir_item()`
  - `btrfs_insert_xattr_item()`
- Lookup:
  - `btrfs_lookup_dir_item()`
  - `btrfs_lookup_dir_index_item()`
  - `btrfs_search_dir_index_item()`
  - `btrfs_lookup_xattr()`
- Packed item helper:
  - `btrfs_match_dir_item_name()`
- Deletion:
  - `btrfs_delete_one_dir_name()`

Hashing:
- `btrfs_name_hash()` returns `crc32c((u32)~1, name, len)`.
- Directory and xattr primary keys use this hash in their key offset, with packed collision handling in `dir-item.c`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/dir-item.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/direct-io.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O on top of iomap. It handles extent locking, DIO mapping, COW/NOCOW decisions, ordered extents, direct bio submission, fallback to buffered I/O, and bioset lifecycle.

Private state:
- `struct btrfs_dio_data`
  - Tracks submitted bytes, qgroup/data reservation changeset, current ordered extent, whether data space was reserved, and whether NOCOW succeeded.
- `struct btrfs_dio_private`
  - Stores file offset/byte count for the bio and embeds `struct btrfs_bio`.
- `btrfs_dio_bioset`
  - Bioset used by iomap direct I/O.

Extent locking:
- `lock_extent_direct()` takes the direct I/O extent lock before the normal extent lock.
- It rejects NOWAIT if either lock would block.
- It checks for ordered extents and, for writes, pagecache pages in the range.
- For blocking DIO writes or DIO ordered extents it waits on ordered extents.
- It returns `-ENOTBLK` to force buffered fallback when it cannot safely proceed without deadlock.
- Reads avoid waiting on buffered ordered extents in some multi-extent cases to prevent page-lock deadlocks.

Direct write extent setup:
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates a direct ordered extent.
- `btrfs_new_extent_direct()` reserves a new extent for COW writes, handling zoned `-EAGAIN` by waiting for zone finish, then creates the DIO extent.
- `btrfs_get_blocks_direct_write()` decides between:
  - NOCOW for suitable existing extents.
  - PREALLOC ordered extent for preallocated extents.
  - COW allocation for everything else.
- NOCOW/PREALLOC reserve metadata only.
- COW requires prior data-space reservation, then metadata reservation and new extent allocation.
- It releases temporary outstanding extent reservation after ordered extent creation.
- It updates `i_size` under extent lock for extending writes.

Iomap begin:
- `btrfs_dio_iomap_begin()`:
  - Rejects large NOWAIT reads that could produce bad short-read behavior.
  - Caps read mapping length to checksum-array-friendly size.
  - Flushes compressed async extents when required.
  - Pre-reserves data space for blocking writes before locking the file range.
  - Locks direct and normal extent state.
  - Gets an extent map.
  - Falls back to buffered I/O for compressed or inline extents.
  - Rejects NOWAIT multi-extent ranges to avoid partial success surprises.
  - For writes, calls `btrfs_get_blocks_direct_write()`.
  - Translates extent map to iomap mapped/hole state.
  - Unlocks normal extent state before returning, while read DIO keeps the DIO lock until I/O completion.
  - Frees unused pre-reserved data space for short mappings or NOCOW.

Iomap end:
- `btrfs_dio_iomap_end()` unlocks holes for reads.
- If less was submitted than mapped, it finishes the unwritten part of write ordered extent as failed or unlocks read DIO extent, then returns `-ENOTBLK`.
- For writes it drops the ordered extent and frees the data reservation changeset.

Bio completion and submission:
- `btrfs_dio_end_io()` logs failed direct I/O, finishes write ordered extents on write completion, unlocks DIO extents on read completion, restores bio private data, then calls iomap completion.
- `btrfs_extract_ordered_extent()` splits ordered extents and extent maps for partial submitted writes; NOCOW skips extent map splitting.
- `btrfs_dio_submit_io()` initializes `btrfs_bio`, records submitted byte count, extracts/splits ordered extents for writes, and submits through `btrfs_submit_bbio()`.

Direct write entry:
- `btrfs_direct_write()`:
  - Uses NOWAIT try-locking when requested.
  - Uses shared inode lock for within-EOF writes when security bits do not need removal.
  - Falls back to buffered I/O for duplicated data profiles other than RAID0/SINGLE, because user buffers could mutate and diverge across mirrors/parity.
  - Runs generic write checks and Btrfs write checks.
  - Requires sectorsize-aligned offset and iov alignment.
  - Falls back to buffered I/O when data checksums are enabled, because user memory can change after checksum calculation.
  - Disables iov faults around iomap DIO to avoid self-deadlocks when the input buffer maps the same file range.
  - Retries after faulting in remaining pages; if no progress is made, falls back to buffered.
  - Buffered fallback writes, flushes and waits the written range, updates position, and invalidates pagecache so later DIO reads see persisted data.
  - NOWAIT buffered fallback returns `-EAGAIN`.

Direct read entry:
- `check_direct_read()` requires sectorsize alignment and rejects duplicate iovec base addresses.
- `btrfs_direct_read()` returns 0 if fsverity is active or checks fail, causing normal buffered handling by callers.
- It takes shared inode lock, disables page faults and iov faults around iomap DIO, retries after faulting destination pages, and returns completed read bytes.
- Fault handling is designed to avoid deadlocks on Btrfs extent locks held until read bio completion.

Alignment:
- `check_direct_IO()` requires offset and iov alignment to `fs_info->sectorsize`.

Bioset lifecycle:
- `btrfs_init_dio()` initializes `btrfs_dio_bioset`.
- `btrfs_destroy_dio()` exits the bioset.

Cross-file relationships:
- Uses delalloc reservation APIs from `delalloc-space.c`.
- Uses ordered extent lifecycle from `ordered-data.h`.
- Submits through Btrfs bio/volume mapping code.
- Relies on extent maps, COW/NOCOW checks, and transaction/block reservation helpers elsewhere in Btrfs.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/direct-io.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/direct-io.h

This header exposes Btrfs direct I/O lifecycle and read/write entry points.

Declared API:
- `btrfs_init_dio()` initializes the direct-I/O bioset.
- `btrfs_destroy_dio()` destroys the bioset.
- `btrfs_direct_write()` handles direct write requests and buffered fallback.
- `btrfs_direct_read()` handles direct read requests and signals fallback by returning 0 in unsupported cases.

Design notes:
- Only forward declares `struct kiocb`; the iov iterator type is used in prototypes through included kernel headers.
- The implementation details are kept private in `direct-io.c`, including iomap ops, bio private state, and locking behavior.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/direct-io.h -->