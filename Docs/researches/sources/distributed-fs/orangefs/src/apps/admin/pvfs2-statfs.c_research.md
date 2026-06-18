<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-statfs.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-statfs.c

**Purpose:** `pvfs2-statfs` prints aggregate and per-server filesystem capacity/health statistics for the filesystem containing a mount point.

**Important APIs, types, and functions:** `struct options` tracks mount and human-readable/SI formatting flags. `main()` uses `PVFS_sys_statfs` for aggregate `PVFS_sysresp_statfs`, `PVFS_mgmt_statfs_all` for an array of `PVFS_mgmt_server_stat`, and `PVFS_util_make_size_human_readable` for formatting.

**Control flow:** The tool parses `-m`, `-h`, `-H`, initializes PVFS, resolves the mount, creates credentials, prints aggregate fsid/server/handle/byte statistics, explains aggregate free-space assumptions, then prints meta server and I/O server stats by filtering `server_type` bits.

**State and persistence:** It is read-only and observes live server state, including RAM, uptime, load averages, handle counts, and byte counts.

**Dependencies and integration points:** It depends on sysint statfs, management statfs, server reporting, and mount resolution. It is operationally useful after server/disk changes or when aggregate free space looks unexpectedly low.

**Risks and edge cases:** In human-readable aggregate output, `bytes total` prints `scratch_size` instead of `scratch_total`, so total duplicates available. The program does not call `PVFS_sys_finalize` before returning. It does not check the return from `PVFS_mgmt_statfs_all` before iterating. Tests should cover raw and human output, SI mode, failed management statfs, mixed meta/I/O servers, and the aggregate total formatting bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-statfs.c -->
