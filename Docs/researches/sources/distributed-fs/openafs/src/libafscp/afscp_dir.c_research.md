## sources/distributed-fs/openafs/src/libafscp/afscp_dir.c

Purpose: Implements directory reading, lookup, path resolution, symlink handling, and AFS mountpoint traversal for `libafscp`. It converts raw AFS directory files into `afscp_dirent` iteration results and maps path strings to `afscp_venusfid` objects.

Important APIs and functions: `afscp_SetDirMode` selects root interpretation between `DIRMODE_CELL` and `DIRMODE_DYNROOT`. `afscp_OpenDir`, `afscp_ReadDir`, `afscp_RewindDir`, and `afscp_CloseDir` expose a small directory stream API. `afscp_DirLookup` and `afscp_ResolveName` look up names inside a directory. `afscp_ResolvePath` and `afscp_ResolvePathFromVol` perform full path resolution. Internal helpers include `_DirUpdate`, `dir_get_entry`, `namehash`, `gettoproot`, `getvolumeroot`, `fidstack_*`, `_ResolvePath`, and `afscp_HandleLink`.

Control flow: `afscp_OpenDir` validates status with `afscp_GetStatus`, allocates a stream, and calls `_DirUpdate`. `_DirUpdate` checks the current data version, consults `volume->dircache` via `tfind`, fetches the directory file with `afscp_PRead` when stale, and stores the buffer in `tsearch`. `afscp_ReadDir` walks the on-disk hash table and chained `DirEntry` records. Path resolution splits path components in place, uses a FID stack for `..`, follows normal symlinks through recursive `_ResolvePath`, and treats non-executable AFS symlinks as volume mountpoints.

State and persistence: State is process-local. Directory buffers are cached in each `afscp_volume` tree and keyed by vnode/unique plus data version. `dirmode` is a process-global setting. The code does not persist anything beyond network-side reads.

Dependencies and integration: Depends on AFS directory layout from `<afs/dir.h>`, volume lookup from `afscp_volume.c`, FID allocation from `afscp_fid.c`, network reads from `afscp_file.c`, and status caching from `afscp_fid.c`. Root traversal depends on VLDB volume names such as `root.afs` and `root.cell`.

Risks: `_DirUpdate` stores the stream's `dirbuffer` pointer directly in the cache, while `afscp_CloseDir` only frees the stream, so ownership is intentionally cache-oriented but easy to misuse. `fidstack_push` silently drops entries on realloc failure, which can break `..` traversal without setting `afscp_errno`. Symlink recursion is capped at 5 per component but recursive path calls can still be complex. Directory parsing trusts on-disk structures after limited bounds checks.

Test signals: Exercise cached and uncached directory reads, stale data version refresh, dynamic-root absolute paths, mountpoints `%` and `#` style, normal symlink terminal and non-terminal behavior, `.` and `..`, ELOOP, ENOTDIR, ENODEV, ENOENT, and large directory rejection with `EFBIG`.
