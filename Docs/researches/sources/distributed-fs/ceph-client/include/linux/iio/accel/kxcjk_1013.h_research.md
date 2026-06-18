# `sources/distributed-fs/ceph-client/include/linux/iio/accel/kxcjk_1013.h`

Purpose: platform-data contract for the KXCJK-1013 three-axis accelerometer IIO driver.

Important APIs/types/functions: `struct kxcjk_1013_platform_data` with interrupt polarity (`active_high_intr`) and an `iio_mount_matrix` orientation.

Control flow and state: no functions; state is board/platform configuration consumed during driver probe.

Dependencies/integration: depends on IIO core types. Used by board files or platform data paths in addition to firmware-node configuration.

Risks: wrong interrupt polarity prevents data-ready handling; incorrect mount matrix misreports axes; platform data can diverge from device-tree/ACPI paths.

Test signals: probe with platform data, interrupt polarity validation, orientation matrix sysfs output, and sample axis mapping.
