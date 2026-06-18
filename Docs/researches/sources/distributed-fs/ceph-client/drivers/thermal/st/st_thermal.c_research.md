# sources/distributed-fs/ceph-client/drivers/thermal/st/st_thermal.c

Purpose: shared core for STi thermal sensor drivers. It provides common regmap-field allocation, clock/power sequencing, calibration, thermal-zone registration, hwmon exposure, unregister logic, and PM callbacks for backend-specific ST thermal implementations.

Important APIs and functions: exported `st_thermal_register()`, `st_thermal_unregister()`, and `st_thermal_pm_ops`; internal `st_thermal_alloc_regfields()`, `st_thermal_sensor_on()`, `st_thermal_sensor_off()`, `st_thermal_calibration()`, and `st_thermal_get_temp()`.

Control flow: backend probe calls `st_thermal_register()` with its OF match table. The core allocates `struct st_thermal_sensor`, resolves compatible data, initializes a backend regmap, allocates common and backend-specific regfields, gets the `thermal` clock, optionally registers/enables IRQs, powers the sensor, writes default calibration if bootloader did not, registers OF thermal zone 0, stores driver data, and adds hwmon sysfs.

Temperature path: `st_thermal_get_temp()` checks overflow through a regmap field, reads raw temperature data, applies `temp_adjust_val`, multiplies by 1000, and returns milli-Celsius.

State and persistence: backend compatible data supplies regfields, calibration value, adjustment, critical temperature, and ops. Runtime state includes regmap fields, clock, thermal zone, and backend private MMIO or syscon state. Calibration is written to hardware only if the register field is empty.

Dependencies and integration points: regmap/regmap_field, backend `st_thermal_sensor_ops`, OF match data, clock API, thermal OF, hwmon, platform driver data, and exported PM ops used by `st_thermal_memmap.c`.

Risks: `devm_thermal_add_hwmon_sysfs()` return is ignored; unregister mixes devm thermal unregister with manual hwmon removal; backend `register_enable_irq()` runs before power-on, so backend IRQ enable must tolerate that ordering; missing compatible data or ops fails probe.

Test signals: backend probe/remove with MMIO regmap; overflow bit returns `-EIO`; calibration already present versus default write; suspend/resume powers off/on and reenables IRQs; symbol resolution when built as modules.
