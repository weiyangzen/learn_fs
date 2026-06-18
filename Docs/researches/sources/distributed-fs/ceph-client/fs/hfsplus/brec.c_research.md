# sources/distributed-fs/ceph-client/fs/hfsplus/brec.c

Purpose: mutates individual HFS+ btree records: insert, remove, split, parent separator update, and height increase. It is the HFS+ counterpart to classic HFS `brec.c` with 16-bit key lengths and attribute-tree handling.

Important APIs and control flow: `hfs_brec_lenoff()` decodes record offsets. `hfs_brec_keylen()` validates record offset and key length against `tree->max_key_len`, using fixed index keys only when variable index keys are absent and the tree is not the attributes tree. `hfs_brec_insert()` inserts into the current leaf or creates a root if empty, splits full nodes, shifts offset/data regions, writes key/payload, increments leaf count, and recursively inserts index records for split nodes. `hfs_brec_remove()` removes records, unlinks empty nodes, recurses into parent records, and updates parent keys for first-record removals. `hfs_bnode_split()` splits approximately half the node into a newly allocated bnode, updates sibling descriptors and leaf tail. `hfs_brec_update_parent()` propagates new separator keys upward, splitting index nodes if needed. `hfs_btree_inc_height()` creates a new root and inserts the old root pointer.

State and persistence: changes btree page data, node descriptors, record offset tables, tree root/depth/leaf count, node links, and dirty state for the btree inode. New nodes come from the btree map; deleted nodes are flagged through bnode unlink.

Dependencies and integration: used by catalog, extents, and attributes code for all persistent btree record mutations. It depends on `bfind.c` strategies, `btree.c` node allocation, and bnode byte helpers.

Risks and test signals: split math is sensitive to descriptor size, record offset table size, and variable key lengths. Tests should force catalog, extents, and attributes splits; root growth; deletion to empty tree; attribute-tree fixed/variable index behavior; and malformed key length rejection.
