# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-hwmon.c

Purpose: exposes SB-RMI package power telemetry and power cap controls through the Linux hwmon subsystem.

Important APIs and functions: `create_hwmon_sensor_device` registers a hwmon device named `sbrmi`. `sbrmi_read` handles `hwmon_power_input`, `hwmon_power_cap`, and `hwmon_power_cap_max`. `sbrmi_write` handles `hwmon_power_cap`. `sbrmi_is_visible` defines read/write permissions.

Control flow: reads build an `apml_mbox_msg` for current package power or current power limit, or return cached `pwr_limit_max`. Values from firmware are in milliwatts and converted to microwatts for hwmon. Writes convert microwatts to milliwatts, clamp to `[0, pwr_limit_max]`, and send `SBRMI_WRITE_PKG_PWR_LIMIT` through `rmi_mailbox_xfer`.

State and persistence: no private state beyond the `sbrmi_data` pointer passed as drvdata. The maximum power limit is cached during transport probe. The configured cap persists in platform firmware/hardware according to SB-RMI behavior, not in this file.

Dependencies and integration points: depends on hwmon APIs, APML UAPI message structures, and the core mailbox transfer function. It is optionally linked by Kconfig.

Risks: clamping silently changes out-of-range writes rather than reporting an error. If `pwr_limit_max` cache is stale, writes can enforce an obsolete maximum. All mailbox failures propagate to hwmon callers, so sensor reads can block until the core timeout.

Test signals: hwmon sysfs reads/writes for `power1_input`, `power1_cap`, `power1_cap_max`, unit conversion checks, clamp behavior at negative and over-max values, and firmware error injection.
