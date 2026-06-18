# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_kern.c

Purpose: this is the kernel-side UML host filesystem. It presents a VFS filesystem whose backing store is a host directory tree and delegates host operations through the wrapper API in `hostfs.h`.

Important APIs and types: `struct hostfs_fs_info` stores the mounted host root path. `struct hostfs_inode_info` extends VFS inodes with a shared host fd, open mode bits, open mutex, host device, and birth time. File, directory, inode, address-space, superblock, fs-context, and filesystem-type operation tables wire hostfs into VFS.

Control flow: mount option parsing builds `host_root_path` from the global `root_ino` plus per-mount suffix. `hostfs_fill_super()` sets anonymous superblock properties, stats/loads the root inode, resolves root symlinks, and installs `s_root`. Lookup and creation convert dentries to host paths using `dentry_path_raw()` plus the configured root prefix. `hostfs_iget()` stats a path and uses `iget5_locked()` with inode-number/device/type/btime matching to avoid stale aliasing. Open accumulates read/write capability in one shared fd per inode, using `replace_file()` when a wider mode is needed. Page-cache reads and writes call `read_file()`/`write_file()` against that fd. Directory iteration opens the host directory each time and emits `readdir()` results.

State and persistence: hostfs keeps no independent on-disk state. VFS inode metadata mirrors host stat results and persistent changes are host syscalls: create, unlink, mkdir, rmdir, mknod, link, symlink, rename, chmod/chown/truncate/times, data writes, and fsync. `append` mode globally prevents unlink and size truncation and opens files with `O_APPEND`.

Dependencies and integration: it depends on UML setup hooks, `hostfs_user.c` wrappers, Linux VFS/page-cache/fs_context APIs, and `HOSTFS_SUPER_MAGIC`. It is registered as `hostfs` with `MODULE_ALIAS_FS`.

Risks: path confinement is string-prefix based: constructed paths prepend `host_root_path`, so correctness depends on VFS path resolution and no unexpected escape through host symlinks except the explicit root symlink follow. A single fd per inode can be widened across opens; mutex coverage is limited to mode/fd replacement. Writeback assumes valid open fds. `hostfs_permission()` combines host `access()` with generic permission, which can diverge from the UML user namespace model.

Test signals: mount with empty and non-empty roots, root symlink backing paths, append mode, concurrent read/write opens, writeback and fsync, rename with `RENAME_NOREPLACE`/`RENAME_EXCHANGE`, special files, statfs, permission checks, inode reuse on host filesystems, and page-cache truncation via setattr.
