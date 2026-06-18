# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_mon.c

## Purpose
This file implements Siena MCDI sensor handling and optional Linux hwmon device registration. It maps firmware sensor IDs to human-readable labels, hwmon classes, units, and port affinity; logs asynchronous sensor-warning events; queries firmware sensor pages; allocates a DMA buffer for sensor readings; and creates read-only sysfs hwmon attributes for values, thresholds, alarms, and labels.

## Important APIs, Types, And Functions
- `enum efx_hwmon_type` classifies firmware sensors as temperature, cooling/fan, voltage, current, power, or unknown.
- `efx_mcdi_sensor_type[]` maps `MC_CMD_SENSOR_*` IDs to label, hwmon type, and optional port number. The table includes board, PHY, fan, regulator, AOE, current, power, internal ADC, ambient, airflow, and hotpoint sensors known to this driver.
- `sensor_status_names[]` maps firmware sensor state IDs to text used in warning logs.
- `efx_siena_mcdi_sensor_event()` decodes MCDI sensor events and emits a netdev hardware error message with sensor ID, label, state text, value, and unit.
- Under `CONFIG_SFC_SIENA_MCDI_MON`, `struct efx_mcdi_mon_attribute` stores one sysfs `device_attribute` plus sensor index/type, hwmon class, cached threshold value, and generated attribute name.
- `efx_mcdi_mon_update()` sends `MC_CMD_READ_SENSORS` with a DMA address and length so firmware writes current sensor entries into the DMA buffer.
- `efx_mcdi_mon_get_entry()` caches readings for one second under `update_lock` and returns a requested sensor entry.
- Attribute readers `efx_mcdi_mon_show_value()`, `efx_mcdi_mon_show_limit()`, `efx_mcdi_mon_show_alarm()`, and `efx_mcdi_mon_show_label()` implement hwmon sysfs reads.
- `efx_siena_mcdi_mon_probe()` discovers sensors via paged `MC_CMD_SENSOR_INFO`, allocates DMA and attribute arrays, creates conventional hwmon names, and registers `hwmon_device_register_with_groups()`. `efx_siena_mcdi_mon_remove()` unregisters and frees those resources.

## Control Flow
Sensor events can be processed regardless of hwmon registration. `efx_siena_mcdi_process_event()` dispatches sensor event qwords to the driver's sensor handler, which extracts monitor, state, and value fields, looks up metadata if known, substitutes fallback text for unknown sensor names, and logs a hardware warning/error.

When hwmon support is enabled, probe first walks `MC_CMD_SENSOR_INFO` pages by repeatedly setting `SENSOR_INFO_EXT_IN_PAGE`, reading the response mask, counting present sensors, and following the `MC_CMD_SENSOR_PAGE0_NEXT` bit. If no sensors are present, it returns success without registering a device. Otherwise it allocates a DMA buffer sized for one `MC_CMD_SENSOR_VALUE_ENTRY_TYPEDEF` per present sensor, initializes the update mutex, performs an initial sensor read, allocates maximum possible attribute objects and attribute pointers, then walks the same paged sensor masks to build sysfs attributes.

For each present sensor, probe skips known sensors that belong to a different physical port. It selects hwmon prefix/index conventions (`temp` and `fan` are 1-based, `in` is 0-based, `curr` and `power` are 1-based), reads min/max threshold pairs from the sensor info entry, and creates `<prefix><n>_input`, `_min`, `_max`, optional `_crit`, `_alarm`, and optional `_label` attributes. Finally it registers a hwmon device with a single attribute group. On any failure after allocation, the shared fail path calls `efx_siena_mcdi_mon_remove()`.

Sysfs reads take the device's parent driver data to recover `struct efx_nic`, lock `update_lock`, refresh from firmware only if the cached buffer is at least one second old, copy the requested entry from DMA memory, and unlock. Value and limit reads convert temperature from degrees C to millidegrees and power from watts to microwatts to match Linux hwmon conventions. `NO_READING` maps to `-EBUSY`; alarms report non-OK firmware states as `1`.

## State And Persistence
Runtime state is stored in `struct efx_mcdi_mon`: DMA buffer, update mutex, last update jiffies, registered hwmon device, dynamic attribute array, attribute group, group list, and attribute count. Each attribute stores immutable sensor metadata and threshold values captured during probe. The DMA buffer holds the most recent firmware-written sensor values and is refreshed on demand with a one-second cache window.

There is no disk persistence. Firmware remains the authoritative source of sensor topology, thresholds, states, and readings. Sysfs attributes are created at probe and persist until `efx_siena_mcdi_mon_remove()` unregisters the hwmon device and frees arrays/DMA memory.

## Dependencies And Integration Points
The file depends on Linux hwmon, sysfs device attributes, slab allocation, bit operations, jiffies caching, and the Siena DMA buffer helpers `efx_siena_alloc_buffer()`/`efx_siena_free_buffer()`. It consumes MCDI protocol definitions from `mcdi_pcol.h` and request-buffer helpers from `mcdi.h`. It is called from Siena probe/remove paths in `siena.c` when `CONFIG_SFC_SIENA_MCDI_MON` is enabled and from the MCDI event dispatcher for sensor events. It depends on `efx_port_num()` to hide per-port sensors that do not belong to the current NIC function.

## Risks And Edge Cases
- `efx_siena_mcdi_sensor_event()` warns if the state index is outside `sensor_status_names`, but then indexes the table. If firmware emits a new out-of-range state, this can produce a bad pointer read rather than a graceful fallback.
- Unknown sensor types default to `EFX_HWMON_UNKNOWN` and are exposed with `in`-style naming if present. That may be semantically poor but keeps readings visible.
- The probe path counts all sensors in the firmware masks before later skipping wrong-port sensors; allocation is intentionally sized for the upper bound, so attribute storage can be larger than used.
- Attribute names are limited to 12 bytes. Current hwmon names fit, but adding longer prefixes or large indices could truncate names through `strscpy()` or `snprintf()`.
- `efx_mcdi_mon_get_entry()` copies the requested DMA entry even if `efx_mcdi_mon_update()` failed; it still returns the error, so current readers do not use the copied value, but future callers must preserve that ordering.
- Sensor info page handling depends on the page-next bit and variable response length checks. New firmware page formats or masks wider than 32 bits would require updates.
- Remove must unregister hwmon before freeing attributes and DMA memory because sysfs callbacks dereference both.

## Test Signals
Build with `CONFIG_SFC_SIENA_MCDI_MON` enabled and disabled. Runtime tests should verify sensor-info enumeration across one and multiple pages, no-device behavior when firmware reports zero sensors, correct filtering of PHY0/PHY1 port-specific sensors, sysfs attribute names and permissions, one-second cache behavior, value conversions for temperature and power, `-EBUSY` on `NO_READING`, alarm output for warning/fatal/broken states, label output for known sensors, clean fail-path cleanup after allocation or registration failures, clean remove/unload with active sysfs readers, and correct log output for sensor events including unknown sensor IDs.
