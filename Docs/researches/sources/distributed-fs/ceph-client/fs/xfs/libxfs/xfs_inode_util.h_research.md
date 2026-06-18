# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.h

Purpose: Declares inode utility interfaces and creation/time-change metadata shared by XFS inode creation, linking, and deletion code.

Important APIs and types: `struct xfs_icreate_args` packages idmap, parent inode, device number, mode, and creation flags. Flags include tmpfile, initialize xattrs, and unlinkable. Time-change flags drive `xfs_trans_ichgtime`. Declared operations include flag conversion, initial project id selection, inode initialization/uninitialization, unlinked-list insertion/removal, and link count changes.

Control flow: the header contains no complex implementation but defines call contracts. Passing `idmap == NULL` creates detached or root-like metadata files with root ownership. `pip == NULL` means tree root creation. Creation flags influence whether an inode starts unlinked and whether an attr fork must be present.

State and persistence: consumers mutate persistent inode core fields, timestamps, link counts, fork offsets, and AGI unlinked structures through the declared functions.

Dependencies and integration: used by inode allocation, metadir creation, quota inode creation, VFS create/link/unlink paths, and transaction logging. `struct xfs_icluster` is forward-declared for inode free batching.

Risks and test signals: API misuse can create incorrectly owned detached metadata files or miss parent-pointer attr fork initialization. Tests should cover idmapped creates, tmpfiles, quota/metadir callers with `idmap == NULL`, and all link count transitions through zero.
