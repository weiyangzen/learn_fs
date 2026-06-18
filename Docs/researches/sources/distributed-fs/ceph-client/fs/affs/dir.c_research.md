# sources/distributed-fs/ceph-client/fs/affs/dir.c

## Purpose
`dir.c` provides AFFS directory file operations and readdir implementation over Amiga hash buckets and hash chains.

## Important APIs, types, and functions
Key items are `struct affs_dir_data`, `affs_dir_open()`, `affs_dir_release()`, `affs_dir_llseek()`, `affs_readdir()`, `affs_dir_operations`, and `affs_dir_inode_operations`.

## Control flow
Directory open allocates private cursor data. `readdir` emits dot entries, decodes `ctx->pos` as hash bucket and chain index, optionally resumes from cached inode number if the inode i_version cookie matches, reads the directory block, walks bucket chains, emits names from header tails, and stores resume state. Directory inode operations delegate create, lookup, link, unlink, symlink, mkdir, rmdir, rename, and setattr to namei/inode code.

## State and persistence
Runtime cursor state tracks last inode and i_version cookie. Persistent directory state is the hash table in the directory header and each entry's `hash_chain`. Directory locking uses `affs_lock_dir()`.

## Dependencies and integration points
It depends on VFS `dir_context`, generic cookie llseek, AFFS hash-chain layout, `affs_file_fsync()`, and namei operations.

## Risks and test signals
Risks include resume after mutation, 16-bit chain-position overflow, I/O errors mid-iteration, invalid name lengths, and hash-chain corruption. Test signals include large directories, seekdir/telldir style offsets, concurrent create/unlink during readdir, corrupted chain pointers, and fsync on directories.
