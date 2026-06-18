# sources/distributed-fs/ceph-client/drivers/thermal/thermal_hwmon.c

## Purpose
`thermal_hwmon.c` exposes thermal zones through the hwmon sysfs ABI so userspace monitoring tools can read `tempN_input` and, when available, `tempN_crit`.

## Important APIs, Types, and Functions
Important types are `thermal_hwmon_device`, `thermal_hwmon_attr`, and `thermal_hwmon_temp`. Public APIs are `thermal_add_hwmon_sysfs`, `thermal_remove_hwmon_sysfs`, and `devm_thermal_add_hwmon_sysfs`; show callbacks read current and critical temperatures.

## Control Flow
Adding a zone first finds or creates a shared hwmon device keyed by thermal zone type with hyphens replaced by underscores. It allocates one `thermal_hwmon_temp`, names attributes using the per-type count, creates `tempN_input`, optionally creates `tempN_crit`, and links the temp entry into the hwmon list. Removal reverses file creation, list membership, and device registration when the last zone of a type disappears. The devm helper registers a cleanup action after successful setup.

## State and Persistence Behavior
The module maintains the global `thermal_hwmon_list` protected by `thermal_hwmon_list_lock`. State is in memory only and tied to thermal-zone lifetime; sysfs files persist while their zone and shared hwmon device remain registered.

## Dependencies and Integration Points
It depends on the hwmon thermal namespace, `thermal_zone_get_temp`, zone `get_crit_temp`, sysfs device files, and devres. Thermal drivers call it directly or through devm helpers after registering a zone.

## Risks and Edge Cases
Shared numbering is monotonic per hwmon device and not compacted on removal. Error unwinding must remove partially created files and unregister newly created devices. If critical temperature validity changes after registration, the `tempN_crit` attribute set will not be dynamically adjusted.

## Test Signals
Build with `CONFIG_THERMAL_HWMON`; register multiple zones of the same type; verify shared hwmon naming, temperature reads, critical attr presence, removal cleanup, and devm cleanup on probe failure/remove.
