# sources/distributed-fs/ceph-client/fs/hpfs/inode.c

Purpose: this file initializes, reads, writes, sets attributes on, and evicts HPFS VFS inodes.

Important APIs and functions: `hpfs_init_inode()` initializes default inode and private fields from mount options. `hpfs_read_inode()` maps the fnode and derives VFS type, mode, uid/gid, size, nlink, operations, and EA-derived special cases. `hpfs_write_inode()` and `hpfs_write_inode_nolock()` synchronize inode state back to fnodes and directory entries. `hpfs_setattr()` validates and applies VFS setattr. `hpfs_evict_inode()` removes fnodes for deleted inodes.

Control flow: reading first loads the fnode. If EAs are enabled, it checks `UID`, `GID`, `SYMLINK`, `MODE`, and `DEV` EAs, which can turn the inode into a symlink or special file. Directories get `hpfs_dir_iops`, dnode root, block/size counts from `hpfs_count_dnodes()`, and nlink from subdir count. Regular files get file ops, size from fnode, and address-space ops. Writing finds the parent dirent via `map_fnode_dirent()`, updates fnode file size and dirent timestamps/size/read-only/EA size, writes EA metadata if enabled, updates the `.` dirent for directories, and dirties buffers.

State and persistence: inode private flags cache EA-backed uid/gid/mode. Persistent updates include fnode fields, directory entry timestamps/sizes/EA size, EA records for UID/GID/MODE/DEV, allocation truncation, and fnode deletion on final eviction.

Dependencies and integration: it uses `map.c`, `ea.c`, `dnode.c`, `file.c`, `dir.c`, global HPFS locking, and Linux setattr helpers. `file.c` marks inodes dirty and release calls writeback through this file.

Risks: `hpfs_setattr()` disallows extending files through truncate and limits uid/gid to 16-bit EA encoding. Root inode writes are skipped. Parent lookup during write can fail, leaving metadata unsynchronized. EA writing uses two-byte values even from `__le32` temporaries for UID/GID/MODE, matching HPFS limits but easy to misread.

Test signals: read regular/dir/symlink/special-file inodes from EAs, chmod/chown/truncate shrink, reject growth via setattr, writeback timestamps and read-only bit, eviction after unlink/rmdir, root inode no-op write, and mount options for default uid/gid/mode/eas.
