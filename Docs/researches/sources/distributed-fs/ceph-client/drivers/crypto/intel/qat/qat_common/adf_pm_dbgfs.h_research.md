# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.h

Purpose: declares PM debugfs lifecycle helpers.

Important API: `adf_pm_dbgfs_add(struct adf_accel_dev *)` and `adf_pm_dbgfs_rm(struct adf_accel_dev *)`.

Control flow and state: header only. The implementation stores dentry state in `accel_dev->power_management`.

Dependencies and integration: used by the broader QAT debugfs lifecycle and device PM implementations.

Risks and test signals: build catches signature drift. Runtime test should confirm PM debugfs appears only when the device reports PM support and is removed cleanly on shutdown/restart.
