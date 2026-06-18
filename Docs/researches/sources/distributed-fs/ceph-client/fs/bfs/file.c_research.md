# sources/distributed-fs/ceph-client/fs/bfs/file.c

Purpose: implements BFS regular file operations and block mapping/allocation for a filesystem that stores each file in one contiguous block range.

Important APIs/types/functions: exported `bfs_file_operations`, `bfs_get_block`, `bfs_move_block`, `bfs_move_blocks`, `bfs_writepages`, `bfs_read_folio`, `bfs_write_begin`, `bfs_bmap`, exported `bfs_aops`, and empty `bfs_file_inops`.

Control flow: reads map logical blocks to `i_sblock + block` if inside `i_eblock`. Writes either reuse allocated range, extend trivially when the file is the last allocated file, or move the entire file to the block after `si_lf_eblk` before extending. Page-cache write paths use generic block helpers with `bfs_get_block`.

State and persistence: updates private inode start/end block range, superblock free block count, last-file end block, dirty inode state, and disk blocks copied during relocation.

Dependencies and integration: used by BFS regular inodes from `inode.c` and `dir.c`; relies on buffer-head and mpage helpers plus `bfs_lock`.

Risks: relocation copies data block by block and comments note assumptions about inode writeback racing with `i_blocks`. ENOSPC and I/O failure during moves can leave corruption risk if not handled carefully.

Test signals: append to empty and non-last files; force relocation; read after relocation; ENOSPC boundary; mmap/writeback/bmap coverage; fault injection on block copy.
