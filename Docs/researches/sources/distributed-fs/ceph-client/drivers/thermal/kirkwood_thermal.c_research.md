# sources/distributed-fs/ceph-client/drivers/thermal/kirkwood_thermal.c

Purpose: Marvell Kirkwood thermal sensor driver. It maps a single sensor register, registers a tripless thermal zone named `kirkwood_thermal`, and converts a valid raw register field into millidegrees Celsius.

Important APIs/types/functions: `struct kirkwood_thermal_priv` stores the MMIO sensor pointer. `kirkwood_get_temp()` reads the register with `readl_relaxed()`, checks the valid bit at offset 9, extracts the 9-bit temperature field at offset 10, and applies the documented formula `Celsius = (322 - reg) / 1.3625`, scaled to millidegrees. `kirkwood_thermal_probe()` maps resource 0, registers and enables the tripless zone, and stores it as platform driver data. `kirkwood_thermal_exit()` unregisters it.

Control flow: probe is linear: allocate private data, map MMIO, register thermal zone, enable it, and store the handle. Thermal reads fail with `-EIO` if the valid bit is clear; otherwise the converted temperature is returned. Remove unregisters the non-devm thermal zone.

State/persistence: only the thermal-zone handle and MMIO pointer are retained. The driver does not program thresholds, clocks, resets, or persistent hardware state. Dependencies/integration: OF compatible `marvell,kirkwood-thermal`, platform MMIO, thermal core tripless zone API.

Risks: invalid-bit handling means early or transient hardware reads surface as `-EIO`; arithmetic uses unsigned long constants and assumes the raw field stays in documented range; no hwmon sysfs is added. Test signals include valid/invalid register reads, formula spot checks, enable failure cleanup, and remove-time unregister.
