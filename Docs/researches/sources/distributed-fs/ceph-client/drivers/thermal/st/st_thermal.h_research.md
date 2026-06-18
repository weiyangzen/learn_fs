# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.h

Purpose: internal header for STi thermal core and backend drivers. It defines common register-field IDs, power states, backend operation callbacks, compatible data, runtime sensor state, and exported registration/PM symbols.

Important types: `enum st_thermal_regfield_ids`, `enum st_thermal_power_state`, `struct st_thermal_sensor_ops`, `struct st_thermal_compat_data`, and `struct st_thermal_sensor`.

Control flow role: backend drivers fill `st_thermal_compat_data` and `st_thermal_sensor_ops`; the shared core consumes them in `st_thermal_register()`. The header's `MAX_REGFIELDS` sets the size contract for backend regfield arrays.

State model: `struct st_thermal_sensor` carries the device, thermal zone, ops, compatible data, clock, regmap, common fields (`dcorrect`, `overflow`, `temp_data`), backend fields (`pwr`, `int_thresh_hi`, `int_enable`), IRQ, and optional MMIO base.

Dependencies and integration points: Linux platform, interrupt, regmap, and thermal APIs. Exports `st_thermal_register()`, `st_thermal_unregister()`, and `st_thermal_pm_ops` for backend modules.

Risks: `INT_THRESH_HI` and `TEMP_PWR` both use enum value 0 because they are mutually exclusive backend field meanings; careless backend arrays can allocate the wrong field. The closing comment names `__STI_RESET_SYSCFG_H` rather than the actual guard, a harmless but confusing documentation drift.

Test signals: compile core and memmap backends; verify backend regfield arrays cover all common IDs; inspect suspend/resume symbol linkage in module builds.
