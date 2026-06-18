# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_node.c

## Purpose
`xfs_dir2_node.c` implements node-format XFS directories. Node-format directories scale beyond a single leaf block by using DA btree leafn blocks for sorted hash entries and separate free-space blocks that summarize the largest free region in each data block. It also owns conversion between leaf and node forms, leafn split/join helpers, and free-space block lifecycle.

## Important APIs, Types, and Functions
Public functions include `xfs_dir2_free_hdr_from_disk`, `xfs_dir2_leaf_to_node`, `xfs_dir2_leaf_lasthash`, `xfs_dir2_leafn_lookup_int`, `xfs_dir2_leafn_order`, `xfs_dir2_leafn_split`, `xfs_dir2_leafn_toosmall`, `xfs_dir2_leafn_unbalance`, `xfs_dir2_node_addname`, `xfs_dir2_node_lookup`, `xfs_dir2_node_removename`, `xfs_dir2_node_replace`, `xfs_dir2_node_trim_free`, and `xfs_dir2_free_read`. Internal helpers map data block numbers to free-space block numbers and indexes, verify free-space blocks, allocate free/data blocks, rebalance leafn entries, and update free-space accounting after removals.

## Control Flow
Free-space buffer IO is handled through `xfs_dir3_free_buf_ops`; read paths verify magic/CRC/UUID/blkno/LSN and then validate `firstdb`, `nvalid`, `nused`, and owner through `xfs_dir3_free_header_check`. `xfs_dir2_free_read` requires a present block, while `xfs_dir2_free_try_read` allows holes for sparse free-space ranges.

`xfs_dir2_leaf_to_node` allocates the first free-space block, copies the leaf1 bests table into it, counts used entries, logs the new free block, and changes the old leaf1 block to a leafn block. `xfs_dir2_node_addname` allocates a DA lookup state, performs `xfs_da3_node_lookup_int` to find the insertion leaf and possibly a useful free-space block, writes the data entry through `xfs_dir2_node_addname_int`, and inserts the leaf entry with `xfs_dir2_leafn_add`. If the target leaf cannot fit, DA split machinery calls `xfs_dir2_leafn_split`, which creates another leafn block, rebalances entries, links siblings, and inserts into the selected leaf.

`xfs_dir2_node_addname_int` first calls `xfs_dir2_node_find_freeblk` to reuse a data block with enough free space or discover that allocation is needed. Allocation goes through `xfs_dir2_node_add_datablk`, which initializes a data block and creates or extends the corresponding free-space block. The new dirent consumes data free space via `xfs_dir2_data_use_free`, updates the free-space bests entry, and returns the data block and offset to the caller so the leaf entry can point at it.

Lookup paths are split by operation mode. For addname, `xfs_dir2_leafn_lookup_for_addname` searches equal-hash entries and returns a free-space block if it finds room near a same-hash data block. For ordinary lookup/remove/replace, `xfs_dir2_leafn_lookup_for_entry` reads data blocks, compares names, tracks case-insensitive matches, and stores the matched data block in `state->extrablk`.

Removal uses `xfs_dir2_leafn_remove` to mark the leaf entry stale, free the data entry, update the corresponding free-space block, remove empty data blocks where possible, and tell the DA layer whether a join is worthwhile. `xfs_dir2_node_removename` then fixes btree hash values, joins underfull leaves, and attempts `xfs_dir2_node_to_leaf`. `xfs_dir2_node_trim_free` removes trailing empty free-space blocks.

## State and Persistence
Persistent state spans data blocks, leafn blocks, DA internal nodes, and free-space blocks. Free-space headers record the first represented data block, valid entry count, and used entry count; `bests[]` entries are either `NULLDATAOFF` or the largest free extent in a data block. All changes are transaction-logged through leaf/data/free log helpers, and buffer types are set to `XFS_BLFT_DIR_FREE_BUF` or `XFS_BLFT_DIR_LEAFN_BUF` for recovery.

## Dependencies and Integration Points
The file depends on DA btree lookup/split/join/path-shift functions, bmap helpers for last offsets, directory geometry conversions, `xfs_dir2_data.c` for data-block mutation, `xfs_dir2_leaf.c` for shared leaf helpers and node-to-leaf conversion, transaction logging, and health/corruption reporting. It is the scalability layer underneath VFS directory operations routed through higher-level XFS directory code.

## Risks and Test Signals
Subtle risks include mismatches between data block numbers and free-space block positions, stale leaf entries distorting split/join thresholds, free-space holes during no-space-reservation operations, and failure to update ancestor hash values after insertion/removal. Tests should stress huge directories, hash collisions, repeated add/remove under ENOSPC injection, sparse free-space block trimming, DA split/join recovery, and scrub detection for invalid `firstdb`, `nvalid`, `nused`, stale counts, and data/free summary mismatches.
