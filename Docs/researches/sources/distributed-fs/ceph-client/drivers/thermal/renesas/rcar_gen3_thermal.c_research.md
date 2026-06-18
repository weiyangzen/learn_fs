# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rcar_gen3_thermal.c

Purpose: Renesas R-Car Gen3, Gen4, and RZ/G2 THS thermal sensor driver. It supports multiple TSC MMIO blocks, reads fused or fallback calibration points, computes piecewise linear conversion coefficients, registers OF thermal zones, and optionally handles threshold IRQs.

Important functions and types: `struct rcar_gen3_thermal_priv`, `struct rcar_gen3_thermal_tsc`, `struct rcar_thermal_info`, fuse descriptor types, `rcar_gen3_thermal_get_temp()`, `rcar_gen3_thermal_set_trips()`, `rcar_gen3_thermal_irq()`, `rcar_gen3_thermal_read_fuses()`, `rcar_gen3_thermal_init()`, `rcar_gen3_thermal_request_irqs()`, `rcar_gen3_thermal_probe()`, and `rcar_gen3_thermal_resume()`.

Control flow: probe installs the OF match data, tries to request two optional IRQs, enables runtime PM, maps up to five TSC resources, reads fuses or default pseudo calibration values, calculates shared and per-TSC coefficients, initializes each hardware block, registers one thermal zone per TSC, and adds hwmon sysfs with a devm cleanup action.

Temperature and trip conversion: the current `REG_GEN3_TEMP` value is compared with `thcode[1]` to choose below or above coefficient sets. Conversion uses datasheet-derived `PTAT` and `THCODE` values and reports milli-Celsius. The inverse conversion programs low and high threshold registers for `set_trips()`.

IRQ behavior: two optional IRQs are requested with a shared threaded handler. The handler checks each TSC `IRQSTR`, clears it, and calls `thermal_zone_device_update()` for zones with nonzero status. If IRQ request fails, `set_trips` is disabled and the driver falls back to thermal framework polling.

State and persistence: persistent state is in fuses and THS registers. Driver state holds per-TSC bases, zones, `thcode[]`, coefficients, shared `ptat[]`, threshold split `tj_t`, and SoC-specific scale/adjust constants. Resume re-runs hardware initialization for every TSC but does not re-read calibration.

Dependencies and integration points: platform MMIO resources, optional IRQs, runtime PM, Linux thermal OF, hwmon sysfs, Renesas DT compatibles from RZ/G2 and R-Car Gen3/Gen4, and hardware fuse monitor registers.

Risks: fallback defaults are essential on unfused parts but can reduce accuracy; coefficient math assumes nonzero denominators from calibration data; `platform_get_irq_optional()` errors disable interrupt trip handling; Gen4 fuse address differences are captured in match data and must be kept aligned with compatibles.

Test signals: boot fused and unfused devices; compare reported temperatures against known calibration points; set high and low trips and verify IRQ updates; suspend/resume and ensure THS blocks restart; test each compatible group with correct number of MMIO resources.
