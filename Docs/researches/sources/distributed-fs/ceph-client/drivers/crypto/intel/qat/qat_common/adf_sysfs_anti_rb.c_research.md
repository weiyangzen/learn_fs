# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.c

Purpose: exposes anti-rollback secure-version-number state and commit action through a `qat_svn` sysfs group when supported by the device.

Important APIs: `adf_sysfs_start_arb` and `adf_sysfs_stop_arb`. Attributes are read-only `enforced_min`, `active`, `permanent_min`, and write-only `commit`.

Control flow and state: show handlers resolve `accel_dev` and call `adf_anti_rb_query` with the requested SVN selector. `commit_store` accepts only a true boolean and calls `adf_anti_rb_commit`. Start checks hardware `anti_rb_enabled` callback, adds the group, and marks `sysfs_added`. Stop removes the group, clears `sysfs_added`, and resets `svncheck_retry`.

Dependencies and integration: depends on anti-rollback hardware data and helpers. Lifecycle code starts/stops it after device start/stop.

Risks and test signals: commit is irreversible at hardware/security level; sysfs must only appear when supported. Test unsupported devices, query failures, invalid commit input, successful commit path, and group removal on stop.
