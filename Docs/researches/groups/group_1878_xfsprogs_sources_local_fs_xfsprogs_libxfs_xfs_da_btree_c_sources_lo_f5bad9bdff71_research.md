# Group Research: group_1878_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_da_btree_c_sources_lo_f5bad9bdff71

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/xfsprogs`. All listed files were read completely. Line/byte counts matched the work item manifest.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.c

## Purpose

`xfs_da_btree.c` implements the shared directory/attribute B-tree engine for libxfs. It manages dir/attr state objects, da node verification, buffer mapping, tree lookup, node/leaf split and join propagation, sibling link maintenance, directory/attribute block allocation, and hash-name comparison.

## Main Behavior

The file normalizes v2/v3 da node headers with `xfs_da3_node_hdr_from_disk` and `xfs_da3_node_hdr_to_disk`, verifies CRC-enabled metadata fields, and provides read/write buffer ops that can redirect leaf-level blocks to attr or directory leaf verifiers when a node read lands on a leaf. `xfs_da3_header_check` dispatches owner/header checks for attr leaves, da nodes, and directory leaf blocks.

Tree growth centers on `xfs_da3_split`. It walks upward from a split attr or dir leaf, inserts the new child into parent nodes, splits full intermediate nodes, handles attr double-split extra blocks, updates parent hash values, and calls `xfs_da3_root_split` when the root must grow. Root splitting copies the old root to a newly allocated block and creates a fresh root containing two child pointers.

Tree shrinking centers on `xfs_da3_join`. It walks upward from a too-small or empty leaf/node, coalesces with siblings when possible, unlinks and frees dropped blocks, repairs hash paths, and collapses a single-child root through `xfs_da3_root_join`. Node helpers rebalance entries, remove entries, unbalance into a surviving sibling, and keep the last hash value propagated up the path.

Lookup is performed by `xfs_da3_node_lookup_int`, which descends from the root using binary search over node hash entries, validates tree level consistency and owner metadata, handles duplicate hashes, and delegates final leaf lookup to attr or dir leaf code. If a leaf ends at the searched hash and the item is not found, it shifts to the next leaf with `xfs_da3_path_shift` to continue duplicate-hash search.

The allocation layer maps logical da blocks through the inode fork, rejects holes or delayed mappings unless explicitly allowed, and provides get/read/readahead helpers. `xfs_da_grow_inode_int` allocates new metadata blocks, falling back from contiguous to fragmented mappings when needed. `xfs_da_shrink_inode` unmaps dead blocks; for directory data fork ENOSPC cases, `xfs_da3_swap_lastblock` moves the last da block into the removed block’s position and repairs siblings and parent pointers.

## Dependencies and Risks

This file is tightly coupled to bmap mapping/unmapping, transaction logging, buffer verification, attr leaf code, dir leaf code, inode fork geometry, health marking, and the on-disk format definitions in `xfs_da_format.h`. High-risk areas are duplicate-hash traversal, root split/join copy semantics, sibling pointer updates, parent hash repair, owner/CRC verifier dispatch, ENOSPC block swapping, and any mismatch between logical da block numbers and physical buffer mappings.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.h

## Purpose

`xfs_da_btree.h` declares the shared data structures and APIs for XFS directory and attribute B-tree operations.

## Key Contents

The header defines `struct xfs_da_geometry`, which captures block size, filesystem block count, log shifts, node/leaf/free block geometry, dir section block numbers, max extents, and data-entry offsets for both directory and attribute forks.

`struct xfs_da_args` is the central operation context for directory and xattr operations. It carries names, values, inode/transaction pointers, owner, inode number, file type, operation flags, attr namespace filters, hashes, reservation totals, fork selector, current block/index state, remote attr value state, secondary attr replace state, and comparison result.

The state structures `xfs_da_state_blk`, `xfs_da_state_path`, and `xfs_da_state` track the active descent path, alternate path for joins, split target information, and extra split blocks. `struct xfs_da3_icnode_hdr` is the in-core abstraction for legacy and CRC-enabled da node headers.

The exported APIs cover node creation, split/join, hash-path repair, node lookup/path shifting, sibling linking, node reads, inode grow/shrink, buffer get/read/readahead, buffer copy, name hashing/comparison, state allocation/reset/free, header conversion, and header verification.

## Dependencies and Risks

Callers must initialize `xfs_da_args` consistently with mount geometry, fork type, owner, transaction, and operation flags. The main invariants are correct path depth tracking, hash ordering, block ownership, and preserving the distinction between directory data fork geometry and attribute fork geometry.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_format.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_format.h

## Purpose

`xfs_da_format.h` defines the shared on-disk formats for XFS directory/attribute blocks, da B-tree nodes, directory data/leaf/free blocks, attribute leaves, remote attributes, and parent pointer records.

## Key Contents

The header defines legacy and CRC-enabled magic numbers for da nodes, attr leaves, directory leaf blocks, directory data/block/free blocks, and remote attr blocks. `xfs_da_blkinfo` and `xfs_da3_blkinfo` provide common sibling-link and metadata-verification headers used by da nodes, attr leaves, and dir leaves.

For da nodes, it defines legacy/v3 node headers, node entries, flexible-array node blocks, maximum tree depth, and CRC offset. For directories, it defines shortform directory headers and entries, inode-number size rules, data block alignment, data/free entry structures, v2/v3 data headers, directory leaf headers/entries/tails, free-space blocks, and single-block directory tails and embedded leaf entry accessors.

For attributes, it defines shortform attr headers/entries, attr leaf headers, leaf entry records, local and remote name/value records, v3 attr leaf headers, namespace and state flags, on-disk masks, and entry-size helpers that preserve historical flexible-array padding semantics. It also defines remote attr block headers and the parent pointer record containing parent inode and generation.

## Dependencies and Risks

This header is the ABI for on-disk metadata. Risks are mostly layout-related: changing structure size, alignment, magic values, padding assumptions, or entry-size formulas would break compatibility. The attr entry-size helpers deliberately encode historical padding behavior, and the v3 structures rely on common leading fields so generic da code can manipulate sibling links safely across v2/v3 formats.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_da_format.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_defer.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_defer.c

## Purpose

`xfs_defer.c` implements XFS deferred operation orchestration: grouping work items, logging intent and done items, rolling transactions, replaying recovered intents, capturing deferred state during recovery, preserving held resources across rolls, and managing deferred-operation caches.

## Main Behavior

Deferred work is tracked in `xfs_defer_pending` records grouped by operation type. Work enters a transaction’s deferred list, gets batched up to the op type’s `max_items`, and later has an intent item logged before the transaction rolls. Finishing creates a done item, calls the operation type’s `finish_item` callback for each work item, and frees the pending record when complete.

`xfs_defer_finish_noroll` is the main engine. It repeatedly creates intents for intake work, isolates paused items, moves work to a pending list, rolls when intents exist, relogs older intents so they do not pin the log tail, and finishes one pending item at a time. If a callback returns `-EAGAIN`, the unfinished work item is put back, a replacement intent is logged, and processing continues in a fresh transaction. Fatal errors abort intents, cancel work, and force shutdown.

The file preserves resources that must survive transaction rolls. `xfs_defer_save_resources` records held buffers and inodes from transaction items; `xfs_defer_restore_resources` rejoins and reholds them after a roll. Recovery support can capture a chain of deferred ops with block/log reservations and held resources, commit it, then continue it later via `xfs_defer_ops_continue`.

It also provides barrier deferred ops to prevent adjacent work from being merged, APIs to add/cancel/move deferred work, start/cancel/finish recovery work, pause/unpause items, release captured resources, and initialize/destroy caches for defer, rmap, refcount, bmap, extent-free, attr, and exchange-mapping intent items.

## Dependencies and Risks

This file depends on transaction internals, log items, AIL/log-tail behavior, btree cursors, rmap/refcount/bmap/attr/exchmaps intent modules, inode and buffer locking, and shutdown semantics. Risky areas are intent/done atomicity across transaction rolls, `-EAGAIN` continuation correctness, preserving enough reservation to log replacement intents, resource hold/rejoin ordering, recovery capture lifetime, and paused items delaying dependent work.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_defer.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_defer.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_defer.h

## Purpose

`xfs_defer.h` declares the data structures and APIs for XFS deferred operations and log intent/done orchestration.

## Key Contents

`struct xfs_defer_pending` tracks one batch of deferred work: list linkage, work item list, intent and done log items, operation type, item count, and flags. `XFS_DEFER_PAUSED` marks work that has an intent but should not be finished yet.

`struct xfs_defer_op_type` describes a deferred operation implementation with callbacks to create/abort intents, create done items, finish/cancel work items, clean up per-finish state, recover work, and relog intents. The header declares the concrete defer types for bmap, refcount, realtime refcount, rmap, realtime rmap, extent free, AGFL free, realtime extent free, attr, and exchange mapping work.

`struct xfs_defer_resources` captures held buffers and inodes across transaction rolls. `struct xfs_defer_capture` stores detached deferred-op state, transaction flags, block reservations, log reservation, and held resources so recovery can commit and resume work later.

The exported APIs add work, finish/cancel/move deferred ops, finish a single pending item, capture/continue/abort recovery chains, release captured resources, start/cancel/finish recovery work, initialize/destroy item caches, pause/unpause items, and add merge barriers.

## Dependencies and Risks

The header ties together transactions, log items, btree cursors, buffers, inodes, and operation-specific intent modules. Correct use requires permanent log reservations, valid callback tables, and careful ownership of captured buffers/inodes across transaction commit and recovery continuation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_defer.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2.c

## Purpose

`xfs_dir2.c` provides the high-level XFS directory API and format dispatcher for libxfs. It initializes directory/attribute geometry, validates inode numbers and names, routes operations to shortform/block/leaf/node implementations, and implements child link, unlink, rename, and exchange workflows including parent pointer updates.

## Main Behavior

Mount setup builds directory and attribute `xfs_da_geometry` from the superblock. Directory geometry includes block/leaf/free/data header sizes, section boundaries, node fanout, max extents, and first data-entry offset. Attribute geometry uses filesystem block size and shares node header sizing.

The basic directory API allocates and populates `xfs_da_args` for create, lookup, remove, replace, and can-enter checks. `xfs_dir2_format` classifies a directory as shortform, block, leaf, or node from inode fork format, file size, and bmap EOF, then the `*_args` dispatchers call the appropriate backend. Lookup supports ASCII case-insensitive filesystems by returning the actual matched name when requested.

Utility functions grow and shrink directory data/free blocks, update `i_disk_size`, validate names against length, slash, and NUL constraints, and switch hashing/comparison between normal and ASCII-CI behavior. Optional live hooks notify online fsck-like consumers of directory entry updates.

Higher-level child operations combine directory entry updates with inode link counts, timestamps, parent pointer xattrs, unlinked-list cleanup for tmpfile/whiteout cases, and `..` updates for directories. `xfs_dir_create_child`, `xfs_dir_add_child`, and `xfs_dir_remove_child` implement link/unlink semantics. `xfs_dir_exchange_children` swaps two existing entries and adjusts directory parents/link counts. `xfs_dir_rename_children` handles target replacement or creation, cross-directory moves, whiteouts, parent pointer changes, and update hooks.

## Dependencies and Risks

This file depends on all directory format backends, bmap growth/shrink, transactions, inode locking/link counts, parent pointers, allocation groups, unlinked-list handling, and optional live hooks. Risks include dispatching based on corrupt directory size/EOF, case-insensitive duplicate handling, link count updates for cross-directory renames, `..` replacement ordering, no-reservation ENOSPC behavior, whiteout/tmpfile state transitions, and keeping parent pointer attr updates atomic with dirent changes.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2.h

## Purpose

`xfs_dir2.h` declares the public directory interfaces, directory geometry helpers, format classifiers, buffer ops, conversion helpers, and inline offset/name utilities for XFS v2/v3 directories.

## Key Contents

The header exposes dot and dotdot names, same-name comparison, directory format enum, mode-to-filetype conversion, mount startup/teardown, high-level create/lookup/remove/replace/canenter APIs, `xfs_da_args` variants, shortform-to-block conversion, directory block shrink, data-block free-space helpers, inode validation, block/leaf/free/data buffer ops, and v3 header checks.

It provides inline conversions among directory byte offsets, dataptrs, logical directory blocks, and da blocks. It also defines tail and leaf-array accessors for block and leaf formats, the readdir buffer size estimate, filetype extraction, data end offset, and name validation.

ASCII-CI helpers fold selected ASCII/Latin-1 uppercase byte ranges for historical case-insensitive directory hashing. Optional live hook declarations allow directory update notification. The parent-pointer-aware `xfs_dir_update` APIs declare create/add/remove/exchange/rename child workflows.

## Dependencies and Risks

Most helpers assume geometry fields are already initialized and that offsets are aligned to directory data alignment. Incorrect conversion between dataptr, db, da, and byte offsets would corrupt directory metadata. Callers must also respect filetype feature availability, owner checks, and parent pointer argument lifetime.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_block.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_block.c

## Purpose

`xfs_dir2_block.c` implements single-block XFS directory operations: block verification, lookup, add, remove, replace, conversion from shortform to block, and conversion from leaf back to block.

## Main Behavior

The file initializes cached hashes for `.` and `..`, defines v2/v3 block buffer ops, verifies magic, CRC, uuid, physical block number, log sequence number, owner, and full data-block structure, and stamps v3 block headers during initialization.

A block directory stores data entries at the front and an embedded sorted leaf array plus tail at the end. `xfs_dir2_block_addname` reads the only block, determines whether data and leaf space exist, reuses stale leaf entries when possible, compacts stale entries when useful, or converts to leaf format when the block cannot fit another entry. Insertions binary-search the hash position, allocate data-entry space from bestfree, fill inode/name/filetype/tag fields, update the embedded leaf entry, log affected ranges, and validate the result.

`xfs_dir2_block_lookup_int` binary-searches the embedded leaf array by hash, scans duplicate hashes, skips stale entries, compares names with normal or ASCII-CI comparison, and preserves a case-insensitive match while continuing to look for an exact match. Public lookup returns inode number, filetype, and optional actual CI name.

Removal finds the entry, frees the data-entry space, marks the leaf entry stale with `XFS_DIR2_NULL_DATAPTR`, updates tail stale count, rescans bestfree if needed, and converts back to shortform when the resulting directory fits in the inode. Replacement changes the inode number and filetype in place.

`xfs_dir2_leaf_to_block` compacts a single-leaf directory back into block format when only the first data block remains and the embedded leaf/tail area fits. It trims trailing empty data blocks, initializes the data block as a block directory, copies non-stale leaf entries, frees the old leaf block, and may then shrink further to shortform. `xfs_dir2_sf_to_block` converts inline shortform directories into a new block: it allocates block zero, creates `.` and `..`, preserves existing shortform offsets by inserting free holes, copies all entries, builds and sorts the embedded leaf array, and logs the block.

## Dependencies and Risks

This file depends on data-block free-space management, shortform helpers, leaf-format conversion helpers, da block allocation/shrink, transaction logging, CRC buffer ops, directory hashing/comparison, and geometry offset helpers. Risks include stale leaf compaction boundaries, bestfree consistency after split/free operations, preserving shortform offsets during conversion, duplicate-hash lookup order, no-reservation conversion failures, and ensuring block-to-shortform decisions use exact packed size calculations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_block.c -->