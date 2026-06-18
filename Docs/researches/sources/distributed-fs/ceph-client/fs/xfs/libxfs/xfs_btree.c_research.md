# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.c

## Purpose
This file is the generic XFS btree engine.  It supplies block validation, cursor traversal, lookup, insertion, deletion, record update, range query, owner rewrite, cursor cache setup, and shared block allocation helpers for all concrete XFS btree families.  Concrete trees provide `struct xfs_btree_ops` callbacks for record/key interpretation, min/max geometry, root updates, block allocation/freeing, comparisons, and buffer verification; this file implements the common mechanics around those callbacks for AG-rooted, inode-rooted, and in-memory btrees.

## Important APIs, Types, And Functions
The primary entry points are `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_update`, `xfs_btree_get_rec`, `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_change_owner`, `xfs_btree_new_iroot`, `xfs_btree_alloc_metafile_block`, and `xfs_btree_free_metafile_block`.

Validation helpers split by pointer format and root type: `__xfs_btree_check_fsblock`, `__xfs_btree_check_memblock`, and `__xfs_btree_check_agblock` validate magic, level, record count, CRC-era UUID/block-number/owner metadata, and sibling pointers.  `xfs_btree_fsblock_verify`, `xfs_btree_agblock_verify`, and `xfs_btree_memblock_verify` are verifier-facing helpers.  CRC helpers integrate with buffer log items and `xfs_buf_update_cksum`.

Layout helpers such as `xfs_btree_rec_addr`, `xfs_btree_key_addr`, `xfs_btree_high_key_addr`, and `xfs_btree_ptr_addr` compute 1-based addresses inside a btree block using operation-provided key, pointer, and record lengths.  They understand overlapping interval trees, where each node pointer has low and high keys.

Mutation helpers include `xfs_btree_lshift`, `xfs_btree_rshift`, `__xfs_btree_split`, `xfs_btree_new_root`, `xfs_btree_insrec`, `xfs_btree_delrec`, `xfs_btree_kill_root`, and inode-root promotion/demotion helpers.  They form the balancing logic for public insert/delete operations.

## Control Flow
Lookup initializes a root pointer, descends from root to leaf, binary-searches each block with `cmp_key_with_cur`, validates child pointers, and adjusts the leaf cursor for EQ, LE, or GE semantics.  Iteration moves within a block when possible; otherwise it climbs to a movable parent, descends into the adjacent subtree, and updates per-level cursor slots.

Insertion generates a record from `cur->bc_rec`, inserts from leaf upward, and handles full blocks by enlarging inode roots, promoting inode roots, shifting to siblings, splitting blocks, or creating a new root.  Deletion removes the selected entry, shifts contents, updates keys, borrows from siblings, joins blocks, and shrinks roots when possible.

Range query uses a simple LE-and-scan path for non-overlapping btrees and a depth-first low/high-key pruning algorithm for overlapping interval btrees.

## State And Persistence Behavior
The central state is `xfs_btree_cur`: transaction, mount, ops, current record, height, root-specific data, private accounting, and per-level buffer/pointer/read-ahead slots.  On-disk changes persist through transaction logging of exact header/key/pointer/record byte ranges; inode-root changes log the inode fork.  AG roots update through `ops->set_root`; staged roots update fake structures; memory btrees route to xmbuf targets.

## Dependencies And Integration Points
This file integrates allocation, inode allocation, bmap, rmap, refcount, realtime btrees, quota/metafile, online repair, transaction, buffer, health, and tracing code.  It relies on `xfs_btree.h`, concrete `xfs_btree_ops`, buffer verifiers, endian helpers, `xfs_trans_*`, allocation/free APIs, group/perag helpers, staging fake roots, and memory-btree xmbuf helpers.

## Risks And Test Signals
Risks include 1-based indexing mistakes, root special cases, inode root reallocation, overlapping high-key maintenance, sibling consistency, transaction buffer ownership, and staging misuse.  Strong tests cover root promotion/demotion, split/join, left/right borrowing, overlapped interval queries, cursor duplication, CRC and owner verifier failures, sibling cycles, allocation failures, metafile allocation/free, and xmbuf-backed memory btrees.
