# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_hwmon.c

## Purpose
`core_hwmon.c` exposes Mellanox/NVIDIA mlxsw switch environmental telemetry and fan controls through Linux hwmon sysfs. It builds dynamic hwmon attribute sets for the main board and, when modular systems report active slots, for line cards. It covers ASIC temperature sensors, highest-temperature history/reset, tachometer RPM/faults, PWM duty, module temperatures, module thresholds, module alarm synthesis, and gearbox temperature sensors.

## Important APIs, Types, and Functions
- `struct mlxsw_hwmon_attr` embeds `device_attribute` and tracks the mlxsw hwmon device plus a `type_index` used to map sysfs attributes to ASIC sensor, module, fan, or gearbox indexes.
- `struct mlxsw_hwmon_dev` owns one hwmon registration: attribute arrays, group pointers, sensor counts, slot index, and active state. `struct mlxsw_hwmon` owns the core/bus references and a flexible array of board/line-card devices.
- Sysfs handlers include `mlxsw_hwmon_temp_show()`, `mlxsw_hwmon_temp_max_show()`, `mlxsw_hwmon_temp_rst_store()`, `mlxsw_hwmon_fan_rpm_show()`, `mlxsw_hwmon_fan_fault_show()`, `mlxsw_hwmon_pwm_show()`, `mlxsw_hwmon_pwm_store()`, and module-specific temperature, threshold, label, and alarm handlers.
- `mlxsw_hwmon_temp_init()`, `mlxsw_hwmon_fans_init()`, `mlxsw_hwmon_module_init()`, and `mlxsw_hwmon_gearbox_init()` query mlxsw registers and populate the dynamic sysfs attribute table through `mlxsw_hwmon_attr_add()`.
- Public lifecycle is `mlxsw_hwmon_init()` / `mlxsw_hwmon_fini()`. Line-card integration is through `mlxsw_linecards_event_ops_register()` with `mlxsw_hwmon_got_active()` / `mlxsw_hwmon_got_inactive()`.

## Control Flow
Initialization queries `MGPIR` to size the flexible line-card array, initializes slot 0, adds attributes by querying `MTCAP`, `MFCR`, `MGPIR`, and `MTMP`, registers the main `mlxsw` hwmon device, and registers line-card event callbacks. Each sysfs read/write builds the relevant register payload, calls `mlxsw_reg_query()` or `mlxsw_reg_write()`, and returns either a numeric sysfs value or a kernel error. On line-card activation, the callback initializes module and gearbox attributes for that slot and registers an additional hwmon device named `linecard#NN`; deactivation unregisters the device and resets its attribute count.

## State and Persistence
State is in memory only. The driver stores dynamic sysfs attributes in fixed-size arrays sized by maximum supported sensors/modules/gearboxes/fans and resets line-card `attrs_count` after unregister. Hardware sensor history is persistent in the device until `temp*_reset_history` sets `mte` and `mtr` in `MTMP`. PWM writes alter hardware fan duty through `MFSC`.

## Dependencies and Integration Points
The file depends on Linux hwmon/sysfs, SFP threshold constants, mlxsw register pack/unpack helpers, `core_env` module temperature threshold helpers, and line-card event registration. It cooperates with `core_linecards.c` so hot-plugged line cards gain telemetry only after the line-card manager marks them active.

## Risks
The dynamic attribute count must remain within `MLXSW_HWMON_ATTR_COUNT`; adding new attributes without updating count macros can overflow arrays. Gearbox sensor indexing is indirect through `mlxsw_hwmon_get_attr_index()` and modulo arithmetic, so off-by-one errors could query the wrong `MTMP` index. Line-card activation failures after partial attribute population do not explicitly clear `attrs_count` unless a device had been registered and later deactivated. Sysfs handlers return raw register errors, so hardware access failures surface directly to userspace.

## Test Signals
Useful tests include reading all generated `/sys/class/hwmon/.../temp*`, `fan*`, and `pwm*` attributes on systems with and without modules, writing valid and invalid PWM values, writing `1` and invalid values to reset-history attributes, unplugging/replugging line cards, and injecting `mlxsw_reg_query()` failures to verify cleanup paths. Kernel logs should show no attribute registration warnings and no use-after-free reports during line-card deactivation.
