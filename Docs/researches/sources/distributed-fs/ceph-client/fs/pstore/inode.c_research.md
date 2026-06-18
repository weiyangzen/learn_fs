# sources/distributed-fs/ceph-client/fs/pstore/inode.c

## Purpose
`inode.c` implements the pstore filesystem mounted at `/sys/fs/pstore`, presenting persistent backend records as read-only files and erasing backend records when files are unlinked.

## Important APIs, types, and functions
Public pstore helpers are `pstore_init_fs`, `pstore_exit_fs`, `pstore_get_records`, `pstore_put_backend_records`, and `pstore_mkfile`. Internal state includes `records_list`, `records_list_lock`, `pstore_sb`, `pstore_private`, and mount context option `kmsg_bytes`.

## Control flow
Mount creates a single ramfs-like superblock, applies `kmsg_bytes`, stores the root in `pstore_sb`, and calls `pstore_get_records` to read backend entries. `pstore_mkfile` deduplicates records by backend/type/id, creates a persistent dentry, and stores the `pstore_record` in inode private data. Reads use simple buffers except ftrace, which formats binary trace records through seq_file. Unlink removes the file from `records_list` and calls backend `erase`.

## State and persistence
Filesystem state is volatile dentries/inodes backed by backend record buffers. The actual persistent state is erased only through backend callbacks. Remount updates global `kmsg_bytes`.

## Dependencies and integration points
It integrates VFS fs_context, sysfs mount point creation, simple directory operations, seq_file, pstore platform code, and backend read/erase locking through `psi->read_mutex`.

## Risks and test signals
Risks include duplicate record handling, unregister while mounted, unlink races, ftrace record alignment, remount option propagation, and backend erase failure. Test signals include mounting before and after backend registration, repeated rescans, unlink with and without erase support, ftrace file reads, remount `kmsg_bytes`, and backend unregister removal.
