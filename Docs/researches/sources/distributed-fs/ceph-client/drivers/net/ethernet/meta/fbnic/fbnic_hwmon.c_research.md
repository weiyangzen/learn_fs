# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hwmon.c

## Purpose

`fbnic_hwmon.c` registers a Linux hwmon device for FBNIC temperature and voltage readings. It maps hwmon sensor types to FBNIC MAC sensor IDs and delegates actual sensor reads to the active MAC implementation.

## Important APIs, Types, And Functions

Public functions are `fbnic_hwmon_register()` and `fbnic_hwmon_unregister()`. Internal callbacks are `fbnic_hwmon_sensor_id()`, `fbnic_hwmon_is_visible()`, and `fbnic_hwmon_read()`. `fbnic_hwmon_ops`, `fbnic_hwmon_info`, and `fbnic_chip_info` describe the hwmon chip with one temperature input channel and one voltage input channel.

## Control Flow

Registration first checks `IS_REACHABLE(CONFIG_HWMON)`. If hwmon support is unavailable, it does nothing. Otherwise it calls `hwmon_device_register_with_info()` with chip name `fbnic`, driver data `fbd`, and the chip info. Registration failures are logged as notices and stored as NULL. Unregister similarly returns early if hwmon is unavailable or no hwmon device is registered.

Read flow receives a hwmon type and attribute, maps supported types (`hwmon_temp`, `hwmon_in`) to `FBNIC_SENSOR_TEMP` or `FBNIC_SENSOR_VOLTAGE`, and calls `fbd->mac->get_sensor(fbd, id, val)`. Visibility exposes only `temp_input` and `in_input` as read-only (`0444`).

## State And Persistence

The only state is `fbd->hwmon`, a registered hwmon device pointer. Sensor values are read on demand and not cached here. There is no persistence beyond device lifetime.

## Dependencies And Integration Points

The file depends on Linux hwmon APIs, `fbnic.h`, and `fbnic_mac.h` sensor IDs and MAC operation callbacks. Sensor retrieval likely uses firmware TSENE mailbox helpers through MAC-specific code, but this file remains MAC-agnostic.

## Risks And Edge Cases

If `fbd->mac` or `mac->get_sensor` is not initialized before registration/read, hwmon reads can fail or dereference invalid callbacks; lifecycle ordering must ensure MAC ops are ready. Only one voltage and one temperature channel are exposed, with no labels or limits. The `IS_REACHABLE(CONFIG_HWMON)` guard allows the same object to build when hwmon is modular/unavailable, but callers should not assume `fbd->hwmon` is non-NULL after register.

## Test Signals

Useful checks include registration with hwmon enabled/disabled, sysfs visibility for temp and voltage input only, successful reads returning MAC-provided values, error propagation from `get_sensor`, and clean unregister on remove. No executable tests were run for this research item.
