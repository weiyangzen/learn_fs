# sources/distributed-fs/ceph-client/fs/bfs/bfs.h

Purpose: central BFS internal header defining in-core superblock/inode state, helpers, logging macro, and cross-file operation declarations.

Important APIs/types/functions: `BFS_MAX_LASTI`, `struct bfs_sb_info`, `struct bfs_inode_info`, `BFS_SB`, `BFS_I`, `bfs_iget`, `bfs_dump_imap`, `bfs_file_operations`, `bfs_aops`, `bfs_dir_inops`, and `bfs_dir_operations`.

Control flow: included by all BFS implementation files; private inode/superblock accessors are used for mount scan, writeback, directory updates, and file block allocation.

State and persistence: `bfs_sb_info` tracks total/free blocks, free inodes, last file end block, highest inode, inode bitmap, and global mutex. `bfs_inode_info` tracks disk inode number, contiguous block range, and metadata buffers for fsync.

Dependencies and integration: wraps UAPI `linux/bfs_fs.h` on-disk definitions and VFS inode embedding.

Risks: BFS has a small fixed inode namespace and contiguous allocation model; bitmap and free counters must remain serialized by `bfs_lock`.

Test signals: create/unlink/link/rename files, fill inode table, and verify statfs free counters.
