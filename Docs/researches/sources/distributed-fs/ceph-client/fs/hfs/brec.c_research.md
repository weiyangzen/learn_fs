# sources/distributed-fs/ceph-client/fs/hfs/brec.c

Purpose: implements classic HFS B-tree record mutation: record length/key length discovery, insert, remove, node split, parent-key maintenance, and root-height growth. It is the low-level mutator used by catalog and extent trees after `bfind.c` has positioned an `hfs_find_data`.

Important APIs and control flow: `hfs_brec_lenoff()` decodes the trailing record-offset table and returns record span. `hfs_brec_keylen()` handles leaf/index key sizing, including fixed index keys and variable/big-key trees. `hfs_brec_insert()` calculates the aligned key plus payload size, splits the node if the record will not fit, shifts offsets/data, writes key and entry, updates `leaf_count`, then inserts a new index record for split nodes and grows the root with `hfs_btree_inc_height()` when needed. `hfs_brec_remove()` removes the selected record, collapses the payload area and offset table, unlinks empty nodes, and recursively removes parent index records. `hfs_brec_update_parent()` repairs separator keys up the tree when the first key in a child changes.

State and persistence: all structural changes are written through `hfs_bnode_*()` helpers into mapped btree inode pages and mark the relevant pages/inodes dirty. Tree-wide state affected here includes `root`, `depth`, `leaf_head`, `leaf_tail`, and `leaf_count`. New nodes are allocated from the btree bitmap by `hfs_bmap_alloc()`; deleted empty nodes are unlinked and later freed through the bnode lifecycle.

Dependencies and integration: depends on `btree.h`, `hfs_bnode_*`, `__hfs_brec_find()`, and btree bitmap allocation. Catalog operations (`hfs_cat_create/delete/move`) and extent writes (`hfs_ext_write_extent`) rely on this file for all on-disk record updates.

Risks and test signals: node splits and parent-key rewrites are corruption-sensitive. The code has panic-style assumptions for impossible split states and limited rollback after partially successful multi-record catalog operations. Useful tests are fsck-backed create/delete/rename workloads that force leaf and index splits, plus fault injection around `hfs_bmap_alloc()` and bnode read failures.
