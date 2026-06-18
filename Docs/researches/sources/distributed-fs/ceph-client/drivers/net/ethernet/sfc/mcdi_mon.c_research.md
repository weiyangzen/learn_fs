# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_mon.c

## Purpose
`mcdi_mon.c` implements hardware monitoring over MCDI sensor commands. It logs asynchronous sensor events and, when `CONFIG_SFC_MCDI_MON` is enabled, registers a Linux hwmon device with generated sysfs attributes backed by DMA reads from `MC_CMD_READ_SENSORS`.

## Important APIs, Types, And Functions
`enum efx_hwmon_type` classifies sensor units. `efx_mcdi_sensor_type[]` maps firmware sensor IDs to labels, hwmon type, and optional port affinity. `efx_mcdi_sensor_event()` logs sensor events. Under monitor config, `struct efx_mcdi_mon_attribute` stores generated sysfs attribute metadata. `efx_mcdi_mon_probe()` discovers sensors, allocates DMA and attributes, creates hwmon groups, and registers the device. `efx_mcdi_mon_remove()` unregisters and frees resources.

Read helpers include `efx_mcdi_mon_update()`, `efx_mcdi_mon_get_entry()`, value/limit/alarm/label show functions, and `efx_mcdi_mon_add_attr()`.

## Control Flow
Sensor events extract monitor ID, state, and value from the MCDI event, look up label/type/unit when known, and emit a hardware log line. Monitor probe pages through `MC_CMD_SENSOR_INFO`, counts available sensors, skips device creation if none exist, allocates a DMA buffer for all sensor entries, performs an initial update, allocates worst-case attributes, then walks sensor bits again to generate sysfs attributes.

Generated attributes follow hwmon naming: `temp`, `fan`, `in`, `curr`, and `power` prefixes with ABI-specific indexing. Thresholds produce min/max/crit attributes when firmware limits are meaningful. Sysfs reads cache sensor DMA data for one second; value reads convert temperature to millidegrees Celsius and power to microwatts, and return `-EBUSY` for `NO_READING`.

## State And Persistence Behavior
Monitor state is volatile in `struct efx_mcdi_mon`: DMA buffer, update mutex, cache timestamp, hwmon device, attributes, and groups. Sensor values are firmware runtime data copied into host DMA memory. Thresholds and sysfs layout are captured at probe; topology changes after probe are not dynamically reflected. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux hwmon/sysfs helpers, DMA buffer allocation, `net_driver.h`, `mcdi.h`, `mcdi_pcol.h`, and `nic.h`. It integrates with the MCDI event dispatcher for sensor events and with `struct efx_mcdi_data` for optional monitor state.

## Risks And Edge Cases
Firmware may expose unknown sensors or states. Unknown sensor IDs are handled with generic labels/types, but unknown states rely on paranoid warnings and array assumptions. Probe has partial-allocation failure paths cleaned through `efx_mcdi_mon_remove()`. Attribute capacity assumes no more than six attributes per sensor. The one-second cache means reads can be stale, and port filtering must match board semantics.

## Test Signals
Test monitor enabled/disabled, zero sensors, multiple sensor-info pages, port-specific PHY sensors, unknown sensor IDs, `NO_READING` states, short responses, allocation failures, and sensor event logging. Validate sysfs names/units against hwmon ABI and confirm cleanup after failed probe.
