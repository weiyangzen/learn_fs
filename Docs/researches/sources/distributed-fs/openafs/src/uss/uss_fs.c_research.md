
# sources/distributed-fs/openafs/src/uss/uss_fs.c

Purpose: `uss_fs.c` wraps AFS cache-manager operations used by `uss`: ACL pioctls, volume status pioctls, backup-map refresh, mount-point symlink creation/deletion, and token removal for a cell.

Important APIs and functions: exported wrappers include `uss_fs_GetACL()`, `uss_fs_SetACL()`, `uss_fs_GetVolStat()`, `uss_fs_SetVolStat()`, `uss_fs_CkBackups()`, `uss_fs_MkMountPoint()`, `uss_fs_RmMountPoint()`, and `uss_fs_UnlogToken()`. Internal `InAFS()` probes with `VIOC_FILE_CELL_NAME`, `ParentAndComponent()` splits a path for mount-point deletion, and `CarefulPioctl()` retries pioctls after `ENODEV` by calling `uss_fs_CkBackups()`.

Control flow: ACL and volume status functions fill a static `ViceIoctl` blob and route through `CarefulPioctl()`. Mount creation checks that the parent is in AFS, formats local or cross-cell mountpoint symlink contents, and calls `symlink()`. Mount deletion first validates the target with `VIOC_AFS_STAT_MT_PT`, then removes it with `VIOC_AFS_DELETE_MT_PT` unless dry-run is enabled. Token unlog enumerates tokens, marks those whose client cell matches, forgets all, and re-registers the rest.

State and persistence: uses a file-static `ViceIoctl` and global `uss_fs_InBuff`/`uss_fs_OutBuff`; it is not thread-safe. Persistent changes are AFS ACL/status data, mount-point objects, and user tokens.

Dependencies and integration: depends on `pioctl`, `venus.h` opcode constants, Rx/auth token APIs, global dry-run state, and `local_Cell` from `uss.c`.

Risks: static pioctl blob and shared buffers make reentrancy unsafe. `ParentAndComponent()` uses `strcpy()` into caller buffers. `uss_fs_UnlogToken()` does not check `malloc()` and can discard all tokens before failing to restore some. `uss_fs_MkMountPoint()` is less used than direct symlink creation in `uss_vol.c`, so behavior may diverge. Test signals should include ENODEV retry, non-AFS parent rejection, dry-run mount removal, token preservation, and cross-cell mount text.
