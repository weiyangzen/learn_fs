# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.c

Full B-tree implementation for large NILFS block mappings. It backs `struct nilfs_bmap_operations` when direct mapping is insufficient and handles lookup, insertion, deletion, conversion, dirty propagation, block assignment, and GC-specific behavior.

Key behavior:
- Manages B-tree path objects from `nilfs_btree_path_cache`.
- Implements node layout helpers for keys, pointers, levels, flags, child counts, root/non-root sizing, and consistency checks.
- Performs binary lookup through root and non-root nodes with optional node readahead.
- Supports contiguous lookup by walking leaf entries and right sibling nodes.
- Inserts with carry-left, carry-right, split, and grow operations; allocates DAT pointers and node buffers before committing.
- Deletes with borrow-left, borrow-right, concat-left/right, and shrink-root operations; prepares pointer termination through DAT.
- Converts direct mappings into B-tree form through `nilfs_btree_convert_and_insert`.
- Propagates dirty buffers upward, updating DAT entries and rekeying node cache entries when virtual block numbers change.
- Collects dirty B-tree node buffers by B-tree level for segment construction.
- Assigns physical block numbers for both physical-pointer maps and DAT-backed virtual-pointer maps.
- Provides GC operation table that marks DAT entries dirty and moves DAT mappings instead of normal lookup/insert/delete behavior.

Integration: depends on `btnode.c` for node cache IO/rekeying, `dat.c` for virtual address lifecycle, `alloc.c` through bmap pointer helpers, and inode block count accounting.

Risk/notes: this is high-risk metadata code. Many paths rely on strict prepare/commit/abort ordering. Internal `-EINVAL` is used to signal corrupted bmap state to the generic bmap layer. Node validation checks levels, root flags, and child counts, but deeper ordering invariants are maintained by operation logic.
