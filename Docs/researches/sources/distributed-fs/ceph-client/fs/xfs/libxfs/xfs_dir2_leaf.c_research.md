# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_leaf.c

## Purpose
`xfs_dir2_leaf.c` implements XFS leaf-format directories. Leaf-format directories store names in data blocks and keep a single leaf1 block containing sorted hash entries plus a tail-side bestfree table for all data blocks. The file also handles transitions between block, leaf, and node formats as directory size changes.

## Important APIs, Types, and Functions
Key public functions include `xfs_dir2_leaf_hdr_from_disk`, `xfs_dir2_leaf_hdr_to_disk`, `xfs_dir3_leaf_check_int`, `xfs_dir3_leaf_read`, `xfs_dir3_leafn_read`, `xfs_dir3_leaf_get_buf`, `xfs_dir2_block_to_leaf`, `xfs_dir2_leaf_addname`, `xfs_dir3_leaf_compact`, `xfs_dir3_leaf_compact_x1`, `xfs_dir3_leaf_log_ents`, `xfs_dir3_leaf_log_header`, `xfs_dir2_leaf_lookup`, `xfs_dir2_leaf_removename`, `xfs_dir2_leaf_replace`, `xfs_dir2_leaf_search_hash`, `xfs_dir2_leaf_trim_data`, and `xfs_dir2_node_to_leaf`. The central abstraction is `struct xfs_dir3_icleaf_hdr`, an in-core header that hides v4/v5 on-disk header layout differences and points at the on-disk leaf entries.

## Control Flow
Leaf buffer reads use `xfs_dir3_leaf_read` for leaf1 blocks and `xfs_dir3_leafn_read` for node leaf blocks. The verifier checks DA block metadata, decodes the leaf header, validates entry bounds, verifies hash ordering and stale counts under expensive checking, and applies v5 owner checks outside the generic verifier.

`xfs_dir2_block_to_leaf` grows the directory into the leaf range, initializes a leaf1 block, copies the block-format leaf entries to it, turns the original block into a pure data block, frees the former inline leaf/tail area, and initializes the leaf bests table from the data block bestfree value. `xfs_dir2_leaf_addname` reads the leaf, finds the hash insertion point, tries same-hash data blocks first, scans the bests table for space, allocates and initializes a data block if needed, consumes data-block free space, writes the new dirent, updates the leaf bests entry, inserts or reuses a leaf entry, and logs all touched leaf/data regions. If the leaf block cannot hold the metadata, it converts to node form and retries through `xfs_dir2_node_addname`.

Lookup is handled by `xfs_dir2_leaf_lookup_int`, which binary-searches the sorted hash table, walks equal-hash entries, reads data blocks lazily as the data block number changes, and preserves case-insensitive matches while looking for exact matches. Removal marks the leaf entry stale, frees the data entry, updates the leaf bests table, may remove empty data blocks, and then tries `xfs_dir2_leaf_to_block`. Replacement changes only the data entry inode/filetype and logs that entry.

`xfs_dir2_node_to_leaf` is the down-conversion from node to leaf when the node root is a single leafn and the separate free-space block can fit back into a leaf1 tail. It trims trailing empty free blocks, verifies only one leaf remains, copies free-space bests into the leaf tail, changes the magic and buffer type, frees the free-space block, and may further convert to block format.

## State and Persistence
Persistent leaf state includes sorted hash/address entries, stale entry count, v5 DA metadata, forward/back sibling fields for leafn, leaf1 tail `bestcount`, and the leaf1 bests table. Data block mutations are delegated to `xfs_dir2_data_*`. Leaf mutations are persisted via `xfs_trans_log_buf` ranges for headers, entries, tail, and bests. Buffer ops assign leaf1 or leafn type so log recovery and verifiers interpret the block correctly.

## Dependencies and Integration Points
This file integrates with data-block free-space code, `xfs_dir2_block.c` for block conversion, `xfs_dir2_node.c` for node conversion and leafn behavior, DA btree buffer reading, geometry helpers, tracing, transaction logging, and directory health marking. Case-insensitive lookup support is delegated to `xfs_dir2_compname` and `xfs_dir_cilookup_result`.

## Risks and Test Signals
Risk centers on preserving sorted hash order while reusing stale entries, keeping leaf bests synchronized with data bestfree, and handling conversion thresholds without leaking or misclassifying buffers. Another subtle area is case-insensitive lookup state when multiple equal hashes span different data blocks. Good tests include repeated create/unlink cycles in one directory, hash-collision workloads, no-space-reservation conversion failures, fsstress format churn between block/leaf/node forms, and corruption tests for stale counts, bestcount, owner, and CRC.
