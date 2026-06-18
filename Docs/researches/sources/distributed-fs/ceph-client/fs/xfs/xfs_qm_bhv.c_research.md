# sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_bhv.c

Purpose: Provides quota-related mount behavior helpers outside the core quota manager: quota-aware `statvfs`, mount-time quota state validation, early quota mounting/deferment, and metadir quota state resume.

Important APIs and functions: `xfs_qm_statvfs` reports project-quota-limited filesystem statistics for project quota directory trees. `xfs_qm_newmount` reconciles mount options and on-disk quota accounting/enforcement flags, decides whether quotas must be mounted immediately or deferred until after log recovery, and rejects forbidden read-only/norecovery state changes. `xfs_qm_resume_quotaon` restores metadir quota accounting/enforcement state from the superblock when no quota mount options were supplied. Internal `xfs_fill_statvfs_from_dquot` clamps block and inode totals/free counts to quota limits.

Control flow: During mount, `xfs_qm_newmount` reads on-disk quota flags, checks whether requested in-core state would change quota accounting/enforcement on read-only or norecovery mounts, then either calls `xfs_qm_mount_quotas` immediately when no quotacheck is needed or clears `m_qflags` while returning the saved flags through `needquotamount/quotaflags`. For `statvfs`, the helper gets the project dquot, locks it, and uses soft limits preferentially over hard limits to clamp `kstatfs`.

State and persistence: Reads persistent superblock `sb_qflags` and quota inode state. Mutates only in-core mount quota flags during mount deferment/resume; persistent changes are handled by the main quota manager. `statvfs` uses reserved counts, not merely committed counts, so delayed allocations affect reported free space.

Dependencies and integration: Integrates with the VFS statfs path, mount path, dquot lookup, quota default limit structures, readonly/norecovery checks, metadir feature flags, and `xfs_qm_mount_quotas`.

Risks and invariants: Read-only or norecovery mounts must not trigger quota state transactions; the function returns `-EPERM` if mount options would require a quota state change. Metadir filesystems prefer mount-without-quota-options behavior to restore persisted quota state. `xfs_qm_statvfs` silently falls back to global statfs if the project dquot cannot be obtained.

Test signals: Mount read-only/norecovery filesystems with matching and mismatching quota flags, metadir quota resume without mount options, deferred quotacheck mount path, and project-quota `df` output under block/inode soft and hard limits including realtime inherited trees.
