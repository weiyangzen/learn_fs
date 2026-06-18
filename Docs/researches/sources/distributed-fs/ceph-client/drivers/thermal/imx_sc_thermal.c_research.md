# sources/distributed-fs/ceph-client/drivers/thermal/imx_sc_thermal.c

## Purpose
NXP i.MX System Controller thermal driver. It exposes multiple firmware-managed resource temperatures as OF thermal zones by issuing SCU MISC GET_TEMP RPCs.

## Important APIs, Types, and Functions
- Global `thermal_ipc_handle` stores the SCU IPC handle.
- `struct imx_sc_sensor` stores thermal zone and SCU resource id.
- Packed request/response structs define the `IMX_SC_MISC_FUNC_GET_TEMP` RPC payload.
- `imx_sc_thermal_get_temp()` builds an SCU RPC for the sensor's resource id and converts celsius/tenths to millicelsius.
- `imx_sc_thermal_probe()` gets the SCU handle, iterates match-data resource ids until `-1`, registers available OF thermal zones, and adds hwmon sysfs.

## Control Flow
Probe obtains the firmware IPC handle and resource-id array from OF match data. For each resource id, it allocates a sensor and attempts to register a thermal OF zone using that resource id as the zone id. `-ENODEV` from registration means no DT thermal-zone description and is skipped; other errors abort probe. Reads synchronously call SCU firmware and return the reported temperature.

## State and Persistence
State is per-sensor resource id and thermal zone. The IPC handle is global. Temperatures are not cached.

## Dependencies and Integration Points
Depends on i.MX SCU firmware IPC, DT resource bindings, thermal OF zones, hwmon sysfs, and firmware-provided resource identifiers.

## Risks and Edge Cases
- Global IPC handle assumes a single SCU context.
- Firmware call latency/failure directly affects thermal reads.
- Zone ids are SCU resource ids, not dense indices; DT thermal maps must match.
- Sensors without DT zones are silently skipped after freeing their allocation.

## Test Signals
Tests should mock SCU RPC success/failure, skipped `-ENODEV` zones, resource iteration termination, temperature conversion with negative tenths, and hwmon addition for registered zones.
