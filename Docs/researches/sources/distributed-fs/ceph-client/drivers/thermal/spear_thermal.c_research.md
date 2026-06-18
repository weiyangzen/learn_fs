# sources/distributed-fs/ceph-client/drivers/thermal/spear_thermal.c

Purpose: simple ST SPEAr thermal sensor driver for `st,thermal-spear1340`. It enables the sensor register block and clock, registers a tripless thermal zone, and reports the low 7 bits of the sensor register as Celsius.

Important functions and types: `struct spear_thermal_dev`, `thermal_get_temp()`, `spear_thermal_probe()`, `spear_thermal_exit()`, `spear_thermal_suspend()`, and `spear_thermal_resume()`.

Control flow: probe requires DT property `st,thermal-flags`, maps MMIO, gets and enables the clock, writes the flags to enable the sensor, registers `spear_thermal` as a tripless thermal zone, enables it, and stores the thermal-zone pointer as driver data. Remove unregisters the zone, clears enable flags, and disables the clock.

Temperature path: `thermal_get_temp()` reads the MMIO register, masks `0x7f`, multiplies by 1000, and returns milli-Celsius. There is no calibration or threshold logic in this driver.

State and persistence: driver state is only base address, clock, and enable flags. Suspend clears the flags and disables the clock; resume enables the clock and rewrites the flags.

Dependencies and integration points: platform MMIO, clock API, DT property `st,thermal-flags`, tripless thermal-zone API, and PM sleep ops.

Risks: no `clk_prepare()` is called, only `clk_enable()`, so it assumes the clock is already prepared or provider permits this path; no OF thermal binding integration or trips; the required post-enable data-ready delay is documented but not enforced at probe or resume; temperature conversion is raw and uncalibrated.

Test signals: verify DT property validation; test clock-enable failure paths; read thermal zone after enable and after resume; ensure remove/suspend clears configured flags.
