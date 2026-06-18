# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra234.c

## Purpose

This file describes Tegra234 pinmux hardware for the common Tegra pinctrl core. Unlike older single-instance Tegra tables, it provides separate SoC data for the main pinmux block and the always-on pinmux block. It maps Tegra234 pins, mux functions, normal groups, AON groups, register offsets, and supported electrical-control bits into `struct tegra_pinctrl_soc_data` records.

## Important APIs, Types, and Data

The file starts with pin-number enums for the main and AON domains, then defines `tegra234_pins[]`, many one-pin arrays, `enum tegra_mux_dt`, `tegra234_functions[]`, macro helpers for optional pin and drive register entries, `tegra234_groups[]`, `tegra234_pinctrl`, `tegra234_aon_pins[]`, `tegra234_aon_groups[]`, and `tegra234_pinctrl_aon`. The source contains 199 `PINCTRL_PIN()` entries across both domains and 199 `PINGROUP()` table entries. `DRV_PINGROUP_ENTRY_Y()` and `DRV_PINGROUP_ENTRY_N()` model whether a pad has drive controls; `PIN_PINGROUP_ENTRY_Y()` and `PIN_PINGROUP_ENTRY_N()` model whether normal mux/pull/tristate/input-related fields exist.

## Control Flow

`tegra234_pinctrl_init()` registers a platform driver at `arch_initcall`. `tegra234_pinctrl_probe()` reads match data with `device_get_match_data(&pdev->dev)` and passes either `tegra234_pinctrl` or `tegra234_pinctrl_aon` to `tegra_pinctrl_probe()`. The OF table distinguishes `nvidia,tegra234-pinmux` from `nvidia,tegra234-pinmux-aon`; both use the same platform driver and common Tegra pinctrl implementation after match selection.

## State and Persistence

The file provides static SoC metadata only. Hardware state is persistent in MMIO pinmux registers written by the shared Tegra core in response to pinctrl consumers. The main and AON data sets intentionally do not set `ngpios` or `gpio_compatible` in this file, so GPIO coupling differs from Tegra30/Tegra210 and is expected to be handled by the broader Tegra234 GPIO/pinctrl integration.

## Dependencies and Integration Points

It depends on the common Tegra pinctrl data model, platform driver core, OF match data, and Linux pinctrl consumers. The table exposes `schmitt_in_mux`, `drvtype_in_mux`, and `sfsel_in_mux`, while leaving `hsm_in_mux` false. It integrates with Device Tree through names such as `nvidia,tegra234-pinmux`, `nvidia,tegra234-pinmux-aon`, group names, and function strings including PCIe, EQOS, QSPI, SDMMC1, UFS, CAN, UART, I2C, SPI, audio, display, and AON control signals.

## Risks

This is register-description-heavy code. The main risks are mismatched main/AON domains, incorrect match data, wrong register bank or offset, and optional-field sentinels that do not match hardware reality. Some groups intentionally have no drive entry, for example EQOS/QSPI compatibility groups with `DRV_PINGROUP_ENTRY_N`; enabling unsupported drive fields would cause common-core writes to invalid registers. Function enum/string order must remain synchronized. Because the AON block has separate pins but shares `tegra234_functions[]`, name collisions and incomplete group coverage are review targets.

## Test Signals

Compile with Tegra234 pinctrl enabled and verify `MODULE_DEVICE_TABLE(of, ...)` exposes both compatibles. On hardware or emulation, confirm both main and AON platform devices probe, pinctrl debugfs shows expected main/AON groups, and DT states for SDMMC1, QSPI, EQOS, PCIe reset/clkreq, UFS, CAN, UART, and I2C apply without invalid register accesses. Regression tests should include suspend/resume-sensitive AON pads and a check that groups with no drive entry reject or ignore drive settings through the common core.
