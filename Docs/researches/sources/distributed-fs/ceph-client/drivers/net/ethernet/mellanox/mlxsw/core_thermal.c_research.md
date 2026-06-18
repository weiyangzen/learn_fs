# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_thermal.c

## Purpose
`core_thermal.c` registers thermal zones and cooling devices for mlxsw ASIC, modules, gearboxes, and line cards. It maps hardware temperature registers into Linux thermal-zone callbacks and maps PWM controls into thermal cooling-device states.

## Important APIs, Types, and Functions
- `struct mlxsw_thermal` owns the main ASIC thermal zone, PWM cooling devices, trip tables, cooling state ranges, and a flexible array of board/line-card thermal areas.
- `struct mlxsw_thermal_area` groups module and gearbox thermal zones for one slot. `struct mlxsw_thermal_module` stores one module/gearbox thermal zone, copied trip table, cooling-state table, module index, and slot index.
- Thermal callbacks include `mlxsw_thermal_get_temp()`, `mlxsw_thermal_module_temp_get()`, `mlxsw_thermal_gearbox_temp_get()`, and `should_bind` variants.
- Cooling callbacks `mlxsw_thermal_get_max_state()`, `mlxsw_thermal_get_cur_state()`, and `mlxsw_thermal_set_cur_state()` translate between thermal state `0..10` and `MFSC` PWM duty `0..255`.
- Lifecycle is `mlxsw_thermal_init()` / `mlxsw_thermal_fini()`, with line-card activation handled by `mlxsw_thermal_got_active()` / `mlxsw_thermal_got_inactive()`.

## Control Flow
Initialization queries slot count, allocates thermal state, copies default trip/cooling tables, queries fan capabilities, zeroes tachometer minimum RPM through `MFSL`, registers one cooling device per active PWM, sets polling delay based on `bus_info->low_frequency`, registers the main `mlxsw` thermal zone, initializes module and gearbox zones for slot 0, registers line-card event ops, then enables the main thermal zone. Module and gearbox init query `MGPIR`, allocate arrays, register named thermal zones, and enable them. Line-card active/inactive events create and destroy the slot's module/gearbox zones.

## State and Persistence
Thermal trips and cooling-state mappings are per-zone in memory and include writable trip temperatures. PWM state is persisted in hardware via `MFSC`. Tachometer minimum RPM is adjusted in hardware during init. Zone registrations and line-card active flags are runtime state only.

## Dependencies and Integration Points
The file depends on Linux thermal framework, mlxsw register access (`MTMP`, `MFCR`, `MFSC`, `MFSL`, `MGPIR`), SFP constants for module thermal defaults, and line-card event registration. It intentionally sets `.no_hwmon = true` because hwmon exposure is handled separately by `core_hwmon.c`.

## Risks
Cooling device binding allows named external devices (`mlxreg_fan`, `emc2305`) and indexes them as cooling device 0, so platform naming changes can affect thermal policy. `mlxsw_thermal_set_cur_state()` clamps nonzero states to a minimum fan state, meaning requests below minimum still drive fans. Init error cleanup must unregister all possible cooling devices, including NULL entries. Line-card zone creation can partially fail and must unwind module zones when gearbox init fails.

## Test Signals
Validate `/sys/class/thermal` zones for ASIC, modules, gearboxes, and line cards; force thermal readings and verify trip binding; change PWM through thermal cooling state; boot low-frequency I2C systems and verify slow polling; hotplug line cards and check zone creation/destruction; inject failures in thermal zone and cooling device registration to confirm cleanup.
