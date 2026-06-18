# sources/distributed-fs/ceph-client/fs/befs/btree.c

Purpose: implements read-only traversal and lookup for BeFS directory B+trees over datastream storage.

Important APIs/types/functions: public `befs_btree_find` and `befs_btree_read`; internal `befs_bt_read_super`, `befs_bt_read_node`, `befs_find_key`, `befs_btree_seekleaf`, `befs_leafnode`, key/value layout helpers, and string comparison.

Control flow: lookup reads the B+tree superblock, loads the root node, descends interior nodes using binary search and overflow links, then searches the leaf for an exact key. Readdir finds the first leaf, walks right links until `ctx->pos` falls in a node, extracts key/value pairs, and signals end/empty/error with BeFS-specific codes.

State and persistence: transient `struct befs_btree_node` wraps one buffer_head and host-endian node header. Persistent keys, key-length indexes, and value arrays remain in packed on-disk node memory.

Dependencies and integration: layered on `befs_read_datastream()` for block access, endian helpers for fields, and directory operations in `linuxvfs.c` for lookup/readdir.

Risks: node layout pointer arithmetic, key length indexes, and overflow semantics are sensitive to corrupt images. The implementation handles string directory keys only and leaves non-string index comparators disabled.

Test signals: directory lookup/readdir on empty, single-node, multi-node, and overflow B+trees; malformed magic/node fields; small key buffers; big-endian images.
