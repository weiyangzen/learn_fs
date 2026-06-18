# sources/distributed-fs/ceph-client/drivers/thermal/qoriq_thermal.c

Purpose: NXP/Freescale QorIQ and i.MX8MQ Thermal Monitoring Unit driver. It programs TMU range and calibration registers from device tree, exposes up to 16 monitoring sites as thermal zones, and polls immediate temperature registers.

Important APIs and functions: `tmu_get_temp()`, `qoriq_tmu_register_tmu_zone()`, `qoriq_tmu_calibration()`, `qoriq_tmu_init_device()`, `qoriq_tmu_probe()`, `qoriq_tmu_suspend()`, and `qoriq_tmu_resume()`. `struct qoriq_tmu_data` owns version, range registers, regmap, clock, and sensor array; `struct qoriq_sensor` supplies the thermal-zone private ID.

Control flow: probe maps the MMIO resource through a regmap with endian selected by the `little-endian` DT property, enables an optional clock, registers a devm action to disable monitoring, reads the IP block revision, initializes the TMU in disabled/polling mode, writes calibration/range data from `fsl,tmu-range` and `fsl,tmu-calibration`, then registers all thermal zones present in the OF thermal map.

Temperature path: `tmu_get_temp()` first checks that measurement is enabled in `REGS_TMR`, then polls `REGS_TRITSR(id)` until `TRITSR_V` is set. Version 1 returns an 8-bit Celsius value. Version 2 treats the value as Kelvin, with `TRITSR_TP5` adding half-Kelvin resolution before converting to milli-Celsius.

State and persistence: hardware registers hold range, calibration, monitor-site enablement, update interval, and measurement enable state. The driver keeps a copy of written range values in `ttrcr[]`, but calibration is not persisted outside hardware. Suspend clears measurement enable and disables the clock; resume reenables the clock, clears v2 command state, and re-enables measurement.

Dependencies and integration points: platform DT compatibles `fsl,qoriq-tmu` and `fsl,imx8mq-tmu`, regmap access tables for safe read/write ranges, optional clock, OF thermal zones, and hwmon sysfs helper.

Risks: DT calibration properties are mandatory and format-sensitive; endianness is DT-controlled and wrong settings corrupt register programming; v1/v2 monitor-site bit ordering differs; no Linux IRQ handler is used even though hardware has interrupt registers, so responsiveness depends on thermal framework polling plus enabled hardware overheat behavior.

Test signals: boot with v1 and v2 compatible hardware or emulation; verify invalid `fsl,tmu-range` lengths are rejected; check Celsius and Kelvin conversion paths; confirm only DT-described zones are registered; run suspend/resume while measurement is active; inspect hwmon exposure.
