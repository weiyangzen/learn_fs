# sources/distributed-fs/orangefs/src/common/misc/realpath.c

Purpose: Provides `PINT_realpath`, a bundled path canonicalizer that removes `.`/`..`, follows symlinks, and works around libc realpath behavior while preserving OrangeFS mount-point interactions.

Important APIs and functions: `PINT_realpath(const char *path, char *resolved_path, int maxreslth)` is the exported function. POSIX builds manually canonicalize path components and symlinks. Windows builds delegate to `_fullpath`.

Control flow: POSIX relative paths start with `getcwd`; absolute paths start at `/`. The loop consumes slash-separated components, ignores repeated slash and `.`, backs up on `..`, copies normal components with length checks, then calls `readlink` or `SYS_readlinkat`. Before reading links, non-user-interface builds call `PVFS_util_resolve_absolute` to detect PVFS mount points and choose the readlink method. Symlink targets are spliced back into the remaining path, with absolute links restarting from the root.

State and persistence: Stateless except for temporary heap buffer `buf` used while expanding symlink targets. It reads filesystem and symlink state but does not write.

Dependencies and integration points: Depends on POSIX `getcwd`, `readlink`, `readlinkat`, `errno`, `PVFS_util_resolve_absolute`, `pvfs2-util.h`, and PVFS error codes. Used by `PVFS_util_resolve` to canonicalize paths during mount resolution and object-creation fallback.

Risks: `readlinks` increments for every path component rather than only successful symlinks, so deep non-symlink paths can hit `PVFS_ELOOP`. Many filesystem errors collapse to `-PVFS_EINVAL`, losing diagnostic precision. The PVFS mount check has side effects through `PVFS_path` resolution state. Windows behavior is only CRT absolute-path expansion and does not resolve symlinks.

Test signals: Relative/absolute paths, repeated slashes, `.`/`..`, trailing slash, nonexistent basename via caller fallback, symlink chains and loops, paths with more than 32 components, PVFS mount-boundary paths, long paths near `PATH_MAX`, and Windows `_fullpath` failure cases.
