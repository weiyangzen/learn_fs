# sources/distributed-fs/ceph-client/drivers/nvme/host/hwmon.c

## Purpose
This file exposes NVMe controller temperature data through the Linux hwmon subsystem. It reads the NVMe SMART / health log for composite and secondary temperature sensors, exposes critical warnings and critical temperature limits, and maps hwmon max/min threshold attributes to the NVMe Temperature Threshold feature.

## Important APIs, Types, And Functions
The private state is `struct nvme_hwmon_data`, containing the owning `struct nvme_ctrl`, a cached `struct nvme_smart_log`, and `read_lock` to serialize SMART log reads. Public entry points are `nvme_hwmon_init()` and `nvme_hwmon_exit()`, declared through `nvme.h` when `CONFIG_NVME_HWMON` is enabled.

Important helpers are `nvme_get_temp_thresh()`, `nvme_set_temp_thresh()`, `nvme_hwmon_get_smart_log()`, `nvme_hwmon_read()`, `nvme_hwmon_write()`, `nvme_hwmon_read_string()`, and `nvme_hwmon_is_visible()`. The hwmon contract is described by `nvme_hwmon_info`, `nvme_hwmon_ops`, and `nvme_hwmon_chip_info`.

## Control Flow
Initialization allocates `nvme_hwmon_data` and a SMART log buffer, records the controller pointer, initializes the mutex, reads the SMART log once, and registers a hwmon device named `nvme` with `hwmon_device_register_with_info()`. The initial SMART read is important because visibility decisions use `data->log->temp_sensor[]` to decide which secondary sensors exist.

Reads first handle attributes that do not need a SMART log refresh. `hwmon_temp_max` and `hwmon_temp_min` issue Get Features for the selected sensor and over/under threshold type. `hwmon_temp_crit` returns the controller's critical composite temperature from identify data. For live attributes, `nvme_hwmon_read()` locks `read_lock`, refreshes the SMART log with `nvme_get_log()`, and returns composite or secondary sensor temperature in millidegrees Celsius, or the composite temperature alarm bit.

Writes support only `hwmon_temp_max` and `hwmon_temp_min`. The value is converted from millidegrees Celsius to Kelvin, clamped into the NVMe threshold field, combined with sensor select and threshold type bits, and sent through Set Features. Exit unregisters the hwmon device and frees the log and data objects.

## State And Persistence
The only persistent in-memory state is the hwmon device pointer stored in `ctrl->hwmon_device`, the private data object attached to that device, and the cached SMART log. Threshold writes persist in the controller according to NVMe feature semantics, not in this file. Temperature values are refreshed on demand rather than periodically cached.

Visibility is partially determined from identify-controller fields (`wctemp`, `cctemp`) and quirks (`NVME_QUIRK_NO_TEMP_THRESH_CHANGE`, `NVME_QUIRK_NO_SECONDARY_TEMP_THRESH`) plus the initial SMART log sensor presence. If sensor presence changes later, visibility does not automatically expand because hwmon attributes are created at registration time.

## Dependencies And Integration Points
This module depends on the NVMe admin command helpers `nvme_get_log()`, `nvme_get_features()`, and `nvme_set_features()`, temperature constants from NVMe headers, hwmon registration APIs, unit conversion helpers, and unaligned little-endian reads. It is called from controller setup/teardown paths through `nvme_hwmon_init()` and `nvme_hwmon_exit()`.

## Risks
Temperature threshold handling relies on controller compliance. Some devices do not support threshold changes or secondary thresholds, which is why visibility honors quirks. A positive NVMe status from Get/Set Features is normalized to `-EIO`, so callers do not see the exact NVMe status. The SMART log buffer is reused under a mutex, but visibility reads some cached fields without refreshing the log.

Secondary sensor exposure is based on nonzero `temp_sensor[]` entries. A valid sensor reading of zero Kelvin is not realistic, so this is acceptable, but devices with lazy or delayed SMART sensor population may hide attributes until the hwmon device is recreated.

## Test Signals
Test by registering controllers with and without `wctemp`, `cctemp`, secondary sensors, and threshold quirks. Verify sysfs permissions for `temp*_max`, `temp*_min`, `temp*_crit`, `temp*_input`, labels, and alarm. Exercise threshold writes and reads around clamp boundaries, controller errors from Get/Set Features, SMART log read failures, and teardown while userspace polls hwmon attributes.
