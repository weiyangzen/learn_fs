# sources/distributed-fs/ceph-client/fs/hfs/btree.h

Purpose: declares the classic HFS in-memory btree model and the shared btree/bnode/search APIs used across catalog, extent, inode, and mount code.

Important types and APIs: `btree_keycmp` abstracts key ordering for catalog versus extents. `struct hfs_btree` stores superblock, backing inode, comparator, CNID, root/leaf topology, node/free counts, attributes, node size geometry, a tree mutex, and a hash table of cached bnodes. `struct hfs_bnode` stores sibling/parent links, node id, type, height, reference count, flags, page offset, and backing pages. `struct hfs_find_data` carries search and found keys, current node, record index, and key/entry offsets/lengths. The header declares btree open/write/reserve/allocation helpers, bnode read/write/move/cache helpers, record insert/remove helpers, and find/goto/read helpers.

State and persistence: the header itself has no persistence behavior, but its fields mirror persistent btree headers, node descriptors, record offset tables, and btree bitmap records. The `tree_lock` is the main serialization point for btree searches and mutations. `HFS_BNODE_NEW`, `HFS_BNODE_DELETED`, and `HFS_BNODE_ERROR` coordinate cache lifecycle and delayed node freeing.

Dependencies and integration: includes `hfs_fs.h`, which supplies HFS on-disk structures, superblock/inode state, and conversion macros. It is the contract between `btree.c`, `bnode.c`, `bfind.c`, `brec.c`, `catalog.c`, and `extent.c`.

Risks and test signals: incorrect assumptions about `max_key_len`, `node_size_shift`, or record offsets affect all users. Static analysis should verify callers hold the tree mutex around find/mutate sequences and release `hfs_find_data` through `hfs_find_exit()`. Runtime tests should stress bnode cache release under memory pressure and concurrent directory operations.
