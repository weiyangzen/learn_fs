# sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.h

Purpose: exposes the file extent allocation interface and the inode-local allocation hint macro.

Important APIs and types: declares `extAlloc`, `extHint`, and `extRecord`. `INOHINT(ip)` computes a block hint from the inode's disk inode extent descriptor (`ixpxd`) by returning the last block of that extent.

Control flow: file allocation callers obtain a hint with `extHint` or `INOHINT`, then call `extAlloc`; delayed or not-recorded extents are finalized through `extRecord`.

State and persistence behavior: the header itself stores no state, but its APIs mutate xtree extent records, the block map, quota state, and inode dirty/commit state through `jfs_extent.c`.

Dependencies and integration: depends on `JFS_IP`, PXD helpers, `struct inode`, `s64`, `xad_t`, and the xtree/block-map layer. Used by JFS block mapping and file write code.

Risks and edge cases: `INOHINT` assumes `ixpxd` is valid and nonzero; callers must only use it for initialized inodes. `extAlloc` can return a shorter allocation than requested, so users must check the output XAD length.

Test signals: compilation of extent users, normal writes, fragmented allocation fallback, not-recorded extent conversion, and invalid inode extent detection in the caller path.
