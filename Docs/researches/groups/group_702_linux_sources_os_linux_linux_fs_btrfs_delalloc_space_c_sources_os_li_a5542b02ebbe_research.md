# Group Research: group_702_linux_sources_os_linux_linux_fs_btrfs_delalloc_space_c_sources_os_li_a5542b02ebbe

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delalloc-space.c -->
# File Research: sources/os/linux/linux/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation reservation accounting for data writes. It coordinates the data space reservation made before dirtying a range with the metadata and qgroup reservations needed later for file extent items, inode updates, and checksum items.

Core responsibilities:
- Reserve and release data bytes in the correct `btrfs_space_info`, including a zoned data-relocation subgroup special case.
- Keep qgroup data reservations synchronized with data-space reservations through `extent_changeset`.
- Maintain per-inode metadata reservations in `inode->block_rsv`.
- Track `inode->outstanding_extents` and `inode->csum_bytes` so the inode block reserve reflects worst-case pending metadata.
- Provide combined delalloc reserve/release helpers used by buffered and direct write paths.

Key mechanisms:
- `data_sinfo_for_inode()` chooses normal data space info unless a zoned data relocation root must use `BTRFS_SUB_GROUP_DATA_RELOC`.
- `btrfs_alloc_data_chunk_ondemand()` aligns bytes to sectorsize and reserves data bytes with a normal data flush policy or the free-space-inode policy.
- `btrfs_check_data_free_space()` aligns the requested range, reserves data bytes, then reserves qgroup data; qgroup failure unwinds data reservation and frees the changeset.
- `btrfs_free_reserved_data_space_noquota()` releases only data `bytes_may_use`, for contexts where accurate qgroup reservation handling is inappropriate.
- `btrfs_free_reserved_data_space()` aligns the range, frees data reservation, and frees qgroup data reservation.
- `btrfs_calculate_inode_block_rsv_size()` recalculates the per-inode block reserve from outstanding extent count, one inode update, and checksum leaves unless `NODATASUM` is set.
- `calc_inode_reservations()` computes an upfront metadata and qgroup reservation for a write operation using `count_max_extents()` and checksum leaf estimates.
- `btrfs_delalloc_reserve_metadata()` performs qgroup metadata prealloc, reserves metadata bytes, updates inode counters under `inode->lock`, then adds bytes to the inode block reserve.
- `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, and `btrfs_delalloc_shrink_extents()` rebalance the counters and release excess reservations.
- `btrfs_delalloc_reserve_space()` and `btrfs_delalloc_release_space()` combine the data and metadata sides.

Important invariants:
- Reservation and release lengths are sectorsize aligned.
- Temporary outstanding extent reservations made by `btrfs_delalloc_reserve_metadata()` must later be released with `btrfs_delalloc_release_extents()` once delalloc or ordered extent accounting owns the range.
- `qgroup_free` selects whether metadata qgroup prealloc is freed as an error path or converted into transaction-scoped accounting for normal completion.
- Testing mode skips actual block reservation release in several metadata release helpers.

Cross-file relationships:
- Direct I/O write setup in `direct-io.c` calls these helpers when it needs COW, NOCOW, or prealloc ordered extents.
- The API is declared by `delalloc-space.h`.
- Reservation primitives come from block reserve, space info, qgroup, inode, and filesystem helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delalloc-space.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delalloc-space.h -->
# File Research: sources/os/linux/linux/fs/btrfs/delalloc-space.h

This header exposes the delayed allocation reservation API implemented by `delalloc-space.c`.

Exported API groups:
- Data reservation: `btrfs_alloc_data_chunk_ondemand()`, `btrfs_check_data_free_space()`, `btrfs_free_reserved_data_space()`, and `btrfs_free_reserved_data_space_noquota()`.
- Combined delalloc data and metadata reservation: `btrfs_delalloc_reserve_space()` and `btrfs_delalloc_release_space()`.
- Metadata reservation lifecycle: `btrfs_delalloc_reserve_metadata()`, `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, and `btrfs_delalloc_shrink_extents()`.

Design notes:
- The header forward declares the small set of Btrfs and extent state types needed by callers.
- Qgroup range tracking is explicit: callers pass `struct extent_changeset **reserved` when reserving and the resulting `struct extent_changeset *reserved` when releasing.
- `btrfs_delalloc_reserve_metadata()` accepts logical and disk byte counts separately, which matters for callers whose on-disk size may differ from the dirty logical range.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delalloc-space.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-inode.c -->
# File Research: sources/os/linux/linux/fs/btrfs/delayed-inode.c

This file implements Btrfs delayed inode and delayed directory index handling. It batches inode item updates, inode ref deletion, and directory index insert/delete records so metadata changes can be flushed later under transaction context or by async workers.

Core data model:
- `btrfs_delayed_root` stores global delayed item counters, a node list, a prepared list, lock, and waitqueue.
- Each `btrfs_delayed_node` belongs to one inode/root pair and is cached both in the inode and in the root `delayed_nodes` xarray.
- A delayed node owns two cached rbtrees: `ins_root` for delayed directory index insertions and `del_root` for delayed deletions.
- `btrfs_delayed_item` stores a directory index offset, item type, refcount, list links for batch/readdir/logging paths, optional reserved bytes, and flexible inline item data.

Initialization and lifetime:
- `btrfs_delayed_inode_init()` and `btrfs_delayed_inode_exit()` manage the slab cache for delayed nodes.
- `btrfs_init_delayed_root()` initializes counters, list heads, lock, and waitqueue.
- `btrfs_get_delayed_node()` first tries the inode cache, then the root xarray, and handles races with final node removal via `refcount_inc_not_zero()`.
- `btrfs_get_or_create_delayed_node()` allocates a node, initializes it, reserves an xarray slot, and installs it if another task did not win the race.
- `btrfs_release_delayed_node()` requeues nodes with pending work, dequeues empty nodes, drops the caller reference, erases the xarray entry on final reference, and frees the node.

Delayed item operations:
- `__btrfs_add_delayed_item()` inserts an item into the insertion or deletion rbtree, updates the per-node count, and increments global delayed item count.
- `finish_one_item()` increments `items_seq`, decrements global item count, and wakes waiters when the background threshold or batch boundary is crossed.
- `btrfs_release_delayed_item()` removes the item from its rbtree if present and frees it when the refcount reaches zero.
- Insertions are batched by `btrfs_insert_delayed_item()` into a leaf-sized `btrfs_item_batch`; log replay restricts batching to continuous keys to preserve ordering.
- Deletions are batched by `btrfs_batch_delete_items()` when consecutive delayed deletion items match consecutive on-disk directory index items.

Metadata reservation:
- Delayed inode updates reserve one metadata update unit into `fs_info->delayed_block_rsv` and record it in `node->bytes_reserved`.
- Delayed deletion items reserve and store `item->bytes_reserved`.
- Delayed insertion items account by reserved leaves on the delayed node with `index_item_leaves` and `curr_index_batch_size`, because many items can share one leaf.
- `btrfs_release_dir_index_item_space()` returns unused transaction reservation when an insertion fits in an already-reserved delayed insertion leaf.

Flush and commit paths:
- `__btrfs_commit_inode_delayed_items()` inserts delayed index items, deletes delayed index items, records the root in the transaction, then updates the inode item.
- `__btrfs_update_delayed_inode()` writes the saved inode item and, when marked, deletes the final inode ref/extref.
- `btrfs_run_delayed_items()` and `btrfs_run_delayed_items_nr()` drain global delayed nodes with `fs_info->delayed_block_rsv` installed as the transaction block reserve.
- `btrfs_commit_inode_delayed_items()` flushes all delayed work for one inode.
- `btrfs_commit_inode_delayed_inode()` joins a transaction and commits only a dirty delayed inode item.

Directory integration:
- `btrfs_insert_delayed_dir_index()` builds an inline `btrfs_dir_item`, adds it to the insertion rbtree, and updates delayed leaf reservation accounting.
- `btrfs_delete_delayed_dir_index()` first removes a matching unflushed insertion; if none exists, it queues a delayed deletion item.
- `btrfs_inode_delayed_dir_index_count()` copies the delayed node index counter back to the inode.
- Readdir helpers collect insertion/deletion items up to a target index, emit delayed insertions with `dir_emit()`, suppress deleted on-disk indexes, and release temporary refs afterward.
- Directory logging helpers collect delayed items into log lists, skip already logged/listed entries, and mark them logged when the log path is done.

Async balancing and cleanup:
- Delayed item thresholds are `BTRFS_DELAYED_BACKGROUND` 128, `BTRFS_DELAYED_WRITEBACK` 512, and `BTRFS_DELAYED_BATCH` 16.
- `btrfs_balance_delayed_items()` queues async worker flushes and may wait when the writeback threshold is exceeded.
- `btrfs_async_run_delayed_root()` drains prepared delayed nodes from a workqueue by joining transactions.
- Cleanup helpers kill delayed items for one inode, one root, all roots, or filesystem shutdown, releasing metadata reservations and qgroup prealloc as appropriate.

Important locking:
- The root delayed node lists use `delayed_root->lock`.
- Per-node dirty inode state and rbtrees use `delayed_node->mutex`.
- The root xarray uses xarray locking.
- The code deliberately releases btree paths before releasing delayed nodes to avoid lock ordering deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-inode.h -->
# File Research: sources/os/linux/linux/fs/btrfs/delayed-inode.h

This header defines the delayed inode and delayed directory item structures and exports their public API.

Key structures and flags:
- `enum btrfs_delayed_item_type` distinguishes delayed insertion and delayed deletion items.
- `struct btrfs_delayed_node` identifies an inode by `inode_id` and `root`, stores per-node counters and flags, owns insertion/deletion rbtrees, carries prepared/global list links, caches a stack-format inode item, and tracks delayed insertion leaf reservations.
- `struct btrfs_delayed_item` contains an rbtree node, directory index offset, batch/readdir/log list links, optional metadata reservation, parent delayed node, refcount, type, logged flag, data length, and flexible inline data.
- Node flags are `BTRFS_DELAYED_NODE_IN_LIST`, `BTRFS_DELAYED_NODE_INODE_DIRTY`, and `BTRFS_DELAYED_NODE_DEL_IREF`.

Exported functionality:
- Root/node lifecycle and cleanup: `btrfs_init_delayed_root()`, `btrfs_remove_delayed_node()`, `btrfs_kill_delayed_inode_items()`, `btrfs_kill_all_delayed_nodes()`, and `btrfs_destroy_delayed_inodes()`.
- Directory index staging: `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, and `btrfs_inode_delayed_dir_index_count()`.
- Flush and balance: `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_balance_delayed_items()`, and `btrfs_commit_inode_delayed_items()`.
- Inode item staging: `btrfs_delayed_update_inode()`, `btrfs_fill_inode()`, `btrfs_delayed_delete_inode_ref()`, and `btrfs_commit_inode_delayed_inode()`.
- Readdir helpers: delayed item collection, release, delete filtering, and delayed insertion emission.
- Directory logging helpers: `btrfs_log_get_delayed_items()` and `btrfs_log_put_delayed_items()`.
- Module lifecycle: `btrfs_delayed_inode_init()` and `btrfs_delayed_inode_exit()`.

Debug support:
- With `CONFIG_BTRFS_DEBUG`, delayed node references are tracked through `ref_tracker`.
- Without debug tracking, the helper functions compile to no-ops and return success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-ref.c -->
# File Research: sources/os/linux/linux/fs/btrfs/delayed-ref.c

This file implements delayed back reference tracking. Btrfs queues extent reference count changes and extent metadata operations in memory, then processes them later so btree modifications do not immediately recurse into extent-tree updates.

Core data model:
- A transaction’s `btrfs_delayed_ref_root` stores delayed ref heads in an xarray keyed by logical bytenr shifted by `sectorsize_bits`.
- Each `btrfs_delayed_ref_head` represents one extent, stores aggregate reference modification counts, and owns an rbtree of individual delayed ref nodes.
- Individual refs are ordered by ref type, root/parent identity, data ref fields, and sequence number.
- Add refs are also linked in `head->ref_add_list` so additions can be selected before drops, avoiding premature extent item deletion.
- Qgroup dirty extent records are tracked in `delayed_refs->dirty_extents`.

Reservation accounting:
- `btrfs_check_space_for_delayed_refs()` checks whether delayed refs pressure exceeds delayed refs plus global reserve.
- `btrfs_delayed_refs_rsv_release()` releases metadata reserve units for delayed refs and checksum deletions.
- `btrfs_update_delayed_refs_rsv()` transfers pending transaction delayed-ref and csum-deletion accounting into `fs_info->delayed_refs_rsv`, preferentially consuming bytes already held in the transaction local delayed reserve.
- Block group insert/update helpers adjust delayed refs reserve size for block group item maintenance.
- `btrfs_delayed_refs_rsv_refill()` refills the reserve up to one delayed-ref metadata unit at a time and releases excess bytes if another task raced and filled it first.
- Zoned filesystems use `btrfs_zoned_cap_metadata_reservation()` to avoid letting delayed refs reserve exceed half of usable metadata space.

Merging and selection:
- `comp_refs()` and related helpers compare delayed refs for ordering and merge eligibility.
- `insert_delayed_ref()` inserts a new ref into a head rbtree or merges it with an equivalent existing ref, cancelling opposite actions when ref counts balance to zero.
- `btrfs_merge_delayed_refs()` performs additional metadata ref merging while respecting the tree mod log’s lowest sequence.
- `btrfs_select_ref_head()` finds the next unprocessed head, marks it processing, advances `run_delayed_start`, and locks the head safely even if the spinlock must be dropped.
- `btrfs_unselect_ref_head()` clears processing state and restores readiness.
- `btrfs_select_delayed_ref()` chooses add refs before other refs for a head.

Adding refs:
- `init_delayed_ref_head()` initializes aggregate head state, including `must_insert_reserved`, data/system flags, owning root, csum deletion tracking basis, and qgroup record fields.
- `add_delayed_ref_head()` inserts or updates the xarray head, traces qgroup extents, maintains `num_heads` and `num_heads_ready`, and accounts pending csum deletion reservations.
- `init_delayed_ref_common()` initializes an individual ref node and captures a tree-mod sequence for filesystem tree refs.
- `btrfs_init_tree_ref()` and `btrfs_init_data_ref()` populate generic ref fields and decide whether qgroup accounting can be skipped.
- `btrfs_add_delayed_tree_ref()` and `btrfs_add_delayed_data_ref()` allocate and queue metadata or data refs.
- `btrfs_add_delayed_extent_op()` attaches or merges an extent operation into the delayed ref head without adding a normal ref node.

Lookup and destruction:
- `btrfs_find_delayed_ref_head()` looks up a head under delayed refs lock.
- `btrfs_find_delayed_tree_ref()` searches a head for an add reference matching a root or parent.
- `btrfs_destroy_delayed_refs()` drains all heads during transaction cleanup/abort, drops all refs, frees delayed extent ops, deletes heads from the xarray, pins reserved extents when needed, performs ref-head accounting cleanup, and destroys qgroup extent records.

Important invariants:
- Head xarray indexes are sector-shifted to be dense and workable on 32-bit platforms.
- A head’s `total_ref_mod` is not decremented as refs run; it records the total modification needed for qgroup/checksum accounting decisions.
- A head’s `ref_mod` is adjusted as refs run so on-disk reference count plus outstanding modifications remains meaningful.
- Add refs must be processed before drop refs for the same head to avoid deleting extent items that later additions still need.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-ref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-ref.h -->
# File Research: sources/os/linux/linux/fs/btrfs/delayed-ref.h

This header defines delayed back reference data structures, reservation helpers, and the public delayed-ref API.

Key types:
- `enum btrfs_delayed_ref_action` defines add, drop, new extent allocation, and head update actions.
- `struct btrfs_data_ref` stores the inode objectid and adjusted file offset for data extent refs.
- `struct btrfs_tree_ref` stores tree block level for metadata refs.
- `struct btrfs_delayed_ref_node` is one queued reference operation, with rb/list links, bytenr, size, sequence, root/parent identity, refcount, ref modification count, action, ref item type, and data/tree ref payload.
- `struct btrfs_delayed_extent_op` stores delayed extent item key/flag updates.
- `struct btrfs_delayed_ref_head` aggregates all pending changes for one extent, owns a lock, rbtree, add list, extent op, ref modification counters, reservation state, block group type flags, and processing/tracking booleans.
- `struct btrfs_delayed_ref_root` stores transaction-wide head and qgroup dirty extent xarrays, counters, pending csum bytes, run cursor, flags, and qgroup skip root.
- `struct btrfs_ref` is the generic input representation used to queue data or metadata delayed refs.

Inline helpers:
- `btrfs_calc_delayed_ref_bytes()` estimates metadata reservation for delayed refs and doubles it when the free space tree is active.
- `btrfs_calc_delayed_ref_csum_bytes()` estimates metadata needed to delete checksum items.
- `btrfs_alloc_delayed_extent_op()` and `btrfs_free_delayed_extent_op()` wrap the extent op slab cache.
- `btrfs_put_delayed_ref_head()` and `btrfs_put_delayed_ref()` handle refcounted delayed ref object release.
- `btrfs_ref_head_to_space_flags()` maps a delayed ref head to data, system, or metadata block group flags.
- `btrfs_delayed_ref_owner()` and `btrfs_delayed_ref_offset()` expose owner/offset interpretation based on ref item type.
- `btrfs_ref_type()` maps generic data/metadata refs with or without parent pointers to the correct on-disk ref item type.

Exported API:
- Slab lifecycle: `btrfs_delayed_ref_init()` and `btrfs_delayed_ref_exit()`.
- Generic ref initialization: `btrfs_init_tree_ref()` and `btrfs_init_data_ref()`.
- Queueing: `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, and `btrfs_add_delayed_extent_op()`.
- Merge/select/run support: `btrfs_merge_delayed_refs()`, `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_delete_ref_head()`, and `btrfs_find_delayed_ref_head()`.
- Reservation management: `btrfs_delayed_refs_rsv_release()`, `btrfs_update_delayed_refs_rsv()`, block group insert/update accounting helpers, `btrfs_delayed_refs_rsv_refill()`, and `btrfs_check_space_for_delayed_refs()`.
- Lookup/cleanup: `btrfs_find_delayed_tree_ref()` and `btrfs_destroy_delayed_refs()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/delayed-ref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dev-replace.c -->
# File Research: sources/os/linux/linux/fs/btrfs/dev-replace.c

This file implements Btrfs online device replacement. Replacement keeps the filesystem writable by duplicating new writes to both source and target while scrub copies already-existing extents from the source to the target, then the finishing path swaps device identities and mapping references.

On-disk state and mount initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device tree.
- Missing or malformed replace state is tolerated only when no replace target device is present.
- Active `STARTED` or `SUSPENDED` state reconnects source and target devices by devid, sets replace target flags, and initializes target geometry from the source when possible.
- Missing source or target devices cause mount failure unless the filesystem is mounted degraded.

Starting replacement:
- `btrfs_dev_replace_by_ioctl()` validates ioctl options and device-name termination before calling `btrfs_dev_replace_start()`.
- `btrfs_dev_replace_start()` locates the source device, rejects active swapfile use, commits any current transaction so device size accounting is current, initializes the target device, and marks zoned block groups for copying when needed.
- `btrfs_init_dev_replace_tgtdev()` opens the target block device writable, validates zoned compatibility, rejects a target already in the filesystem, checks it is not smaller than the source, allocates a Btrfs device object, initializes device fields, attaches zone info, and links it into the fs devices list.
- Once state is switched to `STARTED`, new writes are duplicated by the volume mapping layer.
- The code waits for ordered roots, commits the replace item to disk, then starts `btrfs_scrub_dev()` over the source device with the replace flag set.

Zoned handling:
- `mark_block_group_to_copy()` scans committed device extents for the source device and marks corresponding block groups with `BLOCK_GROUP_FLAG_TO_COPY`.
- `btrfs_finish_block_group_to_copy()` clears that flag only after the last stripe on the source device for a block group has been copied.
- This protects against unsafe NOCOW writes while replace is copying committed extents on zoned filesystems.

Persisting replace state:
- `btrfs_run_dev_replace()` is called from transaction commit when `item_needs_writeback` is set.
- It creates or updates the device replace item with source devid, read mode, state, timestamps, error counters, and copy cursors.
- It handles too-small legacy/corrupt items by deleting and reinserting a correctly sized item.

Finishing:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount, flushes delalloc and ordered roots, commits until source-device post-commit work is drained, then blocks new bios while the source and target are swapped.
- On success it copies allocation state to the target, updates the mapping tree to replace source device pointers with target device pointers, swaps devids and UUIDs, moves allocation-list membership, updates active device selection, removes the old source device, updates sysfs, scratches old superblocks, commits final superblock state, and frees the old source device.
- On scrub failure or cancellation it marks the replace canceled and destroys the target device.

Status, cancel, suspend, and resume:
- `btrfs_dev_replace_progress()` reports progress in thousandths from the copy cursor and source size.
- `btrfs_dev_replace_status()` fills ioctl status fields under the replace rwsem.
- `btrfs_dev_replace_cancel()` handles active and suspended cancellation. Active cancellation asks scrub to cancel and lets finishing cleanup run; suspended cancellation performs cleanup directly.
- `btrfs_dev_replace_suspend_for_unmount()` changes `STARTED` to `SUSPENDED` and marks the replace item dirty.
- `btrfs_resume_dev_replace_async()` resumes `STARTED` or `SUSPENDED` replacement, validates the target, starts the exclusive device replace operation, and launches `btrfs_dev_replace_kthread()`.
- The kthread restarts scrub from `committed_cursor_left`, runs finishing, and ends the exclusive operation.

Bio quiescing:
- `btrfs_bio_counter_inc_blocked()` increments the replace bio counter but waits if `BTRFS_FS_STATE_DEV_REPLACING` is set.
- `btrfs_bio_counter_sub()` decrements and wakes waiters.
- Finishing uses these counters to wait for in-flight bios before removing/swapping devices.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dev-replace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dev-replace.h -->
# File Research: sources/os/linux/linux/fs/btrfs/dev-replace.h

This header declares the public device replacement API.

Exported operations:
- Initialization and transaction writeback: `btrfs_init_dev_replace()` and `btrfs_run_dev_replace()`.
- Ioctl entry points: `btrfs_dev_replace_by_ioctl()`, `btrfs_dev_replace_status()`, and `btrfs_dev_replace_cancel()`.
- Mount/unmount lifecycle: `btrfs_dev_replace_suspend_for_unmount()` and `btrfs_resume_dev_replace_async()`.
- State query: `btrfs_dev_replace_is_ongoing()`.
- Zoned/block-group support: `btrfs_finish_block_group_to_copy()`.
- Bio quiescing helpers: `btrfs_bio_counter_inc_blocked()`, `btrfs_bio_counter_sub()`, and inline `btrfs_bio_counter_dec()`.

Design notes:
- The header forward declares ioctl, filesystem, transaction, replace, block group, and device structures to keep dependencies narrow.
- The `__pure` attribute on `btrfs_dev_replace_is_ongoing()` indicates the query depends only on the passed replace structure state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dev-replace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dir-item.c -->
# File Research: sources/os/linux/linux/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision detection, name matching, and deletion. Btrfs stores name-hashed directory and xattr items that may contain multiple packed entries when names collide on the hash.

Insertion:
- `insert_with_overflow()` inserts an empty item for a key or, on `-EEXIST`, checks for an exact name match and extends the existing item to append another packed entry.
- `btrfs_insert_xattr_item()` validates xattr size, builds a `BTRFS_XATTR_ITEM_KEY` using `btrfs_name_hash()`, inserts/extends the item, initializes the embedded `btrfs_dir_item`, and copies name/data payloads.
- `btrfs_insert_dir_item()` inserts the name-hash `BTRFS_DIR_ITEM_KEY` entry and then queues the directory index entry through `btrfs_insert_delayed_dir_index()` unless operating on the tree root.
- Encrypted directories mark the file type with `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` wraps `btrfs_search_slot()` with mode-dependent insertion/deletion parameters and calls `btrfs_match_dir_item_name()`.
- `btrfs_lookup_dir_item()` searches the hash-keyed directory item and returns NULL for not found.
- `btrfs_lookup_dir_index_item()` searches a specific `BTRFS_DIR_INDEX_KEY` by index and name.
- `btrfs_search_dir_index_item()` scans directory index items from offset zero until it finds a matching name or leaves the directory index key range.
- `btrfs_lookup_xattr()` searches hash-keyed xattr items.

Collision and packed-entry handling:
- `btrfs_check_dir_item_collision()` detects exact name existence and checks whether a hash-collision entry can fit into the existing leaf item; if not, it returns `-EOVERFLOW`.
- `btrfs_match_dir_item_name()` walks all packed `btrfs_dir_item` records inside a single item, comparing name length and name bytes from the extent buffer.
- `btrfs_delete_one_dir_name()` deletes either the whole item when it contains only one entry or compacts the item by memmoving later packed entries over the deleted entry and truncating the item.

Cross-file relationships:
- Delayed directory index insertion is implemented in `delayed-inode.c`.
- The public declarations and `btrfs_name_hash()` inline helper live in `dir-item.h`.
- Callers depend on transaction, ctree, extent buffer, fscrypt string, and accessor helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dir-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dir-item.h -->
# File Research: sources/os/linux/linux/fs/btrfs/dir-item.h

This header declares Btrfs directory item and xattr item helpers and defines the directory name hash helper.

Exported operations:
- Directory insertion: `btrfs_insert_dir_item()`.
- Directory lookup: `btrfs_lookup_dir_item()`, `btrfs_lookup_dir_index_item()`, and `btrfs_search_dir_index_item()`.
- Collision detection: `btrfs_check_dir_item_collision()`.
- Name matching and deletion inside packed items: `btrfs_match_dir_item_name()` and `btrfs_delete_one_dir_name()`.
- Xattr item insertion and lookup: `btrfs_insert_xattr_item()` and `btrfs_lookup_xattr()`.

Hashing:
- `btrfs_name_hash()` computes a CRC32C hash seeded with `~1`, used for hash-keyed `BTRFS_DIR_ITEM_KEY` and `BTRFS_XATTR_ITEM_KEY` offsets.

Design notes:
- The API accepts `struct fscrypt_str` for directory names so encrypted-name handling can be passed through the same lookup/insert paths.
- `mod` parameters on lookup declarations encode read-only, modification, or deletion slot-search behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/dir-item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/direct-io.c -->
# File Research: sources/os/linux/linux/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O using iomap. It bridges iomap callbacks with Btrfs extent maps, ordered extents, data/metadata reservation, NOCOW/prealloc handling, checksum constraints, page-cache invalidation, and completion cleanup.

Core structures:
- `btrfs_dio_data` is per-iomap-iteration state: submitted byte count, qgroup/data reservation changeset, active ordered extent, data-space-reserved flag, and NOCOW completion flag.
- `btrfs_dio_private` extends `btrfs_bio` with file offset and byte count for completion.
- `btrfs_dio_bioset` backs allocation of direct I/O bios.

Range locking and extent preparation:
- `lock_extent_direct()` takes the DIO extent lock before the normal extent lock, rejects or waits on overlapping ordered extents, and prevents stale page-cache interactions. NOWAIT paths return `-EAGAIN` instead of blocking.
- Direct reads avoid waiting on buffered ordered extents in cases that could deadlock with buffered writers.
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates an ordered extent tagged as direct I/O.
- `btrfs_new_extent_direct()` reserves a new COW extent, handles zoned `-EAGAIN` by waiting for zone finish, creates the DIO extent, and frees reserved extents on failure.
- `btrfs_get_blocks_direct_write()` decides between NOCOW, prealloc, and COW. It reserves metadata for NOCOW/prealloc, requires previously reserved data space for COW, creates ordered extents, releases temporary outstanding extent reservations, and updates i_size under the extent lock.

Iomap callbacks:
- `btrfs_dio_iomap_begin()` caps read size for checksum memory, flushes async compressed extents when needed, optionally reserves data space before locking, locks the target range, loads an extent map, and rejects compressed or inline extents to buffered I/O.
- NOWAIT requests avoid multi-extent partial I/O and return `-EAGAIN` where blocking or unsafe short I/O could occur.
- For writes, the begin callback calls `btrfs_get_blocks_direct_write()` and releases unused data reservation for NOCOW or shorter-than-requested COW mappings.
- It translates extent maps into iomap mapped or hole entries and unlocks the correct extent bits.
- `btrfs_dio_iomap_end()` unlocks holes for reads, completes/cancels unwritten write tail ranges, drops ordered extent refs, and frees data reservation changesets.

Bio submission and completion:
- `btrfs_dio_submit_io()` initializes the Btrfs bio, records submitted bytes, splits ordered extents for partial write bios, and submits with `btrfs_submit_bbio()`.
- `btrfs_extract_ordered_extent()` splits extent maps and ordered extents so each submitted write bio has a matching ordered extent, except NOCOW writes do not split the existing extent map.
- `btrfs_dio_end_io()` warns on bio errors, finishes ordered extents for writes, unlocks DIO ranges for reads, restores bio private data, and hands completion back to iomap.

Direct write behavior:
- `btrfs_direct_write()` uses shared inode locking for within-EOF writes when security bits allow it, otherwise exclusive locking.
- True direct write is allowed only for SINGLE or RAID0 data profiles because duplicated profiles could observe changing userspace buffers differently across mirrors.
- Unaligned I/O, checksummed inodes, compressed/inline extents, unsafe NOWAIT cases, or other fallback triggers use buffered I/O.
- For direct writes, the iov iterator is marked nofault and retried after explicit fault-in to avoid deadlocks when writing from mmaped ranges of the same file.
- Buffered fallback writes data, forces and waits writeback for the written range, advances `ki_pos`, and invalidates page cache so subsequent direct reads see persisted data.

Direct read behavior:
- `btrfs_direct_read()` returns 0 when fsverity is active or direct read validation fails, allowing higher layers to use buffered read behavior.
- `check_direct_read()` enforces sectorsize alignment and rejects duplicate iovec base pointers.
- Reads use shared inode locking, disable page faults, set iterator nofault, retry after fault-in when progress is made, and avoid long retry loops by returning accumulated read bytes when progress stalls.

Lifecycle:
- `btrfs_init_dio()` initializes the bioset with space for embedded `btrfs_dio_private`.
- `btrfs_destroy_dio()` exits the bioset.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/direct-io.h -->
# File Research: sources/os/linux/linux/fs/btrfs/direct-io.h

This header declares the Btrfs direct I/O entry points and bioset lifecycle.

Exported API:
- `btrfs_init_dio()` initializes direct I/O bio allocation state.
- `btrfs_destroy_dio()` releases direct I/O bio allocation state.
- `btrfs_direct_write()` handles direct write requests from the file write path, with buffered fallback where required.
- `btrfs_direct_read()` handles direct read requests from the file read path, with validation behavior that lets callers fall back when direct I/O is unsuitable.

Design notes:
- The header forward declares `struct kiocb`; `struct iov_iter` is referenced by the prototypes through kernel headers included by translation units using this header.
- The implementation depends on iomap, Btrfs ordered extents, Btrfs bios, and delalloc reservation helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/direct-io.h -->