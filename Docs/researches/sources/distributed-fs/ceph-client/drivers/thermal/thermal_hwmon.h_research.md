# sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.h

## Purpose
`thermal_hwmon.h` declares the thermal-to-hwmon bridge API and provides no-op stubs when hwmon exposure is disabled.

## Important APIs, Types, and Functions
The header declares `thermal_add_hwmon_sysfs`, `devm_thermal_add_hwmon_sysfs`, and `thermal_remove_hwmon_sysfs`. Disabled builds return success for add paths and no-op for remove.

## Control Flow
There is no runtime control flow in the header. It allows thermal drivers and core registration code to call hwmon setup without open-coding config guards.

## State and Persistence Behavior
No state is owned here. Enabled builds create hwmon sysfs state in `thermal_hwmon.c`; disabled builds preserve no hwmon state.

## Dependencies and Integration Points
The header includes `<linux/thermal.h>` and is consumed by thermal core code and drivers such as the TI thermal common layer.

## Risks and Edge Cases
Callers cannot detect disabled hwmon because stubs return success. That is intentional, but tests that expect sysfs files must run under `CONFIG_THERMAL_HWMON`.

## Test Signals
Compile both config branches and verify consumers build without conditional code. In enabled builds, pair with `thermal_hwmon.c` sysfs tests.
