<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/quota.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/quota.h

Purpose: defines the `quotactl` userspace ABI for user, group, and project quotas, including command encoding, quota formats, limit/usage structures, grace timers, and notification values.

Important APIs and types: `QCMD`, `Q_SYNC`, `Q_QUOTAON/OFF`, `Q_GETFMT`, `Q_GETINFO/SETINFO`, `Q_GETQUOTA/SETQUOTA`, and `Q_GETNEXTQUOTA` define operations. `QFMT_*` names quota formats. `struct if_dqblk`, `struct if_nextdqblk`, and `struct if_dqinfo` carry space/inode limits, usage, grace times, validity masks, and warnings. `QIF_*` and `IIF_*` masks select valid fields; quota netlink warning constants identify soft/hard limit and grace events.

Control flow: userspace calls `quotactl()` with a `QCMD(command,type)` and filesystem path/id/payload. The kernel dispatches to filesystem quota ops, updates or reads quota records, and may emit warnings/events.

State and persistence: quota limits, usage, grace times, and accounting flags persist in filesystem quota files or metadata depending on format. Runtime state includes in-memory dquot caches and enabled/disabled status.

Dependencies and integration points: depends on Linux types and integrates with VFS quota core, ext*/xfs/ocfs2/shmem quota implementations, quota tools, project quotas, and quota warning delivery.

Risks and test signals: risks include block-size unit confusion (`QIF_DQBLKSIZE`), project quota type handling, validity-mask misuse, grace-time semantics, and format-specific behavior. Test quotaon/off, set/get limits for user/group/project, grace expiry, get-next iteration, usage accounting under writes/unlinks, and filesystem format compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/quota.h -->
