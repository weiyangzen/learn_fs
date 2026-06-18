# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-hwmon.c

## Purpose

`ufs-hwmon.c` exposes UFS temperature monitoring through the Linux hwmon subsystem and forwards UFS exception events as hwmon alarms.

## Important APIs, Types, and Functions

`struct ufs_hwmon_data` stores the `ufs_hba` pointer and enabled exception mask. Public functions are `ufs_hwmon_probe()`, `ufs_hwmon_remove()`, and `ufs_hwmon_notify_event()`. Core callbacks are `ufs_hwmon_read()`, `ufs_hwmon_write()`, and `ufs_hwmon_is_visible()`.

## Control Flow

Probe allocates per-device data and registers a hwmon chip named `ufs` with one temp channel exposing enable, input, critical, and low-critical values. Reads lock `host_sem`, reject access while shutting down, resume runtime PM, then query UFS temperature and boundary attributes. Writes only accept `temp_enable` values 0 or 1 and update the user exception-event mask for urgent temperature notifications.

## State and Persistence Behavior

Runtime state is `hba->hwmon_device`, allocated `ufs_hwmon_data`, and UFS device exception-event masks. Temperature values come from device attributes and are converted from UFS encoded Celsius offset to millidegrees Celsius.

## Dependencies and Integration Points

It depends on hwmon, UFS query attributes, runtime PM, `host_sem`, and exception-event mask helpers. It integrates UFS thermal alerts with standard userspace monitoring.

## Risks and Test Signals

Risks include query failures returning transient sysfs errors, incorrect enable reporting when masks are partially supported, temperature value zero mapping to `-ENODATA`, and alarm notification mismatch. Test signals include hwmon device creation/removal, reading all attributes, toggling enable, runtime-suspended access, and high/low temperature exception events producing hwmon notifications.
