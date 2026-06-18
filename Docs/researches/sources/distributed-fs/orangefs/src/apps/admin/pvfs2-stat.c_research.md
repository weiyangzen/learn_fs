<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stat.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stat.c

**Purpose:** `pvfs2-stat` reports OrangeFS object metadata for one or more files, similar to Unix `stat` but using PVFS sysint attributes.

**Important APIs, types, and functions:** `struct options` tracks verbose, symlink dereference, dfile flag, and up to `MAX_NUM_FILES` paths. `main()` resolves each path with `PVFS_util_resolve`, creates one credential, and calls `do_stat()`. `do_stat()` performs `PVFS_sys_lookup` with follow/no-follow behavior, handles absolute symlink targets that return `-PVFS_ENOTPVFS`, then calls `PVFS_sys_getattr`. `print_stats()` formats `PVFS_sys_attr` fields including perms, type, link target, size, owner/group names, atime/mtime/ctime, dfile count, block size, dirent count, dist-dir attributes, and file flags.

**Control flow:** Options are parsed first; the remaining args are stored as file names. Each file is resolved to fsid and relative path, with empty relative path normalized to `/`. `do_stat()` optionally follows symlinks recursively via `goto next_target` when absolute symlink targets require a new mount resolution. Aggregate return ORs per-file errors.

**State and persistence:** It is read-only. It reads filesystem metadata and local passwd/group databases for name display. It allocates `lk_response.error_path` but does not free it.

**Dependencies and integration points:** It depends on PVFS sysint lookup/getattr, mount resolution, credential defaults, and libc user/group lookup. It is a diagnostic input for scripts such as `pvfs2-setmattr`.

**Risks and edge cases:** Symlink-follow recursion has no explicit cycle limit. `new_path`-style buffers are avoided here, but `sprintf`/`ctime` formatting assumes valid timestamps and link targets. The `-D` dfile handle printing code is compiled out, so the option has no visible effect. Tests should cover multiple files, mount root, symlink no-follow/follow, absolute symlink targets across PVFS mounts, unknown uid/gid, and all object types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-stat.c -->
