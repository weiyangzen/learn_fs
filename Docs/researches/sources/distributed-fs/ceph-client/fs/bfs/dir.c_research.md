# sources/distributed-fs/ceph-client/fs/bfs/dir.c

Purpose: implements BFS directory reading and mutation: create, lookup, hard link, unlink, rename, entry insertion, and entry lookup.

Important APIs/types/functions: `bfs_readdir`, `bfs_fsync`, exported `bfs_dir_operations`, `bfs_create`, `bfs_lookup`, `bfs_link`, `bfs_unlink`, `bfs_rename`, exported `bfs_dir_inops`, `bfs_add_entry`, `bfs_namecmp`, and `bfs_find_entry`.

Control flow: readdir scans fixed-size directory entries from the directory's contiguous block range. Create allocates a free inode bit under `bfs_lock`, initializes a regular file inode, marks it dirty, and inserts a directory entry. Lookup finds an entry and calls `bfs_iget()`. Link/unlink/rename update directory entries, timestamps, nlinks, and metadata buffer dirty tracking.

State and persistence: directory entries persist in BFS data blocks; inode allocation uses `si_imap` and `si_freei`; metadata buffer heads are tracked for fsync via `mapping_metadata_bhs`.

Dependencies and integration: uses buffer-head I/O, VFS dentry/inode helpers, global BFS mutex, file operations from `file.c`, inode writeback from `inode.c`, and on-disk formats from `linux/bfs_fs.h`.

Risks: directories have fixed capacity from their allocated blocks; create can allocate an inode and then fail to insert an entry. Rename rejects directories and supports only `RENAME_NOREPLACE`. All mutation relies on the global mutex for consistency.

Test signals: xfstests-style create/link/unlink/rename; directory full returning `-ENOSPC`; invalid f_pos alignment; fsync after metadata changes; lookup name-length boundary.
