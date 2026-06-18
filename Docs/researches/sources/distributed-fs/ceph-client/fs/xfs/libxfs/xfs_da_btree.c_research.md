# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.c

## Purpose
`xfs_da_btree.c` implements the shared directory/attribute btree machinery for XFS "DA" blocks: hashed-name btree search, split, join, sibling linkage, block allocation/removal, logical-to-physical buffer mapping, and v2/v3 metadata verification for directory leaf, attribute leaf, and intermediate node blocks.

## Important APIs, Types, And Functions
The file exports state lifetime helpers `xfs_da_state_alloc()`, `xfs_da_state_reset()`, and `xfs_da_state_free()`, backed by `xfs_da_state_cache`. Header conversion helpers `xfs_da3_node_hdr_from_disk()` and `xfs_da3_node_hdr_to_disk()` abstract v2 versus CRC-enabled v3 node headers. Verification entry points include `xfs_da3_blkinfo_verify()`, `xfs_da3_node_header_check()`, `xfs_da3_header_check()`, and `xfs_da3_node_buf_ops`.

Tree mutation APIs include `xfs_da3_node_create()`, `xfs_da3_split()`, `xfs_da3_join()`, `xfs_da3_fixhashpath()`, `xfs_attr3_node_entry_remove()`, `xfs_da3_blk_link()`, and `xfs_da3_path_shift()`. Lookup is implemented by `xfs_da3_node_lookup_int()`, which descends the btree and delegates leaf matching to attr or dir leaf code. Storage utilities include `xfs_da_grow_inode_int()`, `xfs_da_grow_inode()`, `xfs_da_shrink_inode()`, `xfs_da_get_buf()`, `xfs_da_read_buf()`, and `xfs_da_reada_buf()`. `xfs_da_hashname()` and `xfs_da_compname()` provide the default name hash and exact comparison functions.

## Control Flow
Lookup starts at `args->geo->leafblk`, reads each node through `xfs_da3_node_read()`, verifies owner/header state, binary-searches sorted hash entries, and descends until an attr or directory leaf is found. Duplicate hashes are handled by choosing the first matching key and, if a leaf ends with the searched hash, shifting forward with `xfs_da3_path_shift()` to inspect adjacent leaves.

Splitting walks upward from the leaf path. Attribute leaves can double-split via `state->extrablk`; directory leaves split once. Intermediate nodes either absorb new child entries or allocate a new node, rebalance entries, link siblings, and propagate hash updates. If propagation reaches above the root, `xfs_da3_root_split()` copies block zero to a new block and creates a new root with two child pointers.

Joining walks upward after deletion. Leaf or node "too small" checks decide whether to do nothing, coalesce into a sibling, or unlink an empty block. `xfs_da3_root_join()` collapses a root with a single child by copying that child into block zero. Shrinking removes extents; if directory bunmap fails with `-ENOSPC`, `xfs_da3_swap_lastblock()` moves the last DA block into the dead block slot so the tail extent can be removed.

## State And Persistence
Persistent state is the inode's directory or attr fork mappings and the on-disk DA blocks. Mutations log precise byte ranges with `xfs_trans_log_buf()`, mark buffer types for recovery, stamp v3 owner/uuid/block-number fields, and update CRCs during write verification. In-memory state in `struct xfs_da_state` carries active and alternate paths, child block metadata, and extra split state. Corruption paths mark the directory/attribute fork sick through health helpers.

## Dependencies And Integration Points
This file depends on bmap mapping/allocation (`xfs_bmapi_write`, `xfs_bmapi_read`, `xfs_bunmapi`), transactions and buffer logging, XFS buffer verifiers, dir leaf/block code, attr leaf code, mount geometry from `xfs_da_mount()`, tracepoints, error injection, and metadata health reporting. It is the common btree backend used by `xfs_dir2_leaf.c`, `xfs_dir2_node.c`, and attribute leaf/node code.

## Risks
Major risks are stale or unsorted hash propagation, sibling link corruption during split/join, owner/CRC verification gaps on v3 filesystems, incorrect block movement in `xfs_da3_swap_lastblock()`, and mapping holes being treated as valid metadata. The code depends on active transaction ownership and inode locks held by callers; violations can corrupt logged metadata. Duplicate hashes and case-insensitive lookup paths are especially sensitive because search must continue across leaf boundaries.

## Test Signals
Useful tests include directory and xattr workloads that force leaf splits, node splits, root splits, joins, root collapse, duplicate-hash names, case-insensitive lookups, no-space deletion that triggers last-block swapping, fragmented DA block mappings, v3 CRC/owner mismatch injection, read verifier format switching between node and leaf blocks, and recovery after crashes between intent/logged DA updates.
