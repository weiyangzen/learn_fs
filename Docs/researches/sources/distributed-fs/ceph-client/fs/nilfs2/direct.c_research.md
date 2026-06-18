# sources/distributed-fs/ceph-client/fs/nilfs2/direct.c

## Purpose
`direct.c` implements the small-file direct block-map backend. It stores a fixed array of block pointers in the inode's bmap area, supports lookup/insert/delete/contiguous scans, participates in DAT virtual block copy-on-write, and can convert to or from B-tree form when size thresholds are crossed.

## Important APIs and functions
- `nilfs_direct_get_ptr()` and `nilfs_direct_set_ptr()` access little-endian direct pointers.
- Lookup APIs implement single and contiguous lookup: `nilfs_direct_lookup()` and `nilfs_direct_lookup_contig()`.
- Mutation APIs: `nilfs_direct_insert()`, `nilfs_direct_delete()`, `nilfs_direct_delete_and_convert()`.
- Key enumeration: `nilfs_direct_seek_key()`, `nilfs_direct_last_key()`, `nilfs_direct_gather_data()`, and `nilfs_direct_check_insert()`.
- Persistence callbacks: `nilfs_direct_propagate()`, `nilfs_direct_assign()`, `nilfs_direct_assign_v()`, and `nilfs_direct_assign_p()`.
- `nilfs_direct_init()` installs `nilfs_direct_ops` in the bmap.

## Control flow
Lookup bounds keys by `NILFS_DIRECT_KEY_MAX` and returns `-ENOENT` for invalid/unallocated pointers. Contiguous lookup optionally translates each virtual block through DAT and stops when physical contiguity breaks.

Insert verifies a free slot, prepares a bmap/DAT pointer allocation, marks the caller-supplied data buffer volatile, commits the allocation, stores the allocated pointer, marks the bmap dirty, updates sequential allocation target state for virtual bmaps, and increments inode block count. Delete prepares and commits pointer end/free, clears the slot to `NILFS_BMAP_INVALID_PTR`, and decrements block count.

Propagation is only meaningful for virtual block maps. If the dirty buffer is not volatile, it replaces the virtual pointer through `nilfs_dat_prepare_update()`/`commit_update()` and stores the new virtual number. If already volatile, it marks the DAT entry dirty. Assignment during segment construction starts the DAT entry for virtual pointers or stores a physical block number directly for physical maps, then fills binfo.

## State and persistence behavior
Direct pointers live inside `nilfs_bmap::b_u.u_data` after a `struct nilfs_direct_node` header. The direct backend has no separate node buffers, so dirty bmap state is written with the inode. DAT tracks lifetime and physical assignment for virtual pointers.

## Dependencies and integration points
It depends on `bmap.h`, `dat.c`, `alloc.c` wrappers, `nilfs_bmap_data_get_key()`, and inode block accounting. `btree.c` consumes `nilfs_direct_delete_and_convert()` during map conversion, and VFS block allocation reaches this backend through `nilfs_bmap_*` calls in `inode.c`.

## Risks and invariants
Direct keys cannot exceed `NILFS_DIRECT_KEY_MAX`; callers must convert to B-tree before inserting larger keys. The `ptr` argument to insert is encoded as a `buffer_head *` cast through integer form, so callers must pass a valid buffer head. DAT update failures must leave old pointers intact. Contiguous lookup treats missing DAT translations as metadata corruption by converting `-ENOENT` to `-EINVAL`.

## Test signals
Exercise direct lookup/insert/delete, conversion boundaries, contiguous physical and virtual extents, propagation of volatile and non-volatile buffers, assignment to binfo, and invalid key handling.
