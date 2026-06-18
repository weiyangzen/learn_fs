# sources/distributed-fs/ceph-client/fs/hfsplus/bnode.c

Purpose: provides HFS+ btree node cache management and byte-level operations for reading, writing, clearing, copying, moving, validating, unlinking, creating, and freeing bnodes.

Important APIs and control flow: `hfs_bnode_read/write/clear/copy/move()` operate across one or more pages, using shared bounds helpers (`is_bnode_offset_valid()`, `check_and_correct_requested_length()`) and dirtying changed pages. `hfs_bnode_read_key()` derives key length from node/tree attributes, with special handling for the attributes tree. `hfs_bnode_unlink()` updates sibling descriptors, adjusts leaf head/tail or root/depth, and marks a node deleted. `hfs_bnode_findhash()`, `__hfs_bnode_create()`, `hfs_bnode_find()`, and `hfs_bnode_create()` implement a hashed bnode cache with `HFS_BNODE_NEW` wait coordination and structural validation of descriptor type/height and record offset table. `hfs_bnode_put()` frees deleted nodes after last reference, optionally zeroing unused nodes. `hfs_bnode_need_zeroout()` checks the volume unused-node-fix attribute.

State and persistence: writes directly to btree inode pages, marks pages dirty, updates sibling/root/leaf metadata, and frees node bitmap bits through `hfs_bmap_free()`. Cached bnodes are in-memory but backed by page-cache pages.

Dependencies and integration: used by all HFS+ btree search and mutation files. Relies on HFS+ raw node descriptors, page cache, hash locking, and volume attributes.

Risks and test signals: bounds checks mitigate malformed images, but truncated reads can still alter caller behavior. Node cache reference correctness is critical under memory pressure. Tests should cover malformed record offsets, deleted node lifetime, zeroout-enabled frees, multi-page nodes, and concurrent lookup of the same new bnode.
