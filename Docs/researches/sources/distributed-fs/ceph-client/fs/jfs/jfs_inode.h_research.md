# sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.h

Purpose: declares the JFS inode, file, directory, symlink, export, ioctl, writeback, truncate, block-mapping, fsync, and file-attribute interfaces used across the filesystem.

Important APIs and types: declares `ialloc`, `jfs_fsync`, file attribute get/set, `jfs_ioctl`, `jfs_iget`, commit/writeback/evict/dirty/truncate helpers, zero-link cleanup, NFS export helpers, `jfs_set_inode_flags`, `jfs_get_block`, `jfs_setattr`, and the address-space, inode-operation, file-operation, dentry-operation tables for JFS files/directories/symlinks/case-insensitive dentries.

Control flow: this header has no executable flow; it supplies the function surface used by VFS operation tables and JFS internal modules.

State and persistence behavior: the declared functions cover all inode lifecycle persistence points: allocation, lookup, dirtying, commit, writeback, eviction, truncation, block mapping, and metadata/file attribute changes.

Dependencies and integration: depends on Linux VFS types (`struct inode`, `file`, `dentry`, `fid`, `iattr`, `address_space_operations`, operation tables) and links JFS implementation files into VFS registration.

Risks and edge cases: signatures must track kernel VFS API changes, especially idmapped mount parameters and file attribute APIs. A mismatch in declared operation tables can break mount-time registration or case-insensitive dentry behavior.

Test signals: kernel build, VFS create/open/read/write/fsync/truncate/setattr/ioctl paths, exportfs file handle decode, symlink operation selection, and case-insensitive lookup behavior.
