# subset-b-005610 Research

Grouped source research for Btrfs delayed allocation space accounting, delayed inode items, delayed refs, device replace, directory items, and direct I/O. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.c

## Purpose

`delalloc-space.c` implements Btrfs delayed-allocation reservation accounting for buffered writes, preallocation, and direct I/O. It separates data space reservation from metadata reservation: data writes first charge `space_info->bytes_may_use`, later real extent allocation moves accounting to reserved/used bytes, and ordered extent completion plus delayed refs finish persistence. Metadata reservations are tracked per inode through `inode->block_rsv`, `outstanding_extents`, and `csum_bytes`, so the filesystem can reserve enough tree space for file extent items, checksum items, and inode updates before dirty ranges are actually materialized.

## Important APIs, Types, and Functions

Public entry points are `btrfs_alloc_data_chunk_ondemand()`, `btrfs_check_data_free_space()`, `btrfs_free_reserved_data_space_noquota()`, `btrfs_free_reserved_data_space()`, `btrfs_delalloc_reserve_metadata()`, `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, `btrfs_delalloc_shrink_extents()`, `btrfs_delalloc_reserve_space()`, and `btrfs_delalloc_release_space()`.

Important helpers include `data_sinfo_for_inode()`, which chooses the normal data space-info or the zoned data-relocation subgroup, `btrfs_inode_rsv_release()`, which releases excess inode block reservation and qgroup reservation, `btrfs_calculate_inode_block_rsv_size()`, which recalculates per-inode metadata and qgroup reservation targets, and `calc_inode_reservations()`, which computes the immediate reservation for a new range.

## Control Flow

The combined reservation flow is `btrfs_delalloc_reserve_space()`: reserve data bytes through `btrfs_check_data_free_space()`, reserve qgroup data for the exact changed extent set, then reserve metadata with `btrfs_delalloc_reserve_metadata()`. Metadata reservation aligns byte counts, computes maximum extent/checksum leaves, preallocates qgroup metadata, reserves metadata bytes with an appropriate flush policy, updates `outstanding_extents` and `csum_bytes` under `inode->lock`, recalculates `inode->block_rsv`, and finally adds bytes to the block reserve.

Release paths mirror the acquisition paths. `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the inode reserve, and releases/converts qgroup metadata depending on whether the caller is aborting or handing reservation to the transaction. `btrfs_delalloc_release_extents()` drops temporary outstanding extents once another state, such as delalloc or ordered extents, owns them. `btrfs_delalloc_release_space()` releases both metadata and data/qgroup reservations. `btrfs_delalloc_shrink_extents()` adjusts outstanding extent accounting if a previously reserved range shrinks.

## State and Persistence Behavior

The file owns no durable on-disk format directly. It manages in-memory accounting that enables later persistence through extent allocation, ordered extent completion, checksum insertion, inode item update, and delayed refs. Key mutable state is `space_info->bytes_may_use`, the inode block reserve size/reserved/qgroup fields, `inode->outstanding_extents`, `inode->csum_bytes`, qgroup preallocations, and extent-changeset records for accurate data quota release.

Reservation flush behavior depends on context. Free-space inodes and explicit no-flush paths use no-flush reservation to avoid commit recursion. Existing transactions use limited flush to reduce deadlock risk. Testing mode skips actual inode reserve release in some paths after updating logical counters.

## Dependencies and Integration Points

This file integrates with `block-rsv`, `space-info`, qgroups, inode accounting, delalloc extent-state hooks, ordered extent creation, direct I/O, and ENOSPC flushing. Direct I/O uses `btrfs_delalloc_reserve_metadata()` and `btrfs_delalloc_release_extents()` after it creates ordered extents. Buffered writes use the combined reserve/release APIs around setting and clearing delalloc bits.

## Risks and Edge Cases

Reservation sizes intentionally overestimate to avoid many inodes each holding partial reservations, but overestimation can temporarily pressure ENOSPC behavior. The data and qgroup ranges must stay sector-aligned and must match the `extent_changeset` passed back for release. `outstanding_extents` is lifecycle-based rather than simply dirty-range-based, so missed calls to release temporary extents or metadata can leak reservation; early calls can underreserve tree changes. Zoned relocation uses a special data subgroup and asserts the subgroup id. Qgroup free versus convert semantics are context sensitive and easy to misuse on error paths.

## Test Signals

Useful tests include buffered write ENOSPC and EDQUOT paths, O_DIRECT COW and NOCOW reservation/release paths, checksum and NODATASUM inode variants, shrink-after-partial-allocation behavior, free-space inode no-flush behavior, active-transaction flush-limit behavior, qgroup exact-range release, zoned data relocation reservations, and fault injection around metadata reservation after successful data reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.h

## Purpose

`delalloc-space.h` is the public Btrfs internal interface for delayed allocation data and metadata reservation helpers. It exposes the reservation, release, and adjustment operations implemented in `delalloc-space.c` to write paths, direct I/O, ordered extent handling, and extent-state cleanup code.

## Important APIs, Types, and Functions

The header forward declares `extent_changeset`, `btrfs_inode`, and `btrfs_fs_info`, includes Linux integer types, and declares the core API: data-only reservation/allocation helpers, data reservation release with and without qgroup accounting, full delalloc reserve/release helpers, metadata-only reserve/release helpers, extent-lifecycle release, and reserved-extent shrink adjustment.

## Control Flow

There is no executable control flow in this header. Its declarations encode the expected call patterns: callers either reserve data plus metadata with `btrfs_delalloc_reserve_space()` and release with `btrfs_delalloc_release_space()`, or they reserve pieces separately when direct I/O, preallocation, or lower-level cleanup needs finer control.

## State and Persistence Behavior

The header owns no state. The pointer types in its signatures show that callers must pass inode-owned reservation state and optional `extent_changeset` records so the implementation can account per-inode, per-space-info, and per-qgroup reservations.

## Dependencies and Integration Points

Integration points are Btrfs inode write paths, quota groups, direct I/O, ordered extents, extent-state hooks, and ENOSPC reservation logic. The header is intentionally narrow so most call sites do not need the implementation's block-reserve and space-info internals.

## Risks and Edge Cases

The API splits quota-aware and noquota releases; choosing the wrong release function can either leak qgroup reservation or free quota that was not accurately tracked. Metadata reservation and extent release are separate calls because `outstanding_extents` has staged ownership, so API users must follow the documented lifecycle.

## Test Signals

Compile coverage should catch signature drift across write/direct-I/O users. Behavioral coverage should verify balanced reserve/release calls for buffered writes, direct writes, partial writes, failed writes, qgroup-enabled filesystems, and NODATASUM inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.c

## Purpose

`delayed-inode.c` implements delayed inode and delayed directory-index item processing for Btrfs. Instead of immediately updating inode items and directory index items in the subvolume tree for every metadata change, it stores per-inode delayed nodes in memory, batches directory index insertions/deletions, defers inode item updates, and runs those delayed items synchronously during transaction commit or asynchronously through the delayed worker queue. This reduces tree churn for operations such as create, unlink, rename, chmod, timestamp updates, and directory logging.

## Important APIs, Types, and Functions

Initialization and root setup are `btrfs_delayed_inode_init()`, `btrfs_delayed_inode_exit()`, and `btrfs_init_delayed_root()`. Delayed-node lifetime is controlled by `btrfs_get_delayed_node()`, `btrfs_get_or_create_delayed_node()`, `btrfs_release_delayed_node()`, `btrfs_remove_delayed_node()`, and kill/destroy helpers. Public mutation APIs include `btrfs_insert_delayed_dir_index()`, `btrfs_delete_delayed_dir_index()`, `btrfs_delayed_update_inode()`, and `btrfs_delayed_delete_inode_ref()`.

Flush and balancing APIs are `btrfs_run_delayed_items()`, `btrfs_run_delayed_items_nr()`, `btrfs_commit_inode_delayed_items()`, `btrfs_commit_inode_delayed_inode()`, `btrfs_balance_delayed_items()`, and `btrfs_assert_delayed_root_empty()`. Readdir and log integration APIs are `btrfs_readdir_get_delayed_items()`, `btrfs_readdir_put_delayed_items()`, `btrfs_should_delete_dir_index()`, `btrfs_readdir_delayed_dir_index()`, `btrfs_log_get_delayed_items()`, and `btrfs_log_put_delayed_items()`.

## Control Flow

Delayed nodes are stored per root in `root->delayed_nodes` and linked into the filesystem-wide `delayed_root` lists when they contain pending work. Creating or retrieving a node uses an xarray and refcounts, with a cached pointer in `btrfs_inode->delayed_node`. Items are stored in per-node cached rbtrees: insertion items in `ins_root`, deletion items in `del_root`. The node mutex protects these rbtrees, item counts, inode item snapshots, and insertion leaf reservation counters.

Directory insertion builds a `btrfs_dir_item` in a flexible delayed item, inserts it in the insertion rbtree, and accounts delayed block-reserve space by predicted leaf batches. Directory deletion first removes a still-pending insertion if possible; otherwise it queues a deletion item and migrates metadata reservation. Flushing runs insertions before deletions, then records the root in the transaction and updates the delayed inode item.

Commit flow switches `trans->block_rsv` to `fs_info->delayed_block_rsv`, walks delayed nodes, calls `__btrfs_commit_inode_delayed_items()`, and releases nodes after dropping any btree path to avoid lock inversion. Async flow picks prepared nodes from `prepare_list`, joins a transaction, commits a bounded number of delayed items, and wakes waiters. `btrfs_balance_delayed_items()` starts work or waits when item counts exceed background/writeback thresholds.

Readdir collects delayed insert/delete items up to a last index, temporarily upgrades the directory inode lock from shared to exclusive because `item->readdir_list` supports one active delayed readdir collection, and later downgrades back. Directory logging collects unlogged delayed items into log lists, marks them logged on release, and avoids requeueing the delayed node.

## State and Persistence Behavior

Persistent effects are delayed until flush: directory index keys are inserted into or removed from the subvolume tree, inode items are overwritten with a stack snapshot of VFS/Btrfs inode state, and delayed inode refs may be removed. Before flush, state is memory-only in `btrfs_delayed_node` and `btrfs_delayed_item`, with reservations held in `fs_info->delayed_block_rsv`. `delayed_root.items` and `items_seq` drive wait/wakeup behavior and background throttling.

Metadata reservation is carefully attached to delayed items or nodes. Insertion items reserve by leaves through `index_item_leaves`; deletion items store per-item `bytes_reserved`; inode updates store `node->bytes_reserved` and convert or free qgroup preallocations depending on success/error cleanup. Log replay skips some reservation behavior and uses continuous-key-only insertion batches.

## Dependencies and Integration Points

This file depends on xarrays, rbtrees, list management, refcounts, mutexes, spinlocks, wait queues, workqueues, Btrfs transactions, btree path operations, inode-item accessors, qgroups, block reservations, delayed workers, directory item format, VFS inode fields, and tree logging. It integrates with `dir-item.c` for secondary directory index creation and with transaction commit to guarantee all delayed items become durable before commit completes.

## Risks and Edge Cases

The node lifetime model is complex: xarray references, inode cached references, list references, temporary callers, debug ref trackers, and zero-ref removal must stay balanced. Delayed item reservation accounting differs for insertion, deletion, inode update, log replay, and kill paths. Async workers intentionally ignore some errors and rely on transaction commit to retry and abort if needed. Readdir's lock upgrade/downgrade must pair with VFS expectations. Log collection must handle multiple tasks logging the same directory and avoid double-listing items. Inode ref deletion is only intended for single-link inodes and is disabled during log recovery.

## Test Signals

Strong tests include metadata-heavy create/unlink/rename workloads, forced transaction commits during delayed item accumulation, async delayed worker throttling, log replay with interleaved directory indexes, fsync logging of directories with concurrent logging tasks, readdir visibility of pending insertions and deletions, inode eviction with pending delayed nodes, kill-all on dead roots, qgroup enabled metadata accounting, ENOMEM/fault injection in node/item allocation, and lockdep coverage for path versus delayed-node mutex ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.h

## Purpose

`delayed-inode.h` defines the in-memory data structures and public internal API for Btrfs delayed inode and delayed directory-index processing. It is the contract between directory operations, inode update paths, readdir, tree logging, transaction commit, delayed worker scheduling, and delayed node cleanup.

## Important APIs, Types, and Functions

Key types are `enum btrfs_delayed_item_type`, `struct btrfs_delayed_node`, and `struct btrfs_delayed_item`. A delayed node identifies an inode, owns insertion/deletion rbtrees, tracks pending item count, delayed inode item snapshot, reservation bytes, directory index counters, prepared/list membership flags, leaf-reservation counters, and optional debug ref trackers. A delayed item stores an index key offset, list nodes for tree/readdir/log use, reserved bytes, parent node pointer, refcount, insertion/deletion type, logged state, data length, and flexible item payload.

The header declares APIs for delayed dir index insert/delete/count, running delayed items, balancing, committing inode-specific delayed state, removing or killing delayed nodes, filling an inode from delayed state, delayed inode ref deletion, readdir integration, logging integration, init/exit, and debugging assertions. It also defines debug ref-tracker wrappers that compile to no-ops without `CONFIG_BTRFS_DEBUG`.

## Control Flow

There is little executable logic beyond debug inline helpers. The type layout shows the expected flow: callers create delayed nodes, queue insertion/deletion items under a mutex, global delayed-root lists expose nodes to commit/worker code, readdir and logging temporarily pin item references, and cleanup drops items plus reservations.

## State and Persistence Behavior

All structures are in-memory staging state. Durability is achieved only when implementation code flushes the delayed items into the Btrfs tree inside a transaction. The header highlights which fields are protected by node mutexes, delayed-root spinlocks, and refcounts, and which list nodes are used by specific consumers.

## Dependencies and Integration Points

Dependencies include Linux rbtrees, spinlocks, mutexes, lists, wait queues, VFS fs types, atomic/refcount/ref-tracker facilities, and Btrfs ctree types. Integration points are Btrfs directory item operations, inode item update/read paths, transaction commit, async delayed workers, readdir, fsync tree logging, root teardown, and debugging leak detection.

## Risks and Edge Cases

The same delayed item has several list nodes with different ownership rules; using the wrong list or failing to take a reference can cause use-after-free. The delayed node flags encode list membership, dirty inode state, and delayed inode-ref deletion, so they must remain synchronized with `count` and `delayed_root.items`. Debug ref tracker wrappers are conditional, so production builds rely only on normal refcounts.

## Test Signals

Compile tests should cover both debug and non-debug configurations. Runtime signals include no delayed-root leaks after unmount, correct readdir/logging behavior with pending delayed items, balanced item counters after insert/delete cancellation, and no refcount warnings under inode eviction and dead-root cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.c

## Purpose

`delayed-ref.c` implements transaction-time delayed reference tracking for Btrfs extents. Instead of updating extent-tree backrefs immediately while modifying file or metadata trees, callers queue reference additions, drops, extent insert accounting, and delayed extent operations. The transaction later selects ref heads, merges compatible ref nodes, runs them in a safe order, and commits the resulting extent-tree, qgroup, checksum, and reservation accounting changes.

## Important APIs, Types, and Functions

Reservation APIs include `btrfs_check_space_for_delayed_refs()`, `btrfs_delayed_refs_rsv_release()`, `btrfs_update_delayed_refs_rsv()`, block-group insert/update reservation adjusters, and `btrfs_delayed_refs_rsv_refill()`. Core queue APIs are `btrfs_init_tree_ref()`, `btrfs_init_data_ref()`, `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, and `btrfs_add_delayed_extent_op()`.

Processing helpers include `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_delete_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_merge_delayed_refs()`, `btrfs_check_delayed_seq()`, `btrfs_find_delayed_ref_head()`, `btrfs_find_delayed_tree_ref()`, `btrfs_put_delayed_ref()`, and `btrfs_destroy_delayed_refs()`. Slab caches for heads, nodes, and extent operations are initialized and destroyed by `btrfs_delayed_ref_init()` and `btrfs_delayed_ref_exit()`.

## Control Flow

Adding a ref allocates a delayed ref node and head, optionally allocates/reserves a qgroup extent record, reserves xarray slots, initializes common fields, then inserts the head into `transaction->delayed_refs.head_refs` under the delayed refs spinlock. If a head already exists for the bytenr, `update_existing_head_ref()` merges aggregate counts, pending checksum-deletion accounting, owning root, `must_insert_reserved`, and delayed extent operations. The individual ref node is inserted into the head rbtree or merged with an equivalent node; add refs are also linked in `ref_add_list`.

Processing selects a head from the xarray starting at `run_delayed_start`, marks it processing, decrements ready counts, and locks the head mutex. Within a head, `btrfs_select_delayed_ref()` prefers add refs before drops so an extent item is not deleted before pending additions are applied. `btrfs_merge_delayed_refs()` merges compatible metadata refs when tree-mod-log sequence constraints allow it. After a head is fully processed, callers remove it with `btrfs_delete_ref_head()` and clean up accounting elsewhere.

Destruction during transaction abort walks all heads, locks each, drops all child refs, frees delayed extent ops, removes heads from the xarray, pins bytes for extents that had reserved insert accounting, performs cleanup accounting, and destroys qgroup extent records.

## State and Persistence Behavior

Delayed refs are in-memory transaction state. They represent future persistent changes to extent refs, extent item insertions, checksum item deletions, qgroup dirty extent records, and block-group reservation accounting. Persistent effects occur when the extent-tree processing code consumes selected refs before transaction commit. The file tracks reserve sizes in `fs_info->delayed_refs_rsv`, local transaction delayed reserves, `pending_csums`, `num_heads`, `num_heads_ready`, `run_delayed_start`, and per-head `ref_mod`/`total_ref_mod`.

## Dependencies and Integration Points

Dependencies include Btrfs transactions, extent-tree processing, qgroups, free-space-tree-aware reservation sizing, tree-mod-log sequence tracking, space-info accounting, block groups, xarrays, rbtrees, lists, spinlocks, mutexes, slab caches, and tracepoints. The qgroup integration records dirty extents when full accounting is enabled and can skip roots for snapshot accounting.

## Risks and Edge Cases

The xarray index is bytenr shifted by sectorsize bits; 32-bit builds reject delayed ref heads beyond the page-cache/xarray index limit. Ref merging must respect tree-mod-log sequence numbers or backref walking can observe wrong histories. Data refs are not aggressively merged because the code expects fewer of them. Pending csum deletion reservations depend on sign changes of aggregate data ref mods. Abort cleanup has to convert reserved extents into pinned bytes if they were never inserted. The lock order between delayed root spinlock, head mutex, and head spinlock is delicate, especially when `btrfs_delayed_ref_lock()` drops and reacquires the root lock.

## Test Signals

Useful validation includes snapshot/delete workloads with qgroups, heavy metadata churn that produces many merging tree refs, data extent drop paths that delete checksums, transaction abort after reserved extent insertion, 32-bit overflow coverage if supported, free-space-tree reservation sizing, zoned metadata reservation cap behavior, tree-mod-log backref walking concurrent with delayed refs, and slab allocation fault injection for head/node/qrecord allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.h

## Purpose

`delayed-ref.h` defines the Btrfs delayed reference data model and API used by transaction, extent-tree, qgroup, and backref code. It describes delayed ref actions, data and metadata ref identities, per-extent ref heads, the delayed-ref root, generic caller-facing ref descriptors, reservation helpers, and processing/lookup functions.

## Important APIs, Types, and Functions

Important types are `enum btrfs_delayed_ref_action`, `struct btrfs_data_ref`, `struct btrfs_tree_ref`, `struct btrfs_delayed_ref_node`, `struct btrfs_delayed_extent_op`, `struct btrfs_delayed_ref_head`, `struct btrfs_delayed_ref_root`, `enum btrfs_ref_type`, and `struct btrfs_ref`. Inline helpers include delayed ref byte calculations, delayed extent op allocation/free, delayed ref/head put helpers, space flag derivation, owner/offset extraction, and `btrfs_ref_type()`.

The header declares initialization/exit, tree/data ref initialization, delayed tree/data ref add, delayed extent op add, merge/select/delete/lookup helpers, delayed refs reservation helpers, space checks, tree-ref existence lookup, and transaction abort destruction.

## Control Flow

The header has inline allocation, release, and classification helpers, but no major runtime algorithm. The exported API separates caller-side generic refs from transaction-internal delayed ref nodes and heads. Callers initialize a `struct btrfs_ref`, fill data/tree-specific details, then queue it through the C implementation.

## State and Persistence Behavior

All state described here is transaction-local memory until delayed refs are processed. `btrfs_delayed_ref_head` aggregates ref count deltas and extent operation metadata for one bytenr. `btrfs_delayed_ref_root` tracks all heads and dirty qgroup extents in xarrays plus counters protected by its spinlock. Persistent extent-tree, checksum-tree, and qgroup effects are deferred.

## Dependencies and Integration Points

The header depends on Linux refcounts, lists, rbtrees, mutexes, spinlocks, slabs, UAPI Btrfs tree constants, and Btrfs fs/message types. It integrates with extent-tree code that consumes refs, transaction code that owns the delayed-ref root, qgroup tracing, free-space-tree reservation sizing, and tree-mod-log/backref lookup.

## Risks and Edge Cases

The structures have explicit lock ownership expectations that are not enforced by the type system. The same delayed ref action enum is used for additions, drops, extent insertion accounting, and head-only updates. `btrfs_delayed_ref_owner()` returns an inode for data refs but a tree level for metadata refs, so generic callers must understand the context. Reservation helper sizing doubles for free-space-tree updates, making mount-option state part of accounting behavior.

## Test Signals

Compile coverage should include qgroup, free-space-tree, and debug builds. Runtime tests should validate delayed ref selection order, qgroup dirty extent tracking, metadata versus data ref type selection, head lookup/removal, delayed extent op merging, and abort cleanup under allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.c

## Purpose

`dev-replace.c` implements Btrfs online device replacement. It copies existing extents from a source device to a target device using scrub infrastructure while new writes are duplicated to both source and target through the block mapping path. When copying finishes, it atomically updates in-memory chunk mappings and on-disk device replace state so the target assumes the source device identity and the old source is removed from active filesystem metadata.

## Important APIs, Types, and Functions

Mount/state APIs are `btrfs_init_dev_replace()` and `btrfs_run_dev_replace()`. User-facing control APIs are `btrfs_dev_replace_by_ioctl()`, `btrfs_dev_replace_status()`, `btrfs_dev_replace_cancel()`, `btrfs_dev_replace_suspend_for_unmount()`, and `btrfs_resume_dev_replace_async()`. Runtime helpers include `btrfs_init_dev_replace_tgtdev()`, `mark_block_group_to_copy()`, `btrfs_finish_block_group_to_copy()`, `btrfs_dev_replace_start()`, `btrfs_dev_replace_finishing()`, `btrfs_dev_replace_kthread()`, `btrfs_dev_replace_is_ongoing()`, `btrfs_bio_counter_sub()`, and `btrfs_bio_counter_inc_blocked()`.

Important finishing helpers include `btrfs_set_target_alloc_state()`, which copies chunk allocation state from source to target, and `btrfs_dev_replace_update_device_in_mapping_tree()`, which rewrites chunk-map stripes from source device pointers to target device pointers.

## Control Flow

Mount initialization reads the `BTRFS_DEV_REPLACE_KEY` item from the device root, validates item size, restores state, source/target devices, cursors, timestamps, and error counters, and rejects inconsistent cases such as a replace target without a valid active item unless degraded semantics allow cancellation.

Starting replacement resolves the source device, rejects active swapfile and seed filesystem cases, commits outstanding transactions to refresh committed sizes, opens and validates the target block device, checks zone type and capacity, adds a replacement target device with devid `BTRFS_DEV_REPLACE_DEVID`, optionally marks zoned block groups as `TO_COPY`, sets `replace_state` to started under `dev_replace->rwsem`, adds sysfs state, waits for ordered roots, commits the device replace item, and calls `btrfs_scrub_dev()` to copy source extents. Finishing then handles success or scrub error.

Finishing serializes against cancel/unmount, flushes all delalloc/ordered I/O, repeatedly commits transactions until the source has no post-commit device updates, locks the device list and chunk mutex, marks replace finished or canceled, updates mapping-tree stripes and target allocation state on success, swaps devids and UUIDs, moves allocation list membership, blocks new bios while removing the old source, updates sysfs, scratches old superblocks if writable, commits superblocks, and frees the old source device.

Cancel either asks scrub to cancel an active replacement and lets finishing clean up, or directly cancels suspended replacements by updating state, committing, and destroying the target. Resume turns suspended state back to started and launches `btrfs-devrepl` if no other exclusive operation is active. The bio counter blocks new bios during source/target removal and wakes waiters when safe.

## State and Persistence Behavior

Persistent state is the device replace item in the device tree, written by `btrfs_run_dev_replace()` during transaction commit. It stores source devid, read-from-source mode, replace state, start/stop times, write/read error counters, and copy cursors. In-memory state lives in `fs_info->dev_replace`: rwsem-protected source/target pointers, state, cursors, scrub progress, error counters, writeback flag, finishing/cancel mutex, replacement task, waitqueue, and per-cpu bio counter.

Replacement also mutates durable device identity by swapping devid/UUID fields and writing superblocks. The scrub copy covers committed extents while write duplication covers new writes after start. Zoned filesystems additionally keep block groups read-only until all source stripes are copied.

## Dependencies and Integration Points

This file integrates with the ioctl layer, device tree items, transaction commit, block device opening, volume/device list management, sysfs, scrub, async kthreads, exclusive-operation tracking, chunk mapping tree, block-group runtime flags, zoned device checks, ordered extent flushing, superblock writing, device stats, and the bio mapping path that duplicates writes during replacement.

## Risks and Edge Cases

The start/finish sequence has many cross-lock constraints: device list mutex, chunk mutex, mapping tree lock, dev_replace rwsem, and finish/cancel mutex must prevent new chunks, bios, or superblock writes from seeing half-swapped devices. Missing source/target devices during mount require degraded handling. Target validation must reject too-small devices, in-filesystem devices, zone mismatches, seed filesystems, and active swapfile sources. Scrub errors route to cancel cleanup; errors while updating target allocation state must destroy the target safely. Progress calculation divides by source size/1000 and assumes a valid nonzero source size while active.

## Test Signals

Validation should cover successful online replacement, cancel during active scrub, cancel of suspended replacement, resume after unmount/remount, missing source/target in degraded and non-degraded mounts, target too small/in filesystem/zone mismatch, scrub error cleanup, write duplication during replacement, direct/metadata writes while finishing, sysfs device replacement, superblock scratching, zoned `TO_COPY` block group handling, and bio counter blocking during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.h

## Purpose

`dev-replace.h` declares the internal Btrfs device-replacement API used by mount, transaction commit, ioctl handling, unmount, resume, block mapping, and bio accounting code.

## Important APIs, Types, and Functions

The header forward declares ioctl arguments, filesystem and transaction structures, device replace state, block groups, and devices. It declares initialization, transaction writeback, ioctl start, status, cancel, unmount suspend, async resume, ongoing-state query, zoned block-group copy completion, and bio counter helpers. It also provides `btrfs_bio_counter_dec()` as an inline wrapper around `btrfs_bio_counter_sub()`.

## Control Flow

There is no substantial executable control flow beyond the decrement inline. The API shape mirrors the replacement lifecycle: initialize from disk, start through ioctl, persist changes during transaction commit, report status, cancel/suspend/resume as lifecycle events require, and coordinate block I/O with replacement removal.

## State and Persistence Behavior

The header owns no state. It exposes functions that operate on `fs_info->dev_replace` and device tree persistent state. The bio counter helpers indicate that replacement finishing/removal synchronizes with in-flight bios.

## Dependencies and Integration Points

Integration points include ioctl definitions, transaction commit, device management, block group handling, unmount/remount paths, and low-level bio mapping. The `__pure` ongoing query can be used by fast paths that only inspect replacement state.

## Risks and Edge Cases

Callers must use the lifecycle APIs under the expected mount/exclusive-operation context; direct manipulation of `struct btrfs_dev_replace` would bypass locking and persistence. Bio counter increment/decrement must remain balanced or finishing can hang waiting for in-flight bios.

## Test Signals

Compile coverage should catch signature drift. Runtime tests should watch for balanced bio counters, correct state after mount/replay/resume, and proper interaction between ioctl operations and transaction writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dir-item.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/dir-item.c

## Purpose

`dir-item.c` implements Btrfs directory item and xattr item insertion, lookup, collision checking, name matching, and deletion. Btrfs stores names under hash keys; a single tree item can contain multiple `btrfs_dir_item` records when names hash to the same key, so the file includes overflow handling for extending existing items and scanning subitems by name.

## Important APIs, Types, and Functions

Public APIs are `btrfs_insert_xattr_item()`, `btrfs_insert_dir_item()`, `btrfs_lookup_dir_item()`, `btrfs_check_dir_item_collision()`, `btrfs_lookup_dir_index_item()`, `btrfs_search_dir_index_item()`, `btrfs_lookup_xattr()`, `btrfs_match_dir_item_name()`, and `btrfs_delete_one_dir_name()`. The key helper is `insert_with_overflow()`, which inserts an empty item or extends an existing hash-collision item after verifying no exact name match exists.

## Control Flow

Insertion builds a key from directory inode/xattr objectid, item type, and `btrfs_name_hash()`. Xattr insertion validates name plus data length against the filesystem xattr limit, inserts/extends the item, fills a zero location key and xattr flags, and writes name/data bytes. Directory insertion inserts the name-hash item, marks encrypted names with `BTRFS_FT_ENCRYPTED`, writes the pointed-to inode key and name, then queues the secondary `BTRFS_DIR_INDEX_KEY` through delayed inode code unless the root is the tree root.

Lookup uses `btrfs_search_slot()` through `btrfs_lookup_match_dir()`, then scans the item payload with `btrfs_match_dir_item_name()`. Collision checking returns success for no hash item, `-EEXIST` for an exact name, `-EOVERFLOW` if extending the hash-collision item would exceed leaf capacity, or an underlying search error. Directory index search can either look up an exact index/name pair or scan index items from offset zero until a matching name is found.

Deletion removes one subitem from a hash item. If the subitem length equals the whole item, it deletes the tree item. Otherwise it memmoves following subitems over the removed record and truncates the item.

## State and Persistence Behavior

This file directly mutates Btrfs tree leaves inside transactions. Directory hash items and xattr items are persistent on commit; secondary directory index insertions are queued as delayed items and persisted by delayed-inode flushing. No independent long-lived state is kept in this file.

## Dependencies and Integration Points

Dependencies include ctree search/insert/delete/truncate helpers, extent buffer accessors, transaction handles, disk key conversion, CRC32C name hashing, fscrypt name strings, delayed inode secondary index insertion, and Btrfs directory item accessors. It is used by inode operations, xattr code, lookup/unlink/rename, readdir, and logging paths.

## Risks and Edge Cases

Hash collisions require exact subitem scanning; callers must not treat a found key as a found name. Leaf capacity limits can return `-EOVERFLOW` even when the hash key exists. Directory insertion can have a primary insert result and a delayed-index insert result; collision on the primary name jumps to secondary insertion logic. Encrypted directories set a file-type flag in the directory item. Deletion pointer arithmetic must correctly compute subitem lengths including xattr data payloads.

## Test Signals

Tests should include colliding names, xattrs near maximum size, duplicate directory names, deletion from single-subitem and multi-subitem hash items, encrypted directory entries, tree-root directory entries that skip delayed indexes, lookup by hash and by directory index, and leaf-full collision overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dir-item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dir-item.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/dir-item.h

## Purpose

`dir-item.h` declares the internal Btrfs directory and xattr item API plus the CRC32C-based name hash helper. It is consumed by directory operations, xattr code, inode operations, delayed inode flushing/logging, and lookup/delete paths.

## Important APIs, Types, and Functions

The header declares directory collision checking, primary dir item insertion, primary dir item lookup, exact dir-index lookup, scanning dir-index search, one-name deletion, xattr insertion and lookup, and subitem name matching. The inline `btrfs_name_hash()` hashes a byte name with `crc32c((u32)~1, name, len)`.

## Control Flow

There is no major runtime control flow beyond the inline hash helper. The declared functions express the split between hash-based directory/xattr items and index-based directory items.

## State and Persistence Behavior

The header owns no state. Its functions operate on transaction handles, roots, btree paths, inode identifiers, and filesystem name strings to read or mutate persistent tree items.

## Dependencies and Integration Points

Dependencies include Linux types, CRC32C, fscrypt strings, Btrfs keys/paths/inodes/roots/transactions, and the on-disk `btrfs_dir_item` format declared elsewhere. Integration points are lookup, create, unlink, rename, xattrs, readdir indexes, and delayed inode secondary index insertion.

## Risks and Edge Cases

The hash helper is not collision-free, so users of this API must always perform exact name matching. Path ownership and transaction/mod flags are caller-controlled; misuse can leave paths locked or search without required COW for modification.

## Test Signals

Compile coverage should catch signature drift across directory and xattr users. Behavioral tests should include hash collisions, encrypted names, xattr item limits, index lookup/search, and deletion from overflow directory items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/dir-item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/direct-io.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/direct-io.c

## Purpose

`direct-io.c` implements Btrfs direct read/write support through iomap. It maps file extents to bios, coordinates extent locks and DIO locks with ordered extents and page cache invalidation, creates ordered extents for direct writes, chooses between COW, NOCOW, prealloc, and buffered fallback, and completes direct I/O through Btrfs bio submission and ordered extent completion.

## Important APIs, Types, and Functions

Public APIs are `btrfs_direct_write()`, `btrfs_direct_read()`, `btrfs_init_dio()`, and `btrfs_destroy_dio()`. Core iomap callbacks are `btrfs_dio_iomap_begin()`, `btrfs_dio_iomap_end()`, and `btrfs_dio_submit_io()`, registered through `btrfs_dio_iomap_ops` and `btrfs_dio_ops`.

Important helpers include `lock_extent_direct()`, `btrfs_create_dio_extent()`, `btrfs_new_extent_direct()`, `btrfs_get_blocks_direct_write()`, `btrfs_dio_end_io()`, `btrfs_extract_ordered_extent()`, `check_direct_IO()`, and `check_direct_read()`. `struct btrfs_dio_data` tracks submitted bytes, data reservation changeset, current ordered extent, and COW/NOCOW reservation flags. `struct btrfs_dio_private` embeds a `btrfs_bio` with file offset and byte count.

## Control Flow

Direct reads and writes enter iomap after alignment checks. Reads reject fsverity and duplicate iovec base pointers, take a shared inode lock, disable page faults around iomap, and retry after faulting user pages when progress is possible. Writes choose a shared inode lock only for within-EOF no-security-bit cases, reject true direct writes for duplicated/RAID56 data profiles because user buffers can mutate while mirrors are written, reject DATASUM direct writes to avoid checksum/data divergence, and otherwise run iomap with fault retry. When direct write cannot proceed or only partially proceeds, it falls back to buffered write, flushes/waits the written range, and invalidates mapping pages.

`btrfs_dio_iomap_begin()` flushes async compressed pages if needed, optionally reserves data space before locking, locks DIO and extent ranges, rejects inline/compressed extents to buffered fallback, restricts NOWAIT requests to a single extent, and for writes calls `btrfs_get_blocks_direct_write()`. That helper tries prealloc/NODATACOW NOCOW first, reserves metadata, creates ordered extent state, or allocates a fresh extent for COW using previously reserved data space. It releases unused data reservations and staged outstanding extents after ordered extents take ownership.

`btrfs_dio_submit_io()` initializes a Btrfs bio, tracks submitted bytes, splits ordered extents for partial write bios when needed, and submits through `btrfs_submit_bbio()`. Completion logs errors, finishes ordered extents for writes, unlocks DIO extents for reads, restores the iomap private pointer, and calls `iomap_dio_bio_end_io()`. `btrfs_dio_iomap_end()` cancels unsubmitted tails by finishing ordered extents as failed or unlocking read ranges.

## State and Persistence Behavior

Persistent data changes happen through allocated or existing extents and ordered extent completion. For COW direct writes, `btrfs_new_extent_direct()` reserves an extent, creates an extent map and ordered extent, and later finish-ordered-io inserts file extent items and delayed refs. For NOCOW/prealloc writes, the ordered extent records writes into existing/preallocated disk space. Reads hold DIO locks until bio completion to keep extent state stable. The file owns the `btrfs_dio_bioset` lifecycle for private direct-I/O bios.

## Dependencies and Integration Points

Dependencies include iomap direct I/O, Btrfs extent maps, extent locking, ordered extents, delalloc space reservations, extent allocation, transactions/ordered completion, Btrfs bio/volume mapping, file write checks, inode locks, page cache writeback/invalidation, fsverity, and block profile selection. It integrates with buffered I/O fallback, qgroup/delalloc metadata accounting, COW/NOCOW extent logic, and Btrfs checksum policy.

## Risks and Edge Cases

Direct I/O is intentionally conservative. Inline and compressed extents fall back. NOWAIT refuses multi-extent ranges and blocking page/writeback conditions. Data checksummed inodes fall back because user buffers may change after checksum calculation. Duplicated and parity data profiles fall back for the same user-buffer mutability reason across mirrors. Lock ordering must avoid deadlocks with buffered writes, readahead, and mmap self-I/O; the code disables user faults and retries to avoid waiting on ordered extents it has not submitted yet. Reservation cleanup must handle partial extent allocation, ordered extent splitting, and submitted-byte shortfalls.

## Test Signals

Tests should cover aligned and unaligned direct reads/writes, NOWAIT success and `-EAGAIN`, inline/compressed fallback, fsverity read fallback, checksummed direct write fallback, RAID1/RAID56 buffered fallback, NODATACOW and prealloc direct writes, COW direct writes with ENOSPC/EDQUOT, mmap-to-self direct I/O deadlock avoidance, partial user fault retries, partial bio ordered-extent splitting, read holes/prealloc extents, page cache invalidation after buffered fallback, and bioset init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/direct-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/direct-io.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/direct-io.h

## Purpose

`direct-io.h` declares the Btrfs direct I/O entry points and bioset lifecycle helpers implemented by `direct-io.c`. It is the narrow interface used by file read/write paths and module/filesystem initialization.

## Important APIs, Types, and Functions

The header forward declares `struct kiocb` and declares `btrfs_init_dio()`, `btrfs_destroy_dio()`, `btrfs_direct_write()`, and `btrfs_direct_read()`.

## Control Flow

There is no executable control flow. The API separates lifecycle setup/teardown of direct-I/O bio private storage from per-I/O read/write entry points.

## State and Persistence Behavior

The header owns no state. The implementation's bioset is initialized and destroyed through the lifecycle functions; reads and writes mutate filesystem state only through the implementation.

## Dependencies and Integration Points

Dependencies are minimal: Linux types and `struct kiocb`. Integration points are Btrfs file operations, iomap direct I/O, ordered extents, and filesystem initialization/cleanup.

## Risks and Edge Cases

Callers must ensure `btrfs_init_dio()` succeeds before direct I/O is available and pair it with `btrfs_destroy_dio()` on teardown. Direct read/write return values include buffered fallback behavior from the implementation, so callers should not assume every accepted request remains direct.

## Test Signals

Compile coverage should catch signature drift. Lifecycle tests should verify bioset initialization failure handling and teardown ordering, while file-operation tests should cover direct read/write fallback and completion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/direct-io.h -->
