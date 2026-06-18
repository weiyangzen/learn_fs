# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.h

Purpose: declares rate-limiting sysfs group add/remove functions.

Important API: `adf_sysfs_rl_add(struct adf_accel_dev *)` and `adf_sysfs_rl_rm(struct adf_accel_dev *)`.

Control flow and state: no header behavior. Implementation stores sysfs-added state inside `adf_rl_interface_data`.

Dependencies and integration: called by `adf_rl_start` and `adf_rl_stop`.

Risks and test signals: build catches signature drift. Runtime test should verify `qat_rl` appears only when RL firmware capability and initialization succeed, and is removed during stop before RL state is freed.
