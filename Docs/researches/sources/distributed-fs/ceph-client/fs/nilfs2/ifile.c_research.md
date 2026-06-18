# sources/distributed-fs/ceph-client/fs/nilfs2/ifile.c

## Purpose
`ifile.c` implements the NILFS inode metadata file. It allocates and frees inode entries with the persistent allocator, maps inode numbers to raw on-disk inode records, counts free inode capacity, and loads the ifile from checkpoint data.

## Important APIs and functions
- `struct nilfs_ifile_info` embeds generic metadata state and a palloc cache.
- `nilfs_ifile_create_inode()` allocates a new inode entry starting from `NILFS_FIRST_INO`, gets/creates the entry block, commits the palloc allocation, dirties the block and metadata inode, and returns the inode number and buffer.
- `nilfs_ifile_delete_inode()` prepares/free an allocated entry, gets its block, clears raw inode flags, marks the block dirty, and commits the palloc free.
- `nilfs_ifile_get_inode_block()` validates inode numbers and returns the metadata block containing the raw inode.
- `nilfs_ifile_count_free_inodes()` derives maximum/free inode counts from palloc capacity and root `inodes_count`.
- `nilfs_ifile_read()` initializes a metadata inode and palloc blockgroup/cache, then asks cpfile to read the checkpoint's embedded ifile inode into it.

## Control flow
New inode creation is called from `nilfs_new_inode()`. The returned buffer remains referenced and becomes `NILFS_I(inode)->i_bh`, letting inode update code write the raw inode directly. Deletion is called from inode eviction after bmap truncation. Loading an ifile is checkpoint-root dependent: `nilfs_ifile_read()` creates or gets inode `NILFS_IFILE_INO` under a specific root and fills it from `nilfs_cpfile_read_checkpoint()`.

## State and persistence behavior
The ifile is a metadata file whose entries are `struct nilfs_inode` records. Allocation state is held by palloc bitmaps/descriptors; entry contents are dirty buffers later persisted through segment construction. Root `inodes_count` is updated by inode code, while ifile palloc tracks available slots.

## Dependencies and integration points
The file depends on `mdt.c`, `alloc.c`, `cpfile.c`, and `inode.c` raw inode helpers. It is central to inode lookup, creation, eviction, checkpoint mount, and free-inode reporting.

## Risks and invariants
Only valid public inode numbers may be read. Allocation/free prepare and commit must stay paired. The raw inode block returned by creation must remain referenced until inode cleanup. Deleting an inode currently only clears `i_flags` before freeing; correctness depends on palloc state preventing stale lookup.

## Test signals
Test inode create/delete loops, ENOSPC handling, invalid inode lookups, checkpoint ifile load, free-inode counts, and eviction after partial creation failures.
