# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_quota_defs.h

Purpose: Defines quota-related shared types, flags, reservation constants, dquot verification hooks, timestamp helpers, and metadir quota inode helpers.

Important APIs and types: `xfs_qcnt_t`, `xfs_dqtype_t`, `XFS_DQUOT_LOGRES`, quota state predicates (`XFS_IS_QUOTA_ON`, user/group/project accounting and enforcement checks), `XFS_QMOPT_*` reservation/modification flags, transaction dquot aliases, `xfs_dqinode_path`, `xfs_dqinode_metafile_type`, dquot verify/repair prototypes, dquot timestamp conversion, sick-mask lookup, and quota inode load/create/link/mkdir APIs.

Control flow: inline helpers map quota type to metadir path strings and metadata file types, asserting on invalid types. Macros separate persistent mount/superblock quota accounting flags from nonpersistent internal operation flags.

State and persistence: quota accounting flags persist in mount/superblock state via values defined in `xfs_log_format.h`; dquot records and quota inode metadata are persistent. `XFS_DQUOT_LOGRES` sizes transaction reservation for worst-case dquot logging.

Dependencies and integration: shared between kernel and userspace libxfs. Integrates with transaction quota modification, metadir quota inode management, dquot buffer verification, and health/scrub code.

Risks and test signals: quota type mapping must stay aligned with metadata inode types; reservation underestimates can deadlock or fail quota updates; persistent and nonpersistent flag spaces must not be confused. Tests should cover user/group/project quota enablement, quotaoff logging, chmod/rename worst-case dquot modifications, metadir quota inode load/create/link, and dquot verifier fuzzing.
