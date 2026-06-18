# Group Research: group_857_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_da_btree_c_sources_os_5b556b4dcd3d

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux/fs/xfs/libxfs` XFS directory, attribute, and deferred-operation files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.c

## Scope

This file implements the shared XFS directory/attribute Btree machinery: DA state allocation, v2/v3 node header conversion and verification, node buffer reads, tree split/join, node rebalance/unbalance, path shifting, hash maintenance, name hashing/comparison, logical DA block allocation/removal, buffer mapping, and readahead.

## Main Interfaces

- State lifecycle: `xfs_da_state_alloc()`, `xfs_da_state_free()`, `xfs_da_state_reset()`.
- Header and verifier helpers: `xfs_da3_node_hdr_from_disk()`, `xfs_da3_node_hdr_to_disk()`, `xfs_da3_blkinfo_verify()`, `xfs_da3_node_header_check()`, `xfs_da3_header_check()`.
- Buffer operations: `xfs_da3_node_read()`, `xfs_da3_node_read_mapped()`, `xfs_da_get_buf()`, `xfs_da_read_buf()`, `xfs_da_reada_buf()`, `xfs_da_buf_copy()`.
- Btree growth: `xfs_da3_node_create()`, `xfs_da3_split()`, `xfs_da3_blk_link()`.
- Btree shrink: `xfs_da3_join()`, `xfs_da3_fixhashpath()`, `xfs_attr3_node_entry_remove()`, `xfs_da_shrink_inode()`.
- Search and traversal: `xfs_da3_node_lookup_int()`, `xfs_da3_path_shift()`.
- Utility: `xfs_da_hashname()`, `xfs_da_compname()`, `xfs_da_grow_inode()`, `xfs_da_grow_inode_int()`.

## Control Flow And Behavior

DA nodes are common infrastructure for both directory leaf/node format and attribute leaf/node format. The code normalizes v2 and v3 on-disk node headers into `xfs_da3_icnode_hdr` so most tree algorithms can ignore CRC-era layout differences. Read verifiers inspect magic, CRC metadata, UUID, block address, LSN validity, level, count, and ownership checks; leaf blocks discovered during ambiguous node reads have their buffer ops switched to the attr or dir leaf verifier.

Insertion starts at the leaf and walks upward through `xfs_da3_split()`. Leaf splits are delegated to attr or dir leaf code; internal node splits allocate a new DA block, rebalance entries, link the new block into the same-level sibling chain, insert child pointers, and propagate final hash values upward. Root splits copy the old root to a new block and create a fresh root with two child pointers.

Removal and shrink run through `xfs_da3_join()`. Leaf or node blocks that become too small are coalesced with a sibling when possible; empty blocks are unlinked and unmapped. If the root has a single remaining child, `xfs_da3_root_join()` copies that child back to block zero and frees the old child block.

Search descends from the root block, binary-searching internal node hash values while accounting for duplicate hashes. At the leaf level it delegates to directory or attribute lookup code. If the leaf’s last hash equals the search hash and lookup fails, it shifts to the next leaf to continue duplicate-hash search.

Logical DA block allocation uses bmap helpers to find unused file offsets and allocate contiguous filesystem blocks when possible. Directory block removal has a fallback for `-ENOSPC`: `xfs_da3_swap_lastblock()` moves the last DA block into the block being removed so the final mapping can be punched without needing a bmap split.

## State And Data Structures

- Uses `xfs_da_state`, `xfs_da_state_path`, and `xfs_da_state_blk` to track active root-to-leaf paths plus alternate paths for sibling joins.
- Uses `xfs_da_geometry` from the mount to interpret directory vs attribute block size, node capacity, leaf/free/data regions, and fork extent limits.
- Internal node entries store a descendant’s final hash and logical block number.
- Same-level blocks use `xfs_da_blkinfo` forward/back links; CRC filesystems embed this in `xfs_da3_blkinfo`.

## Dependencies

Depends on attr leaf helpers, dir leaf helpers, bmap allocation/unmapping, transaction buffer logging, buffer verifiers, metadata health marking, XFS error injection, and mount geometry initialized by directory setup.

## Risks And Invariants

- Internal node hash values must always equal the last hash in each child subtree; `xfs_da3_fixhashpath()` repairs this after split/join edits.
- Duplicate hashes require scanning sibling leaves; lookup changes must preserve path shifting behavior.
- DA block link/unlink must update both neighbors and validate owners before trusting sibling blocks.
- `xfs_da3_swap_lastblock()` is delicate because it updates sibling links and parent pointers after moving a block’s contents.
- v2/v3 layout abstraction depends on magic checks and correct buffer ops switching for node-vs-leaf ambiguity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.h

## Scope

This header declares the shared directory/attribute Btree geometry, operation arguments, search comparison results, tree traversal state, in-core v3 node header abstraction, logging range helpers, and the public DA Btree API used by directory and attribute code.

## Main Interfaces

- `struct xfs_da_geometry` describes DA block geometry, node capacity, directory data/leaf/free address-space boundaries, and maximum fork extents.
- `struct xfs_da_args` carries a single directory or attribute operation: names, values, inode, transaction, owner, hash, fork, block/index outputs, remote attr metadata, flags, and comparison result.
- `enum xfs_dacmp` reports different, exact, or case-insensitive name matches.
- Operation flags include just-check, replace, add-name, ok-no-entry, case-insensitive lookup, recovery, and logged intent operation.
- `xfs_da_state_blk`, `xfs_da_state_path`, and `xfs_da_state` hold traversal/split/join state.
- `struct xfs_da3_icnode_hdr` abstracts v2/v3 node header fields and points to node entries.
- Declares split/join/search/path/buffer/allocation/hash/state APIs.

## Data Model

The geometry is per mount and differs between the data fork directory Btree and the attribute fork. Directory geometry can span logical data, leaf, and free spaces; attribute geometry is one filesystem block. `xfs_da_args` is the central cross-layer argument object used by generic DA code, directory implementations, and attribute implementations.

## Dependencies

Forward declares inode and transaction types and depends on DA format definitions for magic values, block numbers, hash types, and node depth. Consumers include `xfs_da_btree.c`, directory shortform/block/leaf/node files, and attribute leaf/node/remote code.

## Risks And Invariants

- `XFS_DA_NODE_MAXDEPTH` is a structural limit assumed by traversal arrays and corruption checks.
- `xfs_da_args` fields are both input and output; callers must initialize owner, fork, geometry, hash, operation flags, and transaction consistently.
- `XFS_DA_LOGRANGE` computes byte ranges for metadata logging; incorrect base/size use can under-log metadata changes.
- State path arrays must match active depth and must not retain stale buffer pointers across reset/free.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_format.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_format.h

## Scope

This header defines the on-disk formats shared by XFS directories and attributes: DA node headers, v2/v3 directory block/data/leaf/free formats, shortform directory records, data entry/free record layouts, single-block directory tails, attribute shortform and leaf records, remote attribute block headers, namespace flags, and parent pointer records.

## Main Format Areas

- DA common structures: v2/v3 magic numbers, `xfs_da_blkinfo`, `xfs_da3_blkinfo`, node headers, node entries, and max depth.
- Directory v2/v3 formats: single-block, data, leaf1, leafn, and free block magic values plus CRC-era headers.
- Directory file types: on-disk `XFS_DIR3_FT_*` values and string table macro.
- Directory shortform: `xfs_dir2_sf_hdr`, `xfs_dir2_sf_entry`, 32-bit vs 64-bit inode packing helpers, offset helpers, and first-entry accessor.
- Directory data blocks: bestfree slots, active entry layout, unused/free entry layout, alignment constants, address-space partitioning, and tag accessors.
- Directory leaf/free/block format: leaf entries, leaf tail bestcount, free block bests array, single-block embedded leaf tail and accessor.
- Attribute formats: shortform header/entries, attr leaf header, entry array, local and remote name/value records, v3 attr leaf header, namespace/incomplete flags, and entry-size helpers.
- Remote attribute format: `xfs_attr3_rmt_hdr`, CRC offset, buffer payload sizing declaration.
- Parent pointer format: `xfs_parent_rec` storing parent inode and generation.

## Notable Layout Rules

Directory address space is partitioned into data, leaf, and free spaces separated by 32 GiB regions. Directory data entries are 8-byte aligned and carry a trailing tag equal to the entry offset. Single-block directories embed the leaf array and tail at the end of the data block.

Attribute leaf blocks pack sorted entries from the front and name/value storage from the back. The freemap tracks only the largest free regions, so compaction is sometimes required. Attribute local/remote entry size helpers deliberately preserve historical flex-array padding formulas from the on-disk ABI.

## Dependencies

This header is consumed by nearly all XFS directory and attribute implementation files, the DA Btree layer, remote attribute code, parent pointer code, verifiers, and userspace repair/tooling that must understand the same on-disk ABI.

## Risks And Invariants

- This file describes on-disk ABI. Structure layout, magic values, alignment, padding formulas, and field sizes cannot be changed casually.
- v3 CRC headers must remain first-field compatible where generic DA code treats them as `xfs_da_blkinfo`.
- Attr namespace and incomplete bits control user-visible xattrs, parent pointers, and crash recovery semantics.
- Directory file type additions require on-disk feature support.
- Shortform directory and attribute structures are variable length; callers must use accessors instead of assuming fixed offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.c

## Scope

This file implements XFS deferred operations: batching metadata work, logging intent/done items for crash recovery, rolling transactions while preserving held resources, finishing or canceling pending work, pausing work items, capturing deferred chains during log recovery, and initializing intent-item caches.

## Main Interfaces

- Work queueing and lifecycle: `xfs_defer_add()`, `xfs_defer_add_barrier()`, `xfs_defer_cancel()`, `xfs_defer_move()`.
- Finish paths: `xfs_defer_finish_noroll()`, `xfs_defer_finish()`, `xfs_defer_finish_one()`.
- Pause controls: `xfs_defer_item_pause()`, `xfs_defer_item_unpause()`.
- Recovery setup: `xfs_defer_start_recovery()`, `xfs_defer_cancel_recovery()`, `xfs_defer_finish_recovery()`.
- Recovery capture/continue: `xfs_defer_ops_capture_and_commit()`, `xfs_defer_ops_continue()`, `xfs_defer_ops_capture_abort()`, `xfs_defer_resources_rele()`.
- Cache lifecycle: `xfs_defer_init_item_caches()`, `xfs_defer_destroy_item_caches()`.

## Control Flow And Behavior

Deferred work is grouped into `xfs_defer_pending` records by operation type. New work is appended to the last compatible pending item unless that item has already logged an intent, is paused, or has reached the operation’s `max_items` limit.

Finishing deferred work first creates log intent items for all intake work, isolates paused items, moves active work to a pending list, rolls the transaction if needed, and finishes the first pending item. Finishing a pending item creates a done item, calls the operation type’s `finish_item` for each work record, and frees the pending record when complete.

If `finish_item` returns `-EAGAIN`, the item is restored to the work list and a replacement intent is logged so the caller can roll to a fresh transaction and resume safely. The code also relogs old intent items when log-tail pressure requires moving the log forward.

Transaction rolls preserve held buffers and inodes. Buffers with `XFS_BLI_HOLD` are rejoined and optionally re-marked ordered; inodes joined without unlock flags are relogged and rejoined to the new transaction.

Recovery can capture a chain of deferred ops into `xfs_defer_capture`, commit the current transaction with fresh intents logged, and later continue the captured work in a new transaction after relocking saved inodes and buffers.

## State And Data Structures

- `xfs_defer_pending_cache` allocates pending work records.
- `xfs_defer_pending` tracks work list, intent item, done item, op type, count, and flags.
- `xfs_defer_resources` records held buffers, ordered buffer bitmap, and inodes that must survive transaction rolls.
- `xfs_defer_capture` stores a captured dfops list, transaction flags, block/log reservations, and held resources.
- `xfs_defer_op_type` callbacks define operation-specific intent creation, done creation, item finish, cleanup, cancellation, recovery, and relogging.

## Dependencies

Integrates with transaction internals, log items, AIL/log-tail push state, buffer and inode log items, rmap/refcount/bmap/extfree/attr/exchange intent caches, metadata health shutdown, and tracepoints.

## Risks And Invariants

- Deferred operations require permanent log reservations; most entry points assert `XFS_TRANS_PERM_LOG_RES`.
- Intent and done items must be logged in the correct transaction order to preserve crash replay guarantees.
- `-EAGAIN` handling depends on the finish callback updating the current work item to represent unfinished work.
- Held resource capture is bounded by `XFS_DEFER_OPS_NR_INODES` and `XFS_DEFER_OPS_NR_BUFS`; exceeding those bounds indicates corruption or incorrect caller behavior.
- Error paths abort outstanding intents, force shutdown for in-core corruption, and cancel pending work to avoid replay ambiguity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.h

## Scope

This header declares the deferred-operation framework data structures, operation-type callback table, exported defer op types, resource capture state, recovery APIs, pause flag, and cache lifecycle functions.

## Main Interfaces

- `struct xfs_defer_pending` stores one pending deferred operation group, its work items, log intent, log done item, operation type, count, and flags.
- `XFS_DEFER_PAUSED` marks pending work that should be carried forward without finishing.
- `struct xfs_defer_op_type` defines callbacks for intent creation/abort, done creation, item finishing, cleanup, cancellation, recovery, and relogging.
- Exports operation types for bmap, refcount, realtime refcount, rmap, realtime rmap, extent free, AGFL free, realtime extent free, attr, and exchange mappings.
- `struct xfs_defer_resources` tracks buffers and inodes held across transaction rolls.
- `struct xfs_defer_capture` stores detached deferred ops plus reservations and held resources for recovery continuation.
- Inline `xfs_defer_add_item()` appends a work item and increments the count.

## Dependencies

Forward declares btree cursor, defer op type, and capture structures, and relies on transaction, log item, list, buffer, and inode types from the broader XFS kernel environment.

## Risks And Invariants

- `max_items` constrains log reservation sizing for each operation type.
- Callback contracts are strict: finish callbacks may request continuation with `-EAGAIN`, cleanup must release operation-specific state, and recovery callbacks own recovered pending records.
- Resource capture supports up to five inodes and two buffers, chosen for complex rename/parent-pointer deferred operations.
- Paused work must not have unresolved data dependencies because it can be requeued indefinitely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.c

## Scope

This file implements the generic XFS directory API above the specific shortform, block, leaf, and node directory formats. It initializes DA geometry, validates inode numbers and names, dispatches create/lookup/remove/replace operations by current directory format, handles ASCII case-insensitive hashing/comparison, grows/shrinks directory data/free spaces, and coordinates child create/link/unlink/rename/exchange operations with link counts, parent pointers, whiteouts, timestamps, and live hooks.

## Main Interfaces

- Constants and helpers: `xfs_name_dot`, `xfs_name_dotdot`, `xfs_mode_to_ftype()`, `xfs_dir2_namecheck()`.
- Case-insensitive support: `xfs_ascii_ci_hashname()`, `xfs_ascii_ci_compname()`, `xfs_dir2_hashname()`, `xfs_dir2_compname()`.
- Mount geometry: `xfs_da_mount()`, `xfs_da_unmount()`.
- Directory format and operations: `xfs_dir2_format()`, `xfs_dir_init()`, `xfs_dir_createname()`, `xfs_dir_lookup()`, `xfs_dir_removename()`, `xfs_dir_replace()`, `xfs_dir_canenter()`.
- Args-level dispatch: `xfs_dir_createname_args()`, `xfs_dir_lookup_args()`, `xfs_dir_removename_args()`, `xfs_dir_replace_args()`.
- Directory block management: `xfs_dir2_grow_inode()`, `xfs_dir2_shrink_inode()`.
- Child update orchestration: `xfs_dir_create_child()`, `xfs_dir_add_child()`, `xfs_dir_remove_child()`, `xfs_dir_exchange_children()`, `xfs_dir_rename_children()`.
- Optional live hooks: `xfs_dir_update_hook()`, hook add/delete/setup/enable/disable functions under `CONFIG_XFS_LIVE_HOOKS`.

## Control Flow And Behavior

`xfs_da_mount()` builds separate directory and attribute geometries from superblock block size, directory block log, CRC feature state, and large extent count support. Directory geometry computes data, leaf, and free space boundaries, node capacity, free index capacity, and first data offset after `.` and `..`.

The generic directory operations allocate and populate `xfs_da_args`, compute the name hash, set owner/fork/transaction fields, and dispatch based on `xfs_dir2_format()`. Shortform, single-block, leaf, and node directories are handled by specialized files. Lookup returns `0` to callers after translating internal `-EEXIST` success, and optional case-insensitive lookup can return the actual matching name.

Directory growth allocates data/free blocks via DA allocation helpers and updates inode size for data-space growth. Shrink unmaps directory data/free blocks, invalidates buffers, and reduces inode size when the removed data block was the last directory data block.

Higher-level child operations maintain VFS-visible metadata. Creating or adding a child inserts the dirent, updates parent timestamps, initializes child directories, bumps link counts, removes tmpfile inodes from the unlinked list when needed, and adds parent pointer attributes when enabled. Removing a child verifies empty directories, adjusts `.` and `..` link counts, rewrites removed directory `..` to root when necessary, removes parent pointer attrs, and emits live hooks.

Rename and exchange handle cross-directory moves, directory `..` replacement, target overwrite link count drops, whiteout insertion, parent pointer replacement/removal/addition, inode ctime updates, and hook notifications modeled as remove events followed by add events.

## State And Data Structures

- Uses `xfs_da_geometry` stored in `m_dir_geo` and `m_attr_geo`.
- Uses `xfs_da_args` as the dispatch object for all format-specific directory operations.
- Uses `xfs_dir_update` to pass directory, child, name, and parent-pointer arguments to child update helpers.
- Optional hook payload is `xfs_dir_update_params`.

## Dependencies

Depends on shortform/block/leaf/node directory implementations, DA Btree allocation, bmap helpers, inode link count helpers, transaction inode logging, parent pointer attribute code, unlinked-list removal, per-AG lookup, live hook infrastructure, and health marking.

## Risks And Invariants

- Format detection assumes data fork locking and validates single-block directories by both EOF and inode disk size.
- Directory inode numbers are validated before insertion and lookup results are checked against filesystem inode constraints.
- Link count and `..` updates must remain transactionally consistent across create, remove, rename, exchange, and whiteout paths.
- Parent pointer updates must match dirent updates exactly or online repair and reverse lookup semantics break.
- Live hook enable/disable uses static branch patching and must not be called while holding reclaim-sensitive locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.h

## Scope

This header declares the public XFS directory interface, directory format enumeration, directory data/free logging helpers, buffer ops, address conversion helpers, block-tail accessors, ASCII case-insensitive helpers, optional live hook interfaces, and child update operation structures.

## Main Interfaces

- Exports `xfs_name_dot` and `xfs_name_dotdot`.
- `xfs_dir2_samename()` compares two `xfs_name` values.
- `enum xfs_dir2_fmt` identifies shortform, block, leaf, node, and error formats.
- Declares generic directory APIs: init, create, lookup, remove, replace, can-enter, and args-level variants.
- Declares direct shortform-to-block conversion and directory shrink helper.
- Declares data block free/logging helpers and data/free/leaf/block verifiers and buffer ops.
- Provides inline conversions among directory byte offsets, dataptrs, logical DB blocks, and DA blocks.
- Provides single-block tail and leaf-tail pointer helpers.
- Defines `XFS_READDIR_BUFSIZE`.
- Declares filetype and name validation helpers.
- Defines ASCII case-insensitive transform helpers for the historical `ascii-ci` feature.
- Defines live hook structures and child update structures/APIs.

## Data Model

Directory offsets use several related coordinate systems: file byte offsets, compact dataptrs, logical directory DB blocks, and DA blocks. The inline helpers centralize conversions using `xfs_da_geometry` so directory implementations can move between on-disk leaf addresses and buffer offsets safely.

## Dependencies

Includes `xfs_da_format.h` and `xfs_da_btree.h`, and is included by generic directory code, shortform/block/leaf/node implementations, readdir, parent pointer code, and userspace-oriented libxfs consumers.

## Risks And Invariants

- Conversion helpers depend on geometry fields initialized at mount time; incorrect `blklog` or `fsblog` corrupts address calculations.
- Tail accessors assume fixed placement at the end of the directory block.
- `ascii-ci` intentionally handles a limited byte transform and does not imply general Unicode casefolding.
- Hook declarations compile to no-ops without `CONFIG_XFS_LIVE_HOOKS`; callers must tolerate both builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_block.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_block.c

## Scope

This file implements the XFS single-block directory format: block verification, initialization, lookup, add, remove, replace, logging of embedded leaf/tail regions, conversion from shortform to block, and conversion from leaf back to block when possible.

## Main Interfaces

- Startup: `xfs_dir_startup()` precomputes hashes for `.` and `..`.
- Verification and buffer ops: `xfs_dir3_block_buf_ops`, `xfs_dir3_block_header_check()`, `xfs_dir3_block_read()`.
- Block initialization: internal `xfs_dir3_block_init()`.
- Single-block operations: `xfs_dir2_block_addname()`, `xfs_dir2_block_lookup()`, `xfs_dir2_block_removename()`, `xfs_dir2_block_replace()`.
- Conversion: `xfs_dir2_leaf_to_block()`, `xfs_dir2_sf_to_block()`.
- Internal helpers: block space selection, leaf compaction, leaf/tail logging, lookup implementation, and leaf-entry sort comparator.

## Control Flow And Behavior

Block verifiers check magic, CRC metadata, UUID, block address, LSN, and data block structural consistency. `xfs_dir3_block_read()` reads the one data block, validates the owner for CRC filesystems, marks the buffer type, and marks directory health sick on corruption.

Adding a name reads the block, determines whether there is room for both a data entry and leaf entry, optionally compacts stale embedded leaf entries, binary-searches the leaf array by hash, inserts or reuses a leaf slot, allocates free space for the data entry, writes inode/name/filetype/tag, updates bestfree, and logs modified ranges. If no room exists and the caller has space reservation, it converts the directory to leaf format and retries there; if the call was only a space check it returns `-ENOSPC` or success without modification.

Lookup binary-searches the embedded leaf array, backs up to the first duplicate hash, scans forward through matching hashes, skips stale entries, compares names with normal or ASCII case-insensitive comparison, and returns the inode/filetype plus optional CI actual name.

Removal marks the data entry free, marks the leaf address stale, updates tail stale count, rescans bestfree if needed, and then tests whether the directory now fits in shortform. If it fits, it converts block format to shortform.

Replacement finds the entry and updates only the inode number and filetype in the data entry.

Leaf-to-block conversion succeeds only when the directory has no extra nonempty data blocks and the first data block has enough trailing free space to embed the leaf entries and tail. It initializes the block header, compacts out stale leaf entries, frees the old leaf block, and may further shrink to shortform.

Shortform-to-block conversion copies the in-inode directory to a temporary buffer, converts the data fork to extents, allocates block zero, initializes data/block headers, creates `.` and `..`, recreates all shortform entries at their preserved offsets, fills holes as unused entries, sorts leaf entries by hash, and logs the new block.

## State And Data Structures

- Single-block directories are a data block with active/unused entries at the front and an embedded sorted leaf array plus `xfs_dir2_block_tail` at the end.
- Tail fields track leaf entry count and stale count.
- Directory data bestfree tracks the largest free regions used to choose insertion space.
- Precomputed dot/dotdot hashes are used during shortform-to-block conversion.

## Dependencies

Depends on directory data helpers, DA buffer reads, bmap conversion from local to extents, leaf format conversion code, transaction logging, CRC buffer verification, and directory health marking.

## Risks And Invariants

- Embedded leaf entries must remain sorted by hash and must preserve duplicate-hash lookup behavior.
- Stale leaf entries and free data regions are separate accounting systems; compaction must update both correctly.
- Add paths must reserve room for both the data entry and the embedded leaf entry.
- Shortform-to-block conversion preserves shortform offsets by creating holes where needed.
- Conversion fallback decisions affect ENOSPC behavior and must respect whether the caller supplied a space reservation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_block.c -->