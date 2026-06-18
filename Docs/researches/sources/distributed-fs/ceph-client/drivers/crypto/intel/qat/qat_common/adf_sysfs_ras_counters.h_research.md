# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.h

Purpose: declares RAS sysfs lifecycle hooks and defines atomic counter helper macros for RAS error accounting.

Important API/macros: `adf_sysfs_start_ras`, `adf_sysfs_stop_ras`, `ADF_RAS_ERR_CTR_READ`, `ADF_RAS_ERR_CTR_CLEAR`, and `ADF_RAS_ERR_CTR_INC`.

Control flow and state: macros operate on `ras_errors.counter[ERR]` atomics. Clear iterates over `ADF_RAS_ERRORS` and sets each counter to zero.

Dependencies and integration: relies on `ADF_RAS_ERRORS` and counter enum values from broader QAT device definitions. Used by RAS interrupt handlers and sysfs implementation.

Risks and test signals: macros evaluate `ras_errors` repeatedly, so callers should pass a stable lvalue. Test atomic increments from interrupt context, sysfs reads after increments, and clear behavior for all enum slots.
