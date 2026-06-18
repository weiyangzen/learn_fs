# sources/distributed-fs/ceph-client/fs/bfs/inode.c

Purpose: implements BFS superblock mount, inode read/write/evict, statfs, inode cache, filesystem registration, and persistent inode/free-space accounting.

Important APIs/types/functions: `bfs_iget`, `find_inode`, `bfs_write_inode`, `bfs_evict_inode`, `bfs_put_super`, `bfs_statfs`, inode cache helpers, `bfs_sops`, `bfs_dump_imap`, `bfs_fill_super`, fs_context ops, and module init/exit.

Control flow: mount sets block size, reads and validates the BFS superblock, computes maximum inode number, initializes reserved inode bits, loads root inode, checks last block readability, scans all inodes to validate block ranges and build free inode/block counters. `bfs_iget()` reads an on-disk inode, reconstructs file type from `i_vtype`, loads ownership/times/ranges, and installs directory or file ops. Writeback serializes and writes the on-disk inode; eviction clears deleted inodes and frees blocks/inode bits.

State and persistence: persistent BFS inode table, superblock geometry, inode bitmap-derived free counts, contiguous file block ranges, and timestamps. In-core `si_freeb`, `si_freei`, and `si_lf_eblk` are reconstructed at mount and updated by mutations.

Dependencies and integration: depends on UAPI BFS structures/macros, directory/file operation tables, buffer-head I/O, VFS writeback/eviction, and module filesystem registration.

Risks: mount continues on unclean BFS but validates inode ranges. Free-space accounting must stay consistent with relocation and eviction. Root and regular file type reconstruction compensates for historical `i_mode` garbage bits.

Test signals: mount clean/unclean/corrupt images; read/write inode sync; delete files and verify free counters; fill inode table; statfs; malformed start/end/eoffset rejection.
