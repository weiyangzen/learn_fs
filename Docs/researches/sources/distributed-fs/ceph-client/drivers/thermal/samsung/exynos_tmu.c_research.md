# sources/distributed-fs/ceph-client/drivers/thermal/samsung/exynos_tmu.c

Purpose: Samsung Exynos TMU driver supporting Exynos3250, 4210, 4412, 5250, 5260, 5420, 5433, and Exynos7 variants. It maps SoC-specific register layouts to common thermal-zone operations for reading temperature, programming trips, handling interrupts, optional emulation, and PM.

Important types and functions: `enum soc_type`, `struct exynos_tmu_data`, `temp_to_code()`, `code_to_temp()`, `sanitize_temp_error()`, `exynos_tmu_initialize()`, `exynos_thermal_zone_configure()`, SoC-specific set-low/high/critical and initialize/control/read functions, `exynos_tmu_threaded_irq()`, `exynos_map_dt_data()`, `exynos_set_trips()`, `exynos_tmu_probe()`, and suspend/resume callbacks.

Control flow: probe allocates `exynos_tmu_data`, optionally enables the `vtmu` regulator, maps DT data and chooses callback functions based on compatible, prepares clocks including optional triminfo and special clocks, initializes hardware and trim data, registers thermal zone 0, configures critical trip threshold, requests a shared rising threaded IRQ, and enables TMU control.

Temperature and calibration: TMU raw codes convert to Celsius through one-point or two-point calibration using `temp_error1` at 25 C and `temp_error2` at 85 C. Trim values are sanitized against SoC-specific min/max fallback ranges. Exynos5433 reads sensor ID and calibration mode from trim info and can switch to two-point calibration.

Trip and IRQ behavior: `set_trips()` enables/disables low and high threshold interrupts via SoC callback methods. Critical trip setup is performed once from the thermal zone's critical trip. IRQ handling updates the zone, clears pending interrupts through the selected register layout, and leaves detailed interrupt cause handling as a TODO.

State and persistence: driver state stores base addresses, clocks, calibration values, selected callbacks, thermal zone, and enabled flag. Hardware state includes control register, threshold registers, interrupt enables/pending state, and optional emulation registers. Remove disables TMU and unprepares clocks. Suspend disables TMU; resume reinitializes and enables it.

Dependencies and integration points: DT compatibles, OF address and IRQ mapping, thermal OF, regulator API, multiple clocks, optional thermal emulation, Exynos thermal DT binding calibration constants, and IRQ subsystem.

Risks: callback selection in `exynos_map_dt_data()` is dense and SoC-specific; missing critical trips fail most SoCs except Exynos5433 special case; Exynos5420 external triminfo requires a second MMIO resource and clock; some SoCs lack true hardware critical handling and use normal interrupts; clock enable/disable is manually paired inside locks.

Test signals: boot one representative for 4210, 4412/5420, 5433, and Exynos7 paths; verify one-point and two-point calibration; set low/high trips and confirm interrupt enables; trigger IRQ and ensure pending bits clear; test thermal emulation when enabled; suspend/resume and confirm TMU reinitialization.
