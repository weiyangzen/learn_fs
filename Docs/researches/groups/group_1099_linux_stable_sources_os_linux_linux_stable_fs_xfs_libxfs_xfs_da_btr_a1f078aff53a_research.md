# Group Research: group_1099_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_da_btr_a1f078aff53a

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`.

This group covers XFS libxfs directory/attribute btree infrastructure, directory on-disk formats, deferred operation transaction machinery, and single-block directory operations.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.c

## Role
`xfs_da_btree.c` is the shared directory/attribute btree engine for XFS. It manages hashed-name btrees used by large directories and extended attributes, including node creation, lookup traversal, split/join rebalancing, sibling list maintenance, logical-to-physical buffer mapping, and block allocation/removal.

## Main Responsibilities
- Allocate, reset, and free `struct xfs_da_state` search/split state through `xfs_da_state_alloc`, `xfs_da_state_reset`, and `xfs_da_state_free`.
- Abstract v2/v3 node headers through `xfs_da3_node_hdr_from_disk` and `xfs_da3_node_hdr_to_disk`.
- Verify DA block metadata for magic values, CRC-era UUID/block/LSN fields, owner checks, node level, and entry count limits.
- Read DA node buffers and dynamically dispatch leaf-looking buffers to attr or directory leaf verifiers when the caller expected a node.
- Grow and shrink directory/attribute btrees through split, root split, join, root join, node rebalance/unbalance, and sibling link/unlink helpers.
- Traverse the btree for lookups using hashed names and duplicate-hash aware descent.
- Allocate, map, read, readahead, copy, and remove DA blocks in the data or attr fork.

## Important Functions
- `xfs_da3_split` walks from a leaf back toward the root, splitting leaf or node blocks as necessary and propagating last-hash updates up the path.
- `xfs_da3_root_split` copies the old root to a new block, creates a new root, and installs two child entries pointing at the split children.
- `xfs_da3_node_split`, `xfs_da3_node_rebalance`, and `xfs_da3_node_add` split full intermediate nodes, rebalance entries between siblings, and insert child pointers.
- `xfs_da3_join`, `xfs_da3_root_join`, `xfs_da3_node_toosmall`, and `xfs_da3_node_unbalance` shrink btrees after deletion by coalescing or dropping underfilled blocks.
- `xfs_da3_node_lookup_int` performs the core btree lookup. It descends from `geo->leafblk`, validates each buffer, binary-searches node entries by hash, and handles duplicate hashes by shifting to adjacent leaves when needed.
- `xfs_da3_path_shift` moves an active search path to the next or previous block at the same level by walking up to a parent edge and then back down.
- `xfs_da3_blk_link` and `xfs_da3_blk_unlink` maintain same-level doubly linked lists using the common `xfs_da_blkinfo` prefix.
- `xfs_da_grow_inode_int`, `xfs_da_grow_inode`, `xfs_da_shrink_inode`, and `xfs_da3_swap_lastblock` handle logical file space allocation and deallocation for DA blocks.
- `xfs_dabuf_map`, `xfs_da_get_buf`, `xfs_da_read_buf`, and `xfs_da_reada_buf` map fork offsets to buffer maps and acquire/read/readahead metadata buffers.

## Data and Invariants
- The tree uses hash values as separator keys, with each node entry storing the largest hash under its child in `hashval` and the child logical block in `before`.
- `xfs_da_state.path` tracks the active descent path; `altpath` is used for neighboring blocks during joins; `extrablk` handles double-split attr leaf cases.
- Magic numbers are normalized in state blocks to `XFS_DA_NODE_MAGIC`, `XFS_ATTR_LEAF_MAGIC`, or `XFS_DIR2_LEAFN_MAGIC` so most logic does not need separate v2/v3 cases.
- Node levels must be nonzero for internal nodes, must not exceed `XFS_DA_NODE_MAXDEPTH`, and must decrease consistently while descending.
- Directory data-fork leaf/node blocks are expected in the leaf/free logical space ranges; attr-fork DA blocks use attr geometry and single-fsb block sizing.

## Error Handling and Corruption Response
- Verifier failures return `-EFSCORRUPTED` or `-EFSBADCRC`, mark buffers corrupt, and mark the directory/attribute fork sick through `xfs_da_mark_sick` or `xfs_dirattr_mark_sick`.
- Mapping holes are corruption unless `XFS_DABUF_MAP_HOLE_OK` is supplied.
- `xfs_da_shrink_inode` has special handling for data-fork `-ENOSPC` during unmap: it swaps the target with the last btree block so the final block can be removed without forcing a bmap split.
- Read paths disambiguate attr-fork `-ENODATA` from disk medium failure by converting it to `-EIO`.

## Dependencies
This file is central glue for `xfs_attr_leaf.c`, directory leaf/node code, bmap allocation/unmap APIs, transaction logging, buffer verifiers, health reporting, and tracepoints. It depends heavily on geometry from `xfs_da_geometry`, on on-disk format definitions in `xfs_da_format.h`, and on directory helpers from `xfs_dir2.h`/`xfs_dir2_priv.h`.

## Research Notes
The file is the main place where XFS makes directory and attribute trees share code. The most important behavioral pattern is that all structural edits are transaction-logged at precise byte ranges, while btree separators are repaired by propagating each child block's last hash upward after splits, joins, and shifts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.h

## Role
`xfs_da_btree.h` declares the shared directory/attribute btree interface, search state, operation arguments, and geometry used by XFS directory and extended attribute code.

## Main Definitions
- `struct xfs_da_geometry` describes DA block size, fsblock count, header sizes, maximum entries, magic free-space percentage, directory logical segment starts, and fork extent limits.
- `enum xfs_dacmp` models name comparison outcomes: different, exact, or case-insensitive match.
- `struct xfs_da_args` is the common operation context for directory and attribute actions. It carries the name, optional new name/value, inode, transaction, owner, hash, fork selector, remote attr tracking fields, and operation flags.
- `XFS_DA_OP_*` flags describe operation intent such as just-check, replace, add-name, no-entry-ok, case-insensitive lookup, recovery, and logged operation.
- `struct xfs_da_state_blk`, `struct xfs_da_state_path`, and `struct xfs_da_state` model the active and alternate paths through DA btrees during lookup, split, and join operations.
- `struct xfs_da3_icnode_hdr` is the in-core abstraction for v2/v3 node headers and points directly at on-disk btree entries.

## Exported API
- Growth and shrinkage: `xfs_da3_node_create`, `xfs_da3_split`, `xfs_da3_join`, `xfs_da3_fixhashpath`, and `xfs_attr3_node_entry_remove`.
- Lookup/path movement: `xfs_da3_node_lookup_int` and `xfs_da3_path_shift`.
- Block and inode management: `xfs_da3_blk_link`, `xfs_da3_node_read`, `xfs_da3_node_read_mapped`, `xfs_da_grow_inode`, `xfs_da_grow_inode_int`, `xfs_da_get_buf`, `xfs_da_read_buf`, `xfs_da_reada_buf`, and `xfs_da_shrink_inode`.
- Utility helpers: `xfs_da_buf_copy`, `xfs_da_hashname`, `xfs_da_compname`, state allocation/free/reset, header conversion, and owner/header checks.

## Design Notes
- `xfs_da_args` deliberately combines directory and xattr fields, which lets the btree code operate on either fork with one algorithm.
- Geometry is passed rather than recomputed so directory and attribute forks can differ in block sizing and layout while sharing code.
- `XFS_DA_LOGOFF` and `XFS_DA_LOGRANGE` standardize byte-range logging of modified metadata fields.

## Dependencies
The header depends on format constants from `xfs_da_format.h` and is included by directory, attr, and DA btree implementations. It exposes `xfs_da_state_cache`, the slab cache backing large per-operation state objects.

## Research Notes
This header is the best compact map of the DA btree subsystem. The key concept is that `xfs_da_args` describes the operation while `xfs_da_state` describes the btree path and temporary split/join blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_format.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_format.h

## Role
`xfs_da_format.h` defines the on-disk format structures and constants for XFS directory/attribute btrees, directory data/leaf/free/block layouts, shortform directories, attribute leaves, remote attributes, and parent pointer records.

## DA Btree Format
- Defines v2 magic values for DA nodes, attr leaves, and dir leaf blocks, plus v3 CRC-enabled equivalents.
- `struct xfs_da_blkinfo` is the common first field for leaf and internal blocks, carrying same-level forward/back links and magic.
- `struct xfs_da3_blkinfo` adds CRC, block number, LSN, UUID, and owner fields for metadata-CRC filesystems.
- `struct xfs_da_node_hdr`, `struct xfs_da3_node_hdr`, `struct xfs_da_node_entry`, `struct xfs_da_intnode`, and `struct xfs_da3_intnode` define internal btree nodes and separator entries.

## Directory Format
- Documents the four directory formats: shortform, single block, multiple data blocks with one leaf/free index, and node/leaf btree form.
- Defines v2/v3 block, data, and free magic values.
- Defines directory file type values `XFS_DIR3_FT_*` and their trace string mapping.
- Defines directory address-space concepts: data, leaf, and free spaces separated by 32GB logical regions.
- Defines shortform headers and entries, including helpers for variable-size headers and stored offsets.
- Defines data-block headers, free extents, active entries, unused entries, leaf blocks, leaf entries, leaf tails, free blocks, and single-block directory tails.
- Provides helpers such as `xfs_dir2_sf_hdr_size`, `xfs_dir2_sf_firstentry`, `xfs_dir2_data_unused_tag_p`, `xfs_dir2_leaf_bests_p`, and `xfs_dir2_block_leaf_p`.

## Attribute Format
- Defines shortform xattr headers/entries, leaf free maps, leaf entries, local name/value records, remote name records, and CRC-enabled attr leaf variants.
- Attribute leaf entries are sorted by hash and store namespace/status flags.
- Defines namespace and storage flags including local, root, secure, parent, and incomplete bits.
- Provides accessors for v2/v3 attr leaf header size, leaf entry arrays, and local/remote name-value payloads.
- Defines precise local and remote attribute entry size calculations that preserve historical on-disk layout after flex-array conversions.

## Remote Attributes and Parent Pointers
- Defines the v3 remote attribute block header with magic, offset, bytes, CRC, UUID, owner, block number, and LSN.
- Declares `xfs_attr3_rmt_buf_space`.
- Defines `struct xfs_parent_rec`, the packed parent pointer value containing parent inode and generation.

## Invariants
- Many structures are variable length and must be traversed through helper accessors rather than direct array assumptions.
- v3 formats add verification metadata but preserve layout relationships used by v2/v3 shared code, especially the common `xfs_da_blkinfo` prefix.
- Directory data entries are 8-byte aligned; attr name/value payloads are 4-byte aligned.
- Some attr entry size formulas are explicitly part of the on-disk ABI and cannot be changed even if C struct padding differs across architectures.

## Research Notes
This header is the on-disk ABI reference for the rest of the group. Most implementation complexity in the C files follows directly from these layout constraints: variable-length entries, end-of-block leaf/tail placement, shared v2/v3 prefixes, and duplicate hash keys.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.c

## Role
`xfs_defer.c` implements XFS deferred operations: a generic framework for work that must be split across rolling transactions while preserving crash recovery through log intent and log done items.

## Main Responsibilities
- Queue typed deferred work items on a transaction.
- Create log intent items before rolling transactions.
- Create log done items as work is completed.
- Finish deferred work one item type at a time while allowing continuations through `-EAGAIN`.
- Relog old intent items to avoid pinning the log tail.
- Save and restore held buffers/inodes across transaction rolls.
- Capture deferred operation chains during log recovery and continue them later.
- Initialize and destroy caches for deferred operation pending items and all registered intent item types.

## Deferred Operation Model
- `struct xfs_defer_pending` tracks one pending operation type, a work list, an optional intent item, an optional done item, item count, flags, and its `xfs_defer_op_type`.
- `struct xfs_defer_op_type` supplies operation-specific hooks for creating/aborting intents, creating done items, finishing work, cleanup, canceling work, recovering work, and relogging intents.
- Work first enters `tp->t_dfops`, then intent creation and transaction rolls move it into pending processing.
- Barrier deferred ops are represented by `xfs_barrier_defer_type` and force separation between otherwise adjacent deferred work batches.

## Important Functions
- `xfs_defer_add` appends a work item to the last compatible pending item, or allocates a new pending item if type, logged state, pause state, or max-items limits prevent append.
- `xfs_defer_create_intent` and `xfs_defer_create_intents` create log intents for deferred work and attach them to the transaction.
- `xfs_defer_create_done` creates intent-done log items and marks the transaction dirty.
- `xfs_defer_finish_one` creates the done item, calls the type-specific `finish_item` hook for each work item, and handles `-EAGAIN` by rebuilding a new intent for unfinished work.
- `xfs_defer_finish_noroll` is the core finishing loop: create intents, isolate paused items, splice intake to pending, roll transactions when needed, relog old intents, finish the first pending item, and abort/shutdown on unrecoverable errors.
- `xfs_defer_finish` wraps the no-roll path and rolls once more if the outgoing transaction is dirty.
- `xfs_defer_cancel` aborts outstanding intents and cancels all queued work.
- `xfs_defer_trans_roll`, `xfs_defer_save_resources`, and `xfs_defer_restore_resources` preserve selected buffers and inodes across transaction rolls.
- `xfs_defer_ops_capture_and_commit`, `xfs_defer_ops_continue`, and `xfs_defer_resources_rele` implement recovery-time capture and continuation.

## Error Handling and Recovery
- If finishing fails with an error other than `-EAGAIN`, the code aborts pending intents, forces a corrupt in-core shutdown, cancels pending and transaction dfops, and returns the error.
- `-EAGAIN` from an operation-specific finisher is a controlled continuation request. The unfinished item is requeued and a new intent is logged in the same transaction context.
- Recovery starts with `xfs_defer_start_recovery`, cancels through `xfs_defer_cancel_recovery`, and finishes through the operation type's `recover_work`.
- Captured recovery chains store deferred ops, low-space flags, block reservations, realtime reservations, log reservation, and held resources.

## Invariants
- Deferred finishing requires permanent log reservation (`XFS_TRANS_PERM_LOG_RES`).
- Paused items are isolated and requeued without being finished until unpaused.
- Held buffer and inode counts are bounded by `XFS_DEFER_OPS_NR_BUFS` and `XFS_DEFER_OPS_NR_INODES`.
- Intent relogging is allowed to be racy because a false negative only slows log-tail movement.

## Dependencies
This file coordinates with transaction internals, log items, buffer and inode log items, rmap/refcount/bmap/extent-free/attr/exchange-map intent caches, allocation and btree subsystems, and log recovery.

## Research Notes
This file is the crash-safety and transaction-splitting backbone for complex XFS metadata updates. Its main abstraction is operation-specific intent/done handling under a generic queueing and transaction roll engine.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.h

## Role
`xfs_defer.h` declares the public deferred-operation framework used by XFS metadata update code and log recovery.

## Main Definitions
- `struct xfs_defer_pending` represents one pending batch of work for a single operation type, including work list, intent item, done item, hook table, count, and flags.
- `XFS_DEFER_PAUSED` marks a deferred item whose intent exists but whose work should not be finished yet.
- `struct xfs_defer_op_type` is the operation-specific vtable for intent creation, abort, done creation, item finishing, cleanup, cancellation, recovery, and intent relogging.
- `struct xfs_defer_resources` stores buffers and inodes that must be held across a transaction roll.
- `struct xfs_defer_capture` stores a detached deferred-operation chain and transaction state so recovery can continue it later.

## Exported API
- Queueing and finishing: `xfs_defer_add`, `xfs_defer_finish_noroll`, `xfs_defer_finish`, `xfs_defer_finish_one`, `xfs_defer_cancel`, and `xfs_defer_move`.
- Pausing: `xfs_defer_item_pause`, `xfs_defer_item_unpause`, and `xfs_defer_add_barrier`.
- Recovery: `xfs_defer_start_recovery`, `xfs_defer_cancel_recovery`, `xfs_defer_finish_recovery`, `xfs_defer_ops_capture_and_commit`, `xfs_defer_ops_continue`, and `xfs_defer_resources_rele`.
- Cache lifecycle: `xfs_defer_init_item_caches` and `xfs_defer_destroy_item_caches`.

## Registered Operation Types
The header exposes defer types for bmap updates, refcount updates, realtime refcount updates, rmap updates, realtime rmap updates, extent frees, AGFL frees, realtime extent frees, attrs, and exchange-map operations.

## Design Notes
- The framework is intentionally generic: actual filesystem operation logic lives in each `xfs_defer_op_type`, while the common code handles transaction ordering and recovery.
- The capture structure is explicitly recovery-oriented and saves enough reservation and held-resource state to reconnect deferred work to a new transaction.

## Research Notes
This header is the compact contract between metadata subsystems and the deferred-ops engine. New deferred work types plug in by defining an `xfs_defer_op_type` and using `xfs_defer_add`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.c

## Role
`xfs_dir2.c` is the generic XFS directory operation layer. It dispatches directory create, lookup, remove, replace, grow, shrink, and higher-level child update operations to the correct shortform/block/leaf/node implementation.

## Main Responsibilities
- Define canonical `.` and `..` names and convert inode modes to directory file types.
- Provide ASCII case-insensitive hashing and comparison for filesystems with the legacy ascii-ci feature.
- Allocate and initialize directory and attribute DA geometry at mount time.
- Determine a directory's current format from inode fork format and mapped EOF.
- Build `xfs_da_args` and dispatch createname, lookup, removename, and replace operations to format-specific helpers.
- Grow and shrink directory data/free blocks.
- Validate directory entry names and inode numbers.
- Coordinate higher-level link, unlink, rename, exchange, whiteout, parent-pointer, and live-hook behavior.

## Important Functions
- `xfs_da_mount` initializes `m_dir_geo` and `m_attr_geo`, computing block sizes, header sizes, leaf/free/node capacities, logical segment starts, max extents, and magic free-space thresholds.
- `xfs_dir2_format` returns shortform, block, leaf, node, or error based on local fork status and last mapped offset.
- `xfs_dir_createname`, `xfs_dir_lookup`, `xfs_dir_removename`, and `xfs_dir_replace` allocate and populate `xfs_da_args`, including hash, fork, transaction, owner, and operation flags.
- `xfs_dir2_grow_inode` allocates directory data/free-space blocks and grows `i_disk_size` for data-space additions.
- `xfs_dir2_shrink_inode` unmaps directory data/free blocks, invalidates buffers, and trims `i_disk_size` when removing trailing data blocks.
- `xfs_dir_create_child`, `xfs_dir_add_child`, and `xfs_dir_remove_child` implement VFS-level child link/unlink semantics, link count updates, parent pointer updates, and directory update hooks.
- `xfs_dir_exchange_children` swaps two existing directory entries and adjusts `..` entries and link counts for directory moves across parents.
- `xfs_dir_rename_children` implements rename with replacement and optional whiteout handling, including target setup, source cleanup, parent pointer updates, and hook notifications.

## Invariants
- Directory operations assert directory inode mode and required inode locks for high-level child updates.
- Inode numbers are validated through `xfs_dir_ino_validate` before insertion or replacement.
- Shortform empty-directory checks assume only `.` and `..` are present when the shortform count is zero.
- The format detector treats local fork data as shortform, one data block as block format, data plus one leaf block as leaf format, and larger layouts as node format.
- Rename and exchange model hook notifications as removals before additions so clients can process changes consistently while locks are held.

## Error Handling
- Corrupt format state marks directory data sick and returns `-EFSCORRUPTED`.
- Expected semantic failures such as non-empty directory removal use `-ENOTEMPTY` or `-EEXIST`.
- No-space checks are supported through `xfs_dir_canenter` and `XFS_DA_OP_JUSTCHECK`.
- `xfs_dir2_shrink_inode` deliberately leaves a block mapped if unmapping returns an error such as no reservation for a bmap split.

## Dependencies
This file bridges VFS-facing directory behavior with format-specific files such as shortform, block, leaf, node, data, and parent-pointer code. It also touches bmap, transaction, inode link count, AG unlink-list, live hooks, and health subsystems.

## Research Notes
The central pattern is format dispatch through `xfs_dir2_format` plus shared `xfs_da_args`. Higher-level directory mutation code is careful to stage link counts, `..` entries, parent pointers, and hook notifications in transaction-safe order.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.h

## Role
`xfs_dir2.h` declares the generic directory API, directory format enumeration, directory offset conversion helpers, live-update hook interface, and higher-level child update structures.

## Main Definitions
- `xfs_name_dotdot` and `xfs_name_dot` are exported canonical directory names.
- `xfs_dir2_samename` compares two `struct xfs_name` values by length and bytes.
- `enum xfs_dir2_fmt` enumerates shortform, block, leaf, node, and error formats.
- `struct xfs_dir_update_params`, `struct xfs_dir_hook`, and hook helpers are available under `CONFIG_XFS_LIVE_HOOKS`.
- `struct xfs_dir_update` packages parent directory, entry name, child inode, and optional parent-pointer args for high-level directory updates.

## Exported API
- Mount/startup: `xfs_dir_startup`, `xfs_da_mount`, and `xfs_da_unmount`.
- Core operations: `xfs_dir_init`, `xfs_dir_createname`, `xfs_dir_lookup`, `xfs_dir_removename`, `xfs_dir_replace`, and `xfs_dir_canenter`.
- Args-based dispatchers: `xfs_dir_lookup_args`, `xfs_dir_createname_args`, `xfs_dir_removename_args`, and `xfs_dir_replace_args`.
- Conversion/shrink/data operations: `xfs_dir2_sf_to_block`, `xfs_dir2_shrink_inode`, data free-space logging and allocation helpers, data/leaf/block header checks, and buffer ops declarations.
- High-level child updates: `xfs_dir_create_child`, `xfs_dir_add_child`, `xfs_dir_remove_child`, `xfs_dir_exchange_children`, and `xfs_dir_rename_children`.

## Conversion Helpers
The header provides inline conversions among directory byte offsets, dataptrs, logical directory blocks, DA blocks, and block offsets. These helpers encode the XFS directory address model where data, leaf, and free spaces are separated by large logical offsets.

## Other Helpers
- `xfs_dir2_block_tail_p` and `xfs_dir2_leaf_tail_p` compute tail pointers from geometry and block base addresses.
- `XFS_READDIR_BUFSIZE` provides the estimated user buffer size for readdir mapping/readahead heuristics.
- `xfs_ascii_ci_need_xfrm` and `xfs_ascii_ci_xfrm` implement legacy ASCII/Latin uppercase folding for ascii-ci directory hash/compare behavior.

## Dependencies
The header includes `xfs_da_format.h` and `xfs_da_btree.h`, making directory APIs tightly connected to the shared DA format and btree abstractions.

## Research Notes
This header is the public directory contract for libxfs. Its most important technical detail is the set of logical address conversion helpers, because directory data, leaf, and free-space blocks all share one file fork but occupy distinct logical spaces.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_block.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_block.c

## Role
`xfs_dir2_block.c` implements XFS single-block directory format operations. In this format, directory data entries and a compact leaf index live together in one directory block.

## Main Responsibilities
- Initialize cached hashes for `.` and `..`.
- Verify, read, initialize, and type single-block directory buffers.
- Add, lookup, remove, and replace entries in block-format directories.
- Manage embedded leaf entries, stale entries, block tails, and data free space.
- Convert block directories to/from shortform and leaf formats.

## Important Functions
- `xfs_dir_startup` precomputes hash values for `.` and `..`.
- `xfs_dir3_block_verify`, read/write verifiers, and `xfs_dir3_block_buf_ops` validate magic, CRC metadata, LSN, UUID, block number, and internal data layout.
- `xfs_dir3_block_read` reads the single directory data block, checks owner metadata for v3 blocks, marks sick state on corruption, and sets transaction buffer type.
- `xfs_dir3_block_init` stamps v2 or v3 block headers and initializes verification metadata.
- `xfs_dir2_block_need_space` determines whether a new data entry can fit by reusing stale leaf entries, using bestfree space, or compacting.
- `xfs_dir2_block_compact` compacts embedded leaf entries while intentionally leaving one stale entry available.
- `xfs_dir2_block_addname` inserts a name by checking space, possibly converting to leaf format, finding the sorted hash position, reusing stale entries or allocating tail leaf space, consuming data free space, writing the dirent, and logging touched ranges.
- `xfs_dir2_block_lookup` and `xfs_dir2_block_lookup_int` binary-search the embedded leaf index by hash and then scan duplicate hashes for an exact or case-insensitive name match.
- `xfs_dir2_block_removename` frees the data entry, marks the leaf index stale, updates bestfree information, and converts to shortform if the result fits in the inode fork.
- `xfs_dir2_block_replace` updates a matched entry's inode number and file type.
- `xfs_dir2_leaf_to_block` converts a single-leaf directory back to block format when all data fits in the first data block and sufficient tail space exists.
- `xfs_dir2_sf_to_block` expands an inode-local shortform directory into an allocated block with `.` and `..` entries, preserved offsets, free holes, and sorted leaf entries.

## Data Layout
- The block starts as a directory data block and ends with `struct xfs_dir2_block_tail`.
- Embedded leaf entries grow backward from the tail area, while directory data entries and unused regions occupy the data area.
- Leaf entries are sorted by hash and point to data entries through directory dataptrs.
- Stale leaf entries are represented by `XFS_DIR2_NULL_DATAPTR`.

## Invariants
- The verifier delegates detailed data layout checking to `__xfs_dir3_data_check`.
- Adds preserve sorted hash order and handle duplicate hashes.
- Directory data entry tags store the entry's starting offset and are logged with the entry.
- Conversion from shortform preserves existing shortform offsets by inserting explicit unused entries where needed.
- Conversion from leaf to block is only allowed when trailing data blocks can be trimmed and the leaf index fits into free space at the end of the first data block.

## Error Handling
- Header or verifier corruption returns `-EFSCORRUPTED`, marks buffers corrupt, and marks the directory data fork sick.
- Space-only checks return `-ENOSPC` without modifying the buffer.
- If a block-format add cannot fit and the caller has a reservation, the directory converts to leaf format and retries through `xfs_dir2_leaf_addname`.

## Dependencies
This file depends on DA buffer reads, directory data free-space helpers, shortform conversion helpers, leaf conversion helpers, transaction range logging, buffer verifier infrastructure, and directory health marking.

## Research Notes
The single-block directory code is a dense in-block allocator plus sorted hash index. Most subtlety comes from balancing three movable areas in one buffer: variable-length dirents, reusable free regions, and a reverse-growing embedded leaf table.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_block.c -->