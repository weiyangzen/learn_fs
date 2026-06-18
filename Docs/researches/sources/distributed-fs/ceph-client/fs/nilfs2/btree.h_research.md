# sources/distributed-fs/ceph-client/fs/nilfs2/btree.h

## Purpose
`btree.h` declares the B-tree block-map interface and layout constants shared by the NILFS bmap layer and the implementation in `btree.c`.

## Important APIs and types
- `struct nilfs_btree_path` is the per-level operation context. It owns current and sibling node buffers, child indices, old/new pointer allocation requests, a btnode key-change context, and the rebalance callback selected by prepare logic.
- Root and non-root child-capacity macros derive the maximum and minimum number of children from `NILFS_BMAP_SIZE`, `struct nilfs_btree_node`, and block size.
- `NILFS_BTREE_KEY_MIN` and `NILFS_BTREE_KEY_MAX` define the full 64-bit key range.
- `nilfs_btree_path_cache` is the slab cache used for path arrays.
- Public functions: `nilfs_btree_init()`, `nilfs_btree_convert_and_insert()`, `nilfs_btree_init_gc()`, and `nilfs_btree_broken_node_block()`.

## Control flow and state behavior
The path type mirrors B-tree traversal from data level through internal node levels. Prepare stages populate pointer requests and rebalance callbacks; commit stages replay those callbacks upward. Header constants describe both root nodes stored in inode bmap data and non-root nodes stored in btnode buffers.

## Dependencies and integration points
The header includes on-disk `nilfs_btree_node`, `btnode.h`, and `bmap.h`. It is consumed by normal bmap initialization, direct-to-B-tree conversion, GC inode initialization, and validation of node buffers read for GC.

## Risks and test signals
Changing any capacity macro changes tree fanout and can invalidate on-disk compatibility. Tests should validate root and non-root capacity calculations for supported block sizes, path allocation initialization, and node-block corruption checks.
