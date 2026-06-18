# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.c

## Purpose
Registers an `hwmon` temperature sensor for supported Intel `ice` devices and reads internal chip temperature thresholds through firmware AdminQ.

## Important APIs, types, and functions
- `ice_hwmon_init()` registers an `hwmon` device named `ice` when internal readings are supported.
- `ice_hwmon_exit()` unregisters `pf->hwmon_dev`.
- `ice_hwmon_read()` handles `hwmon_temp_input`, `hwmon_temp_max`, `hwmon_temp_crit`, and `hwmon_temp_emergency` by calling `ice_aq_get_sensor_reading()`.
- `ice_hwmon_is_visible()` exposes those attributes as read-only.
- `ice_is_internal_reading_supported()` gates registration to PF 0 and capability bit `ICE_SENSOR_SUPPORT_E810_INT_TEMP_BIT`.

## Control flow
Initialization checks support and registers with `hwmon_device_register_with_info()`. Reads are demand-driven by the hwmon core; each read fetches a fresh sensor response from firmware and converts register degrees to millidegrees Celsius using `TEMP_FROM_REG`. Exit unregisters only if registration succeeded.

## State and persistence behavior
The only persistent driver state is `pf->hwmon_dev`. Sensor values are not cached; they are retrieved from firmware per read. No host files are written except sysfs nodes managed by the hwmon core.

## Dependencies and integration points
Depends on `linux/hwmon.h`, `ice_aq_get_sensor_reading()`, device capabilities, and `dev_get_drvdata()` returning `struct ice_pf`. Called from PF initialization and teardown paths when `CONFIG_ICE_HWMON` is enabled.

## Risks
Firmware older than the documented support level may not provide readings, so capability gating is essential. The implementation currently leaves `pf->hwmon_dev` unchanged after unregister; callers must not double-unregister without guarding. Read failures are ratelimited warnings but propagate the AdminQ error to sysfs.

## Test signals
Build with `CONFIG_ICE_HWMON` enabled and disabled. Runtime signals include creation of `temp*_input`, `temp*_max`, `temp*_crit`, and `temp*_emergency` sysfs attributes only on PF 0 with the capability bit set, successful millidegree values, and ratelimited warnings under injected AdminQ failures.
