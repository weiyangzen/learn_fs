# sources/distributed-fs/ceph-client/drivers/thermal/rockchip_thermal.c

Purpose: Rockchip TSADC thermal driver for many Rockchip SoCs. It abstracts multiple TSADC hardware generations through chip-data callbacks, registers one thermal zone per channel, programs software alarm trips and hardware TSHUT thresholds, applies optional eFuse trim, and supports suspend/resume reinitialization.

Important types and functions: `struct rockchip_tsadc_chip`, `struct chip_tsadc_table`, `struct rockchip_thermal_data`, `struct rockchip_thermal_sensor`, ADC conversion helpers `rk_tsadcv2_temp_to_code()` and `rk_tsadcv2_code_to_temp()`, generation-specific initialize/control/IRQ/alarm/TSHUT functions, `rockchip_configure_from_dt()`, `rockchip_get_trim_configuration()`, `rockchip_thermal_register_sensor()`, `rockchip_thermal_probe()`, and PM callbacks.

Control flow: probe gets IRQ, chip match data, sensor array, MMIO, reset, `tsadc` and `apb_pclk` clocks, resets the controller, parses DT TSHUT temperature/mode/polarity and optional `rockchip,grf`, initializes hardware through the chip callback, attaches child-node trim data by channel, registers every sensor thermal zone, requests threaded IRQ, enables automatic conversion, enables zones, and adds hwmon sysfs.

Temperature path: per-sensor `get_temp` calls the chip-specific register read, converts raw ADC code through a piecewise linear table with interpolation, then subtracts sensor trim temperature. Conversion tables may be ADC-incrementing or ADC-decrementing and use different masks for v2/v3/v4 data widths.

Trip and shutdown behavior: `set_trips()` programs only the high alarm threshold and adds sensor trim before converting to ADC code. Hardware TSHUT is configured at registration and resume through `set_tshut_mode()` and `set_tshut_temp()`, clamped to `RK_MAX_TEMP`, and can target CRU reset or GPIO/PMIC depending on DT or chip defaults. The IRQ thread acknowledges hardware status and updates all thermal zones.

Calibration and trim: newer chips can provide `get_trim_code()`, with controller-level `trim_base`, `trim_base_frac`, and fallback `trim`, plus per-channel child-node `trim`. Trim code is converted to a temperature offset using a chip `trim_slope`.

State and persistence: state lives in clocks, reset, GRF settings, conversion registers, alarm registers, TSHUT registers, and per-sensor trim offsets. Suspend disables zones and controller, turns off clocks, and selects sleep pinctrl state. Resume re-enables clocks, resets and reinitializes hardware, reprograms TSHUT for every channel, restarts auto conversion, reenables zones, and restores default pinctrl.

Dependencies and integration points: OF compatibles for PX30, RV1108, RK3228, RK3288, RK3328, RK3366, RK3368, RK3399, RK3568, RK3576, and RK3588; syscon GRF; NVMEM cells; reset controller; clocks; pinctrl PM; thermal OF; hwmon.

Risks: conversion tables are hardware-specific and interpolation assumes monotonic order; missing required GRF fails probe on selected SoCs; child `reg` values outside channel count silently lose trim; alarm programming ignores the low trip; `rockchip_configure_from_dt()` ignores trim-configuration return value, which can hide trim-read errors; suspend uses `clk_disable()` rather than unprepare because devm enabled clocks were already prepared.

Test signals: compile all compatible chip data; test ADC increment and decrement conversion boundaries; set high trips and verify IRQ update; verify TSHUT programming for CRU and GPIO modes; boot with and without NVMEM trim cells; suspend/resume and confirm TSHUT/auto conversion are restored; check GRF-required platforms fail cleanly without `rockchip,grf`.
