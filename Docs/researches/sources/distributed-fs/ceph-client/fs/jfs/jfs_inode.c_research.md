# sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.c

Purpose: implements JFS inode flag projection to VFS flags and allocation/initialization of new in-memory plus on-disk inodes.

Important APIs and functions: exported functions in this file are `jfs_set_inode_flags` and `ialloc`.

Control flow: `jfs_set_inode_flags` maps JFS private `mode2` bits such as immutable, append-only, noatime, dirsync, and sync to VFS inode flags. `ialloc` allocates a VFS inode with `new_inode`, asks `diAlloc` for a disk inode, inserts it locked into the inode cache, initializes ownership and quota, inherits selected JFS flags from the parent, sets directory versus non-directory mode bits, initializes timestamps, generation number, commit flags, ACL/EA descriptors, index counters, lock-related fields, and returns the new inode. Error paths drop quota, clear link count, discard or put the inode as appropriate.

State and persistence behavior: `ialloc` creates persistent allocation state indirectly through `diAlloc`, but this file initializes the in-memory fields that will later be committed by `diWrite`. It preserves saved UID/GID for mount override behavior, sets `mode2` for JFS-specific flags, zeroes ACL/EA descriptors and transaction fields, and increments the superblock generation generator.

Dependencies and integration: depends on VFS inode/quota APIs, `jfs_incore`, `jfs_imap`, `jfs_dinode` mode flags, and debug logging. It integrates with create/mkdir/symlink paths and with later writeback/commit code through the fields it initializes.

Risks and edge cases: failure after disk inode allocation but before quota allocation must not leak a live VFS inode. Symlinks intentionally clear inherited immutable/append flags. Directories get `IDIRECTORY` but clear `JFS_DIRSYNC_FL` in `mode2` while VFS mode still controls behavior. New fields in `jfs_inode_info` require updates here to avoid uninitialized runtime state.

Test signals: create regular files, directories, symlinks under parents with inherited flags, quota allocation failure, inode-cache insert failure, UID/GID mount override behavior, generation increment, and VFS flag projection from private mode bits.
