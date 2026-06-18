# sources/distributed-fs/orangefs/src/client/sysint/getparent.c
## sources/distributed-fs/orangefs/src/client/sysint/getparent.c

**Purpose:** Implements `PVFS_sys_getparent()`, a helper that resolves a path's parent directory reference and basename.

**APIs and control flow:** The function validates `entry_name` and `resp`, extracts the parent directory path with `PINT_get_base_dir`, looks it up via `PVFS_sys_lookup(..., PVFS2_LOOKUP_LINK_NO_FOLLOW, hints)`, extracts the final basename with `PINT_remove_base_dir`, copies it into `resp->basename`, and stores the parent object reference.

**State and dependencies:** No persistent state. Depends on path utilities, sysint lookup, credentials, gossip logging, and `PVFS_sysresp_getparent`.

**Risks and tests:** `strncpy(resp->basename, file_buf, PVFS_SEGMENT_MAX)` may not terminate if source length hits the limit. It returns the initial `-PVFS_EINVAL` after basename extraction failure even if previous operations succeeded. Tests should include root paths, relative paths, too-long segments, symlinks, lookup failures, and basename termination.
