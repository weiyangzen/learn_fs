# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.c

Implements the inode file, a metadata file that stores on-disk NILFS inode records. It uses the shared persistent allocator from `alloc.c`.

Key behavior:
- Allocates new inode numbers starting from `NILFS_FIRST_INO`, returning the buffer containing the new raw inode.
- Deletes inode records by preparing allocator free state, clearing raw inode flags, dirtying the entry block, and committing the free.
- Retrieves inode entry blocks after validating inode numbers.
- Computes maximum and free inode counts from root inode count and allocator capacity.
- Initializes the ifile inode for a root/checkpoint by setting up metadata private data, allocator block groups, palloc cache, and reading checkpoint state from cpfile.

Integration: bridges checkpoint roots (`cpfile.c`) and VFS inode loading. Uses `nilfs_cpfile_read_checkpoint` to restore the ifile for a selected checkpoint.

Risk/notes: inode allocation is non-wrapping in this implementation. Delete clears only `i_flags` before committing allocator free, relying on allocation state to control reuse.
