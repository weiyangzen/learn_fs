<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/debugfs/internal.h

Purpose: declares the private debugfs data structures and proxy fops shared between `inode.c` and `file.c`.

Important APIs/types/functions: defines `struct debugfs_inode_info`, `DEBUGFS_I()`, external proxy file operation tables, `struct debugfs_fsdata`, and method-bit constants `HAS_READ`, `HAS_WRITE`, `HAS_LSEEK`, `HAS_POLL`, and `HAS_IOCTL`.

Control flow: `inode.c` stores raw file operations, short operations, automount callbacks, and auxiliary data in `debugfs_inode_info`; `file.c` reads these fields through `DEBUGFS_I()` to initialize per-dentry `debugfs_fsdata` and dispatch proxy operations.

State and persistence: `debugfs_inode_info` embeds the VFS inode and is allocated from the debugfs inode slab for inode lifetime. `debugfs_fsdata` is installed lazily in `dentry->d_fsdata` and holds active-user/cancellation state until dentry release.

Dependencies and integration: requires core inode, file operation, list, refcount, completion, mutex, and debugfs short-fops/automount type definitions from kernel headers. It is intentionally local to debugfs and not part of the external API.

Risks: the union in `debugfs_inode_info` requires the creator and opener to agree on whether the raw pointer is real fops, short fops, or automount callback. Method bits must stay synchronized with the proxy wrappers in `file.c`; otherwise wrappers may call absent operations or reject valid ones.

Test signals: compile-time coverage catches most type drift. Runtime signals come from creating full, short, noop, and automount debugfs entries, then opening/removing them under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/internal.h -->
