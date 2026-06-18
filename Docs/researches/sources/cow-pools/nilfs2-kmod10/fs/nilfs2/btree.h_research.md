# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.h

B-tree public header. It defines path state, node/root capacity macros, key bounds, and exported B-tree entry points.

Important type:
- `struct nilfs_btree_path`: per-level traversal and mutation state, including current/sibling buffers, child index, old/new pointer requests, node rekey context, and rebalance callback.

Exports include initialization, direct-to-B-tree conversion, GC initialization, and node-block corruption checking.

Risk/notes: capacity macros derive from on-disk structure layout and block size. Any on-disk format change must preserve these calculations.
