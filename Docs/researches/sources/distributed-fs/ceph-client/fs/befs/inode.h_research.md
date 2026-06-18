# sources/distributed-fs/ceph-client/fs/befs/inode.h

Purpose: declares BeFS raw inode validation.

Important APIs/types/functions: `befs_check_inode(struct super_block *, befs_inode *, befs_blocknr_t)`.

Control flow: consumed by `linuxvfs.c` when loading an inode from disk.

State and persistence: no header state; interface receives persistent raw inode data.

Dependencies and integration: ties `inode.c` validation into `befs_iget()`.

Risks: callers must pass the block number corresponding to the raw inode buffer for self-address validation.

Test signals: compile coverage and corrupt-inode mount/read tests.
