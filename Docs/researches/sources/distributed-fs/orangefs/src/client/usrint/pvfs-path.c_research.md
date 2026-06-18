# sources/distributed-fs/orangefs/src/client/usrint/pvfs-path.c

## Purpose
`pvfs-path.c` decides whether a pathname belongs to PVFS and expands/qualifies paths for the user-space interface. It resolves relative paths, dot and dot-dot components, symlinks, mount points, and final filename splits while preserving metadata in `PVFS_path_t`.

## Important APIs, Types, and Functions
The public functions are `PVFS_expand_path(const char *path, int skip_last_lookup)`, `is_pvfs_path(const char **path, int skip_last_lookup)`, and `split_pathname(const char *path, char **directory, char **filename)`. `PVFS_expand_path` operates on `PVFS_path_t` objects from helpers such as `PVFS_path_from_expanded`, `PVFS_new_path`, `PVFS_qualify_path`, and `PVFS_free_expanded`. It sets and clears flags such as `PATH_EXPANDED`, `PATH_RESOLVED`, `PATH_LOOKEDUP`, `PATH_MNTPOINT`, and `PATH_ERROR`, and fills `fs_id`, `handle`, `pvfs_path`, and `filename` fields as lookup progresses.

## Control Flow
`PVFS_expand_path` starts from an existing expanded PVFS path object or creates a new one. Relative paths are prefixed with `getcwd`; absolute paths start at `/`. It loops over components, skipping repeated slashes and `.`, backing up for `..`, checking length, resolving mount points with `PVFS_util_resolve_absolute`, optionally skipping final lookup for lstat/readlink-style no-follow behavior, and looking up PVFS components with `iocommon_lookup_absolute(PVFS2_LOOKUP_LINK_NO_FOLLOW)`. If a PVFS component is a symlink, it gets `PVFS_ATTR_SYS_LNK_TARGET` and restarts or rewrites the remaining path. For non-PVFS components, it uses raw syscalls `SYS_readlink` and `SYS_stat` to avoid interposition loops. A 16-link limit prevents infinite symlink expansion.

`is_pvfs_path` initializes the library, validates input, and either uses kernel-mount detection under `PVFS_USRINT_KMOUNT` with glibc `stat/statfs`, or creates a `PVFS_path_t`, qualifies it, resolves it through PVFS mount tables, and if necessary calls `PVFS_expand_path`. It rewrites `*path` to the expanded path and returns 1 for PVFS, 0 otherwise. `split_pathname` allocates directory and filename pieces from a clean path and treats root-level and trailing-slash cases as errors with `EISDIR` or `ENOENT`.

## State and Persistence Behavior
Path state is held in allocated `PVFS_path_t` objects and their embedded original/expanded strings. The function updates object flags, return code, fs id, handle, filename pointer, and path pointers. It may allocate temporary symlink-rewrite buffers while expanding. Callers that receive an expanded path are responsible for `PVFS_free_expanded` where appropriate. No filesystem state is changed except lookups and stats.

## Dependencies and Integration Points
The file depends on `usrint.h`, `openfile-util.h`, `iocommon.h`, and `pvfs-path.h`. It integrates directly with `posix.c` path dispatch, `posix-pvfs.c` qualification and cwd behavior, PVFS mount resolution through `PVFS_util_resolve_absolute`, iocommon lookup/getattr, and glibc/syscall fallback for non-PVFS path components. It also calls `pvfs_sys_init`, so path checks can trigger full usrint initialization.

## Risks and Edge Cases
Path expansion is subtle around `skip_last_lookup`; the code has a suspicious check for `*p == '.' && *(p+1) == '0'`, likely intended for `.` followed by NUL. `PVFS_expand_path` sets `PATH_ERROR` only if `Ppath->rc != 0`, but local errors may not always propagate into `Ppath->rc`. In the kernel-mount branch, `strnlen(path, PVFS_PATH_MAX)` appears to use the pointer-to-pointer rather than `*path`. `split_pathname` assigns `filename = NULL` instead of `*filename = NULL` in one trailing-slash branch. The path logic depends on correct ownership and lifetime of `PVFS_path_t` buffers.

## Test Signals
Tests should cover absolute and relative paths, cwd in PVFS and non-PVFS locations, repeated slashes, dot and dot-dot normalization, PVFS and non-PVFS symlinks, absolute and relative symlink targets, symlink loops over 16 expansions, missing final components for create, lstat/readlink no-follow behavior, mount point detection, paths crossing from PVFS to non-PVFS, very long paths, root-level paths, trailing slashes, and memory ownership with `PVFS_free_expanded`.
