# sources/distributed-fs/ceph-client/fs/befs/inode.c

Purpose: validates raw BeFS inodes before the VFS inode is populated.

Important APIs/types/functions: `befs_check_inode`.

Control flow: converts inode magic, stored inode address, and flags to host order; rejects bad magic, mismatch between requested block number and inode self-address, and inodes not marked in use.

State and persistence: reads persistent inode header fields but does not mutate disk or VFS state.

Dependencies and integration: called by `befs_iget()` in `linuxvfs.c`; uses endian and address conversion helpers from `befs.h`.

Risks: validation is intentionally minimal; malformed datastreams or modes are checked later. Incorrect acceptance can lead to invalid block mapping.

Test signals: mount images with corrupt inode magic, stale self-address, and cleared `BEFS_INODE_IN_USE`; expect `befs_iget()` failure.
