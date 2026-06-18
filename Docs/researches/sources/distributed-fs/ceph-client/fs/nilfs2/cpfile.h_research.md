# sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.h

## Purpose
`cpfile.h` declares the checkpoint-file API used by mount, inode-file loading, ioctl handlers, segment construction, and snapshot management.

## Important APIs
- `nilfs_cpfile_read_checkpoint()` loads a checkpoint's ifile inode and root counters.
- `nilfs_cpfile_create_checkpoint()` and `nilfs_cpfile_finalize_checkpoint()` create and complete checkpoint entries.
- `nilfs_cpfile_delete_checkpoints()` and `nilfs_cpfile_delete_checkpoint()` remove plain checkpoints.
- `nilfs_cpfile_change_cpmode()` and `nilfs_cpfile_is_snapshot()` manage and query checkpoint versus snapshot state.
- `nilfs_cpfile_get_stat()` and `nilfs_cpfile_get_cpinfo()` back checkpoint/snapshot reporting ioctls.
- `nilfs_cpfile_read()` loads the cpfile metadata inode from its raw inode.

## Control flow and persistence behavior
The header exposes a stateful metadata API: callers create checkpoints inside transactions, finalize them after root and ifile data are ready, and later query/delete/convert entries under cpfile locking in the implementation. The declarations preserve source-level coupling to `struct nilfs_root`, `struct nilfs_inode`, `struct nilfs_cpstat`, and on-disk checkpoint layout.

## Dependencies and integration points
It includes VFS inode/buffer types plus NILFS API and on-disk structures. `ifile.c` depends on it to read a checkpoint's ifile inode, and `ioctl.c` depends on it for user-visible checkpoint operations.

## Risks and test signals
Callers must pass valid checkpoint numbers and hold broader mount/transaction permissions where required. Tests should check all declared operations through mount, sync, snapshot, and ioctl flows rather than only direct cpfile calls.
