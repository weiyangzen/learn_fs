# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.h

Purpose: declares sysfs lifecycle hooks for the anti-rollback `qat_svn` group.

Important API: `adf_sysfs_start_arb(struct adf_accel_dev *)` and `adf_sysfs_stop_arb(struct adf_accel_dev *)`.

Control flow and state: header only. Implementation stores sysfs-added and retry state in anti-rollback hardware data.

Dependencies and integration: called from device start/stop in `adf_init.c`.

Risks and test signals: build coverage catches declaration drift. Runtime tests should verify the sysfs group is gated by hardware anti-rollback support and removed on stop.
