# sources/distributed-fs/ceph-client/fs/hfsplus/bfind.c

Purpose: implements HFS+ btree search cursors, binary search strategies, record reads, record-relative movement, and catalog record size validation.

Important APIs and control flow: `hfs_find_init()` allocates paired search/current key buffers sized from `tree->max_key_len`, records the tree, and locks the tree mutex with a tree-specific lock class. `hfs_find_exit()` drops the current bnode, frees keys, and unlocks. `hfs_find_1st_rec_by_cnid()` is a strategy for locating the first record with a matching CNID in extents, catalog, or attributes trees. `hfs_find_rec_by_key()` is exact comparator-based search. `__hfs_brec_find()` performs binary search within one bnode and fills offsets/lengths. `hfs_brec_find()` traverses root-to-leaf through index records, validating node type/height. `hfs_brec_read()` combines find and payload copy. `hfs_brec_goto()` moves forward/backward across linked leaf nodes. `hfsplus_brec_read_cat()` reads a catalog entry and validates exact record size based on type, including variable thread size.

State and persistence: no direct writes. It establishes in-memory cursor state used by mutators and readers. The tree mutex serializes concurrent operations while a cursor is active.

Dependencies and integration: depends on bnode read helpers, tree comparators configured by `btree.c`, and HFS+ raw catalog structures. Catalog, extents, attributes, directory, and inode code all build keys then use this search layer.

Risks and test signals: bad key lengths or malformed record offsets propagate as `-EINVAL`/`-EIO`; caller cleanup must always invoke `hfs_find_exit()`. Tests should cover malformed catalog thread sizes, movement across leaf boundaries, first-by-CNID searches with multiple attrs, and invalid index height/type.
