# sources/distributed-fs/ceph-client/fs/ufs/ufs.h

`ufs.h` is the in-kernel UFS private interface. It defines in-core superblock and inode state, mount option bits, debug macros, cross-file function declarations, and helper accessors used throughout the UFS implementation.

`struct ufs_sb_info` stores parsed private superblock state, cylinder summary/cache pointers, byte sex, flavour flags, error policy, delayed sync work, and locks. `struct ufs_inode_info` embeds UFS block pointer/fast symlink storage, flags, truncation and metadata synchronization state, and the VFS inode. `UFS_SB()` and `UFS_I()` convert VFS objects to private structures. The header declares allocation, directory, file, inode, and superblock functions, and provides `ufs_dtog()`/`ufs_dtogd()` for block-to-cylinder-group mapping.

This header is mostly declarative, but it defines the contracts used by `super.c`, `namei.c`, inode/file code, and allocation code. Persistent-facing state includes `i_u1` block pointers or fast symlink bytes; transient state includes cylinder-group cache arrays, mutexes, spinlocks, and delayed work. Risks are stale cache state, mount flag mismatches, and layout assumptions in `container_of`. Good test signals are compile coverage across UFS configs and runtime testing for delayed sync, truncation, allocation, and namespace operations.
