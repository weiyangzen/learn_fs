# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra30.c

## Purpose

This file is the Tegra30 SoC-specific pinctrl table. It enumerates GPIO-backed pins and non-GPIO system pins, declares pin groups, function names, mux options, drive groups, and register bit layouts for the common Tegra pinctrl core. It supports the older Tegra30 register model where mux/pull/tristate/input/open-drain/ioreset fields live in pinmux bank registers and drive controls live in a separate drive bank.

## Important APIs, Types, and Data

The file defines `_GPIO()`, `_PIN()`, `NUM_GPIOS`, Tegra30 pin IDs, `tegra30_pins[]`, one-pin arrays for each group, large drive grouping arrays such as `drive_lcd2_pins[]`, `enum tegra_mux`, `tegra30_functions[]`, `PINGROUP`, `DRV_PINGROUP`, `tegra30_groups[]`, and `tegra30_pinctrl`. The source contains 260 `PINCTRL_PIN()` entries and 290 `PINGROUP()`/`DRV_PINGROUP()` entries. `PINGROUP()` captures mux functions, register offset, open-drain support, and IO reset support. `DRV_PINGROUP()` captures high-speed mode, Schmitt, low-power mode, drive-down/up fields, and slew-rate fields for drive groups.

## Control Flow

The driver is registered from `tegra30_pinctrl_init()` at `arch_initcall`. Platform matching on `nvidia,tegra30-pinmux` calls `tegra30_pinctrl_probe()`, which passes `tegra30_pinctrl` into `tegra_pinctrl_probe()`. After that, the common Tegra pinctrl code performs all pinctrl operations by resolving pin/group/function names into these tables and writing the described MMIO fields.

## State and Persistence

The file has no mutable runtime state other than static registration of a platform driver. Pin configuration state persists in Tegra30 pinmux/drive registers through the common core. `tegra30_pinctrl` sets `ngpios = NUM_GPIOS` and `gpio_compatible = "nvidia,tegra30-gpio"`, so the common core can expose or coordinate GPIO-capable pads with the Tegra30 GPIO controller.

## Dependencies and Integration Points

It integrates with the common Tegra pinctrl driver, platform bus, Device Tree, Linux pinctrl/pinmux/pinconf APIs, and the Tegra30 GPIO driver. Its group and function names are the ABI consumed by DTS pinctrl states for peripherals such as display, GMI/NAND, SDMMC, UART, I2C, SPI, ULPI, HDMI/CEC, PCIe, audio, keyboard controller, and camera/VI. The SoC flags set `hsm_in_mux = false`, `schmitt_in_mux = false`, and `drvtype_in_mux = false`, meaning those electrical controls are not represented as mux-register fields.

## Risks

The file is highly table-driven and sensitive to numeric accuracy. Incorrect register offsets or bit positions can cause wrong pads to be muxed or electrically misconfigured. Drive group membership is especially risky because a single drive group spans multiple pins; wrong membership affects a whole peripheral bus. `TEGRA_MUX_INVALID` and reserved function entries must stay in the correct function order. Unsupported fields use `-1`; the common core must avoid writes for those fields. Because this is older hardware, regressions may only be visible on real Tegra30 boards.

## Test Signals

Build with Tegra30 pinctrl enabled and boot a DT using `nvidia,tegra30-pinmux`. Verify debugfs pin/group/function inventories, GPIO range behavior against `nvidia,tegra30-gpio`, and live pinctrl state application for SDMMC, UART, I2C, SPI, display, and ULPI. Electrical tests should exercise open-drain I2C groups, IO reset capable VI/SDMMC4 groups, and drive-strength/slew-rate programming on representative drive groups. Review table edits against the Tegra30 TRM and board schematics.
