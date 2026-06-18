# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.c

Purpose: exposes RAS error counters through a `qat_ras` sysfs group.

Important APIs: `adf_sysfs_start_ras` and `adf_sysfs_stop_ras`. Attributes are `errors_correctable`, `errors_nonfatal`, `errors_fatal`, and write-only `reset_error_counters`.

Control flow and state: show handlers resolve `accel_dev` and read atomic counters from `accel_dev->ras_errors`. Reset accepts only `1\n` and clears all counters. Start is gated by `ras_errors.enabled`, clears counters, adds the sysfs group, and marks `sysfs_added`. Stop removes the group if present and clears counters again.

Dependencies and integration: RAS interrupt handling increments counters through macros in the header. Lifecycle starts/stops sysfs after device start/stop.

Risks and test signals: start sets `sysfs_added` even if `device_add_group` fails; stop will attempt removal if marked. Test group creation failure handling, reset input validation, atomic counter increments under interrupts, and counter reset across restart.
