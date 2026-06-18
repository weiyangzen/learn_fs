# sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/sun8i_thermal.c` is the platform thermal sensor driver for Allwinner sun8i/sun50i/sun20i THS blocks. It maps the MMIO THS register bank through regmap, calibrates sensor channels from NVMEM efuse data when available, registers one thermal zone per SoC sensor, and updates those zones from data-ready interrupts. The source was read as a complete 736-line file.

## Important APIs, Types, and Functions

The main data types are `struct ths_thermal_chip`, the SoC-specific operations/data table; `struct ths_device`, the devm-owned driver state; and `struct tsensor`, the per-zone channel object passed as thermal-zone private data. Important functions include `sun8i_ths_probe()`, `sun8i_ths_resource_init()`, `sun8i_ths_register()`, `sun8i_ths_get_temp()`, `sun8i_irq_thread()`, `sun8i_h3_ths_calibrate()`, `sun50i_h6_ths_calibrate()`, `sun8i_h3_thermal_init()`, and `sun50i_h6_thermal_init()`. The thermal API surface is the `ths_ops.get_temp` callback.

## Control Flow

Probe allocates `ths_device`, selects `ths_thermal_chip` via `of_device_get_match_data()`, maps the THS registers, enables/reset clocks as required by the chip descriptor, optionally accesses an SRAM control regmap for H616, and runs calibration. After the IRQ number is obtained, the chip-specific init routine programs acquisition timing, filtering, sampling period, channel enable bits, and data interrupt masks. The driver then registers all configured sensor zones with `devm_thermal_of_zone_register()` and only requests the threaded IRQ at the end to avoid updates before zones exist. Runtime temperature reads fetch a channel register, reject zero as no data yet with `-EAGAIN`, convert raw codes with the chip-specific formula, then apply `ft_deviation`. The IRQ thread acks per-channel status bits through the SoC-specific `irq_ack()` helper and calls `thermal_zone_device_update()` for each registered zone.

## State and Persistence Behavior

State is devm-owned and tied to the platform device lifetime. Calibration values are programmed into hardware registers at probe and are not persisted by the driver; the persistent source is NVMEM efuse data named `calibration`. Thermal zone state is owned by the thermal core. The H616 SRAM field is a one-bit hardware integration setting cleared during init.

## Dependencies and Integration Points

The driver depends on regmap, platform MMIO resources, reset/clock frameworks, NVMEM consumer APIs, optional SRAM regmap lookup through an `allwinner,sram` phandle, IRQ support, Device Tree compatible matching, `devm_thermal_of_zone_register()`, and `devm_thermal_add_hwmon_sysfs()`. Supported compatible strings include `allwinner,sun8i-a83t-ths`, `sun8i-h3-ths`, `sun8i-r40-ths`, `sun50i-a64-ths`, `sun50i-a100-ths`, `sun50i-h5-ths`, `sun50i-h6-ths`, `sun20i-d1-ths`, and `sun50i-h616-ths`.

## Risks and Edge Cases

Calibration is best-effort except for probe deferral; missing NVMEM leaves hardware working but less accurate. `sun8i_ths_resource_init()` calls `clk_set_rate(tmdev->mod_clk, 24000000)` even on chips where `has_mod_clk` is false, so behavior relies on the clock API tolerating the stored value on those platforms. Individual thermal-zone registration failures other than `-EPROBE_DEFER` are ignored, so a bad DT zone can silently reduce coverage. Raw zero readings return `-EAGAIN`, which depends on the thermal core recheck path. H6-style efuse packing for sensor 3 and 12-bit calibration clipping are easy to regress.

## Test Signals

Useful signals are DT binding/probe tests for each compatible, NVMEM-present and NVMEM-missing boot logs, IRQ-driven `thermal_zone_device_update()` behavior, sysfs/hwmon temperature reads after first conversion, calibration register programming checks on H3 and H6/H616 layouts, and suspend/resume or unbind tests that confirm devm cleanup asserts resets and disables clocks.
