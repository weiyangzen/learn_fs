# sources/distributed-fs/ceph-client/fs/hfs/btree.c

Purpose: opens, validates, writes, reserves, allocates, and frees nodes in classic HFS catalog and extents B-trees. It bridges MDB fork metadata into in-memory `struct hfs_btree` state and manages the tree node allocation bitmap.

Important APIs and control flow: `hfs_btree_open()` allocates `struct hfs_btree`, creates/loads the special btree inode for `HFS_EXT_CNID` or `HFS_CAT_CNID`, reads the header node from disk, validates power-of-two node size, node count, and max key length, then configures node geometry. `hfs_btree_close()` releases cached bnodes and the btree inode. `hfs_btree_write()` writes mutable header fields (`root`, leaf links/count, node/free counts, attributes, depth) to node 0. `hfs_bmap_reserve()` extends the btree file by calling `hfs_extend_file()` until enough free nodes exist. `hfs_bmap_alloc()` scans header/map-node bitmap records for a clear bit, sets it, decrements `free_nodes`, and creates the corresponding bnode. `hfs_bmap_free()` clears the bit and increments `free_nodes`.

State and persistence: this file persists btree header records, btree bitmap bits, btree inode size/bytes, and dirty inode state. Growing a btree updates the special btree inode's allocated block counts and `tree->node_count`. Bitmap changes dirty individual pages and the btree inode so writeback can flush them.

Dependencies and integration: depends on `hfs_inode_read_fork()`, `hfs_ext_find_block()`, `hfs_extend_file()`, bnode cache helpers, and the MDB fields loaded by `mdb.c`. It is used by `brec.c` for node allocation and by mount setup for opening catalog/extents trees.

Risks and test signals: header reading manually copies block data into folio 0, so block-size and offset mistakes can corrupt all later tree parsing. Bitmap map-node growth has a `panic("FIXME!!!")` when no free nodes remain in one path. Tests should mount crafted images with bad max key lengths, non-power-of-two node sizes, full btree maps, and forced catalog/extents growth.
