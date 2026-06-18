# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item_recover.c

Purpose: Replays dquot and quotaoff log items during recovery, suppressing obsolete quota records after quotaoff and validating individual dquot payloads before writing quota metadata.

Important APIs, types, and functions: Defines recovery ops `xlog_dquot_item_ops` and `xlog_quotaoff_item_ops`, with callbacks `xlog_recover_dquot_ra_pass2()`, `xlog_recover_dquot_commit_pass2()`, and `xlog_recover_quotaoff_commit_pass1()`.

Control flow: Quotaoff pass1 records disabled quota types in `log->l_quotaoffs_flag`. Dquot pass2 validates vector size and type, skips disabled quota types, verifies the logged dquot, reads the containing dquot buffer, skips replay if on-disk LSN is newer, copies the dquot, updates CRC, verifies the recovered block, and queues writeback.

State and persistence: Mutates quota inode dquot blocks during recovery and marks buffers `_XBF_LOGRECOVERY`. Quotaoff state is transient recovery state.

Dependencies and integration points: Depends on mount quota flags, dquot verifiers/checksums, buffer recovery delwri lists, quotaoff log formats, and log recovery registration.

Risks and test signals: Risks are replay after quotaoff, truncated/corrupt log payload acceptance, wrong LSN skip behavior, and checksum mismatch. Test crashes around quotaoff, CRC/non-CRC dquots, corrupted log vectors, disabled quota support, and repeated recovery interruption.
