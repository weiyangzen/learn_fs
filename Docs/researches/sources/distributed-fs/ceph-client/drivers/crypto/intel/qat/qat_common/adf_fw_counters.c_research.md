## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.c

Purpose: Implements a debugfs `fw_counters` file that snapshots firmware request/response counters per non-admin acceleration engine (AE). It is diagnostic-only and reads live device state through the admin interface when the debugfs file is opened.

Important APIs/functions: `adf_fw_counters_dbgfs_add()` creates the file and stores the dentry in `accel_dev->fw_cntr_dbgfile`; `adf_fw_counters_dbgfs_rm()` removes it. Internally, `adf_fw_counters_get()` checks `adf_dev_started()`, computes `hw_data->ae_mask & ~hw_data->admin_ae_mask`, allocates a flexible `struct adf_fw_counters`, and fills per-AE `Requests` and `Responses` values by calling `adf_get_ae_fw_counters()`. The seq-file operations render a header row and one row per AE.

Control flow and state: State is allocated per file open, assigned to `seq_file->private`, and freed in release. The counters are a point-in-time snapshot rather than a streaming view, so repeated reads of the same opened file do not refresh hardware values. Persistent driver state is limited to the debugfs dentry pointer.

Dependencies/integration: Depends on debugfs, seq_file, QAT admin counters, `adf_accel_dev` status helpers, and `hw_device` AE/admin masks. It integrates with the driver's debugfs setup/teardown path and only works after the device has started.

Risks and test signals: The main risks are stale snapshots, admin command failure propagation, and AE mask/count mismatch returning `-EINVAL`. Tests should exercise unopened/not-started behavior, allocation failure, admin-counter error handling, seq iteration boundaries, and debugfs removal setting the dentry pointer to NULL.
