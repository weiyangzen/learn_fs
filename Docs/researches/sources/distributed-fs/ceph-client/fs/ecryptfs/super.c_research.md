<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/super.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/super.c

## Purpose
`super.c` defines eCryptfs superblock operations and inode-cache lifetime. It allocates and initializes eCryptfs private inode state, forwards filesystem statistics to the lower filesystem, reports mount options, and tears down lower inode references on eviction.

## Important APIs, types, and functions
The exported table is `ecryptfs_sops`. Important functions are `ecryptfs_alloc_inode`, `ecryptfs_destroy_inode`, `ecryptfs_free_inode`, `ecryptfs_statfs`, `ecryptfs_evict_inode`, and `ecryptfs_show_options`. The file owns the global `ecryptfs_inode_info_cache`.

## Control flow
Allocation pulls `struct ecryptfs_inode_info` from the slab cache, initializes `crypt_stat`, lower-file mutex/count, and lower-file pointer, and returns the embedded VFS inode. Destroy asserts the lower file has already been dropped and releases crypto state. Eviction truncates page cache, clears the inode, and iputs the lower inode. `statfs` calls the lower superblock operation, rewrites the magic to `ECRYPTFS_SUPER_MAGIC`, and clamps filename length through mount crypto settings. `show_options` walks global auth tokens and prints cipher, key-size, passthrough, xattr metadata, encrypted view, unlink-sigs, and mount-auth-token-only flags.

## State and persistence
The file maintains only runtime slab/inode state. Persistent user-visible state is represented indirectly by mount options and lower filesystem stats. Inode crypto state is initialized here and destroyed when the inode dies.

## Dependencies and integration points
It depends on lower dentry/superblock operations, eCryptfs mount crypt-stat structures, key/auth token lists, and Linux superblock/inode lifecycle callbacks. Other eCryptfs files rely on the initialized private inode layout and crypt stat.

## Risks and test signals
Risks include lower inode reference leaks, BUGs if lower files survive destroy, incorrect `statfs` passthrough, mount option disclosure mismatches, and slab lifetime issues at module unload. Test signals include mount/unmount loops, inode eviction after open lower files, `statfs`, `/proc/mounts` option output, lower filesystems with no `statfs`, and encrypted filename length limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/super.c -->
