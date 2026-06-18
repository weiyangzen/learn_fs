# sources/distributed-fs/ceph-client/fs/nilfs2/export.h

## Purpose
`export.h` declares NILFS exportfs support for NFS-style file handles and the filesystem's export operations table.

## Important APIs and types
- `extern const struct export_operations nilfs_export_ops` is the VFS export operations object provided elsewhere.
- `struct nilfs_fid` is the packed NILFS file identifier containing checkpoint number, inode number, generation, parent generation, and parent inode number.

## Control flow and state behavior
This header does not implement control flow. It defines the persistent identity fields needed to reconstruct file handles across checkpoints and parent directories. Including `cno` is essential because NILFS can expose snapshot roots where the same inode number may refer to different historical states.

## Dependencies and integration points
It depends on `<linux/exportfs.h>` and is consumed by superblock/export implementation code outside this work item. The generation fields align with inode generation handling in `inode.c` and `FS_IOC_GETVERSION`.

## Risks and test signals
Packed layout must remain stable for file-handle compatibility. Tests should cover file handle encode/decode for current and snapshot checkpoints, stale generation detection, and parent handle reconstruction.
