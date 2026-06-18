# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.c

Purpose: exposes a power-management status debugfs file for devices whose PM implementation provides a status printer.

Important APIs: `adf_pm_dbgfs_add` creates `pm_status`; `adf_pm_dbgfs_rm` removes it. `pm_status_read` delegates to `accel_dev->power_management.print_pm_status` when present.

Control flow and state: add checks `pm->present` and `pm->print_pm_status` before creating the file. Read copies `accel_dev->power_management` locally and calls the driver-provided printer. Remove clears the stored dentry pointer.

Dependencies and integration: depends on debugfs and `struct adf_pm` fields in `adf_accel_dev`. Device-specific PM code supplies the actual status formatting.

Risks and test signals: returns `count` if no printer is set, but add normally prevents that file. Test PM-present and PM-absent devices, debugfs removal during device stop, and that printer callbacks honor user buffer/count/pos semantics.
