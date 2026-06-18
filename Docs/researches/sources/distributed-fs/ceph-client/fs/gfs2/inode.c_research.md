## sources/distributed-fs/ceph-client/fs/gfs2/inode.c

### Purpose
`inode.c` implements GFS2 inode lookup, creation, directory mutation, rename/exchange, permission, getattr/setattr, symlink reading, fiemap, seek-data/hole, and inode operation tables. It is the main VFS inode-operation bridge and coordinates directory contents, dinode allocation/deallocation, quota, rgrp locking, ACL/security xattrs, and glock ordering.

### Important APIs, Types, and Functions
Externally visible functions include `gfs2_setup_inode`, `gfs2_inode_lookup`, `gfs2_lookup_by_inum`, `gfs2_lookup_meta`, `gfs2_lookupi`, `gfs2_dinode_dealloc`, `gfs2_permission`, `gfs2_seek_data`, and `gfs2_seek_hole`. Static VFS callbacks include `gfs2_create`, `gfs2_lookup`, `gfs2_link`, `gfs2_unlink`, `gfs2_symlink`, `gfs2_mkdir`, `gfs2_mknod`, `gfs2_atomic_open`, `gfs2_rename2`, `gfs2_get_link`, `gfs2_setattr`, `gfs2_getattr`, `gfs2_fiemap`, and `gfs2_update_time`. The file defines `gfs2_file_iops`, `gfs2_dir_iops`, and `gfs2_symlink_iops`.

### Control Flow
Lookup begins with `iget5_locked`, then creates inode and iopen glocks for new VFS inodes, takes the iopen glock shared, optionally takes the inode glock with `GL_SKIP` to check block type or stale generation, attaches the in-core inode object to glocks, instantiates disk state when needed, sets operations, and unlocks the inode. Directory lookup takes the parent glock shared unless already held and calls `gfs2_dir_search`.

Creation (`gfs2_create_inode`) takes quota references, refreshes rindex, locks the parent directory exclusive, validates permissions/link limits/name existence, allocates a new VFS inode, sets mode/uid/gid/timestamps/inherited disk flags, allocates dinode and optional xattr block, creates inode and iopen glocks, inserts the inode into the inode cache, locks iopen and inode glocks, writes the dinode, sets ACLs/security xattrs, links into the directory, instantiates the dentry, and opens the file if atomic open requested. Failure paths deallocate xattrs/dinode, drop glocks, clear objects, and release quota.

Hard links lock parent and child glocks exclusive, validate target/link limits/immutability, allocate directory space if needed, start a transaction, add the directory entry, increment link count, and dirty the inode. Unlink/rmdir refresh rindex, lock parent, target, and target rgrp glocks, validate sticky/append/immutability/emptiness, remove the directory entry, update link count, and mark unlinked dinodes. Rename locks the global rename glock when moving across parents, acquires involved directory/inode glocks asynchronously with retry on `-ESTALE`, optionally locks the overwritten inode's rgrp, validates source/target, allocates target dir space, unlinks replacement, updates `..` or ctime, removes old entry, and adds new entry. `RENAME_EXCHANGE` swaps directory entries and adjusts parent link counts when directory/non-directory types cross parents.

### State and Persistence Behavior
Persistent state includes dinode fields, directory entries, link counts, ctime/mtime/atime, quota usage, resource-group bitmaps, statfs, ACL/security xattrs, xattr blocks, and unlinked state. Transactions wrap all mutating directory and dinode operations. `gfs2_dinode_dealloc` frees a dinode under the rgrp glock and final-releases pages. `gfs2_setattr` takes the inode glock exclusive, validates VFS attributes, routes size changes to truncate code, routes ownership changes through quota transfer, and wraps simple metadata changes in transactions as needed.

### Dependencies and Integration Points
`inode.c` depends on `glock` for cluster locking, `dir` for directory search/add/delete/move, `rgrp` for allocation and dinode free, `quota` for creation and chown accounting, `trans` for journaling, `meta_io` for dinode buffers, `acl`/`xattr`/security for metadata, `bmap`/iomap for fiemap and seek, `file.c` for file operation tables and open common, and `glops.c` for inode glock operation behavior.

### Risks and Edge Cases
The largest risks are incomplete failure unwinding during create, deadlocks from inconsistent multi-glock ordering, stale inode generations during delete/recreate races, rename cycles involving directories, unlinked-directory operations, quota/rgrp reservation mismatches, and page faults while holding glocks during fiemap. RCU permission checks must return `-ECHILD` instead of blocking. `gfs2_update_time` can upgrade a held shared glock to exclusive and must preserve holder consistency.

### Test Signals
Relevant tests include lookup under concurrent unlink/recreate, atomic open with and without `O_EXCL`, mkdir/symlink/mknod ACL and security xattr creation, hard link/unlink/rmdir limits, cross-directory rename and `RENAME_EXCHANGE`, chown quota transfer, truncate/setattr, fiemap with faulted user buffers, seek-data/hole correctness, NFS readdirplus lookup/getattr paths, and multi-node rename/unlink stress.
