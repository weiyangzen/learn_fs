## sources/distributed-fs/ceph-client/include/uapi/linux/dqblk_xfs.h

Purpose: This header defines XFS quota-manager commands and data structures used with `quotactl(2)`. It covers user, group, and project quota accounting, enforcement, limits, usage, timers, warnings, and quota subsystem status.

Important APIs and types: `XQM_CMD()` builds XFS-specific quota commands such as `Q_XQUOTAON`, `Q_XQUOTAOFF`, `Q_XGETQUOTA`, `Q_XSETQLIM`, `Q_XGETQSTAT`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XGETQSTATV`, and `Q_XGETNEXTQUOTA`. `fs_disk_quota_t` stores per-ID hard/soft block, inode, and realtime block limits and usage, warning counts, timers, 40-bit bigtime timer extension bytes, flags, ID, and field mask. Field masks distinguish limit, timer, warning, and accounting updates. `fs_quota_stat_t` and `struct fs_quota_statv` report global quota file/storage and default timer/warning status, with `statv` adding versioning and project quota fields.

Control flow and state: Userspace enables quota accounting/enforcement, reads or sets per-ID limits using field masks, syncs delayed allocation quota updates, removes quota storage, and iterates quota records at or after a given ID. For non-superuser dquots, timers are started/stopped by quota state changes; superuser dquot timer and warning fields act as defaults.

Persistence and dependencies: Quota state persists in XFS quota metadata and in-core dquot caches. Units for block fields are 512-byte basic blocks. The ABI depends on `<linux/types.h>` and `quotactl` command encoding.

Integration points: It integrates with XFS, generic quota tools, project quota administration, and filesystem repair/check tooling.

Risks and test signals: Risks include BB versus filesystem-block unit confusion, signed 40-bit timer encoding, partial updates with incorrect `d_fieldmask`, version fallback for `Q_XGETQSTATV`, and non-transactional accounting field writes. Tests should cover user/group/project quota types, soft-limit timer start/expiry, warning count changes, bigtime timestamps, `Q_XGETNEXTQUOTA` iteration gaps, unsupported statv versions returning `EINVAL`, and sync/removal interactions.
