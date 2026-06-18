# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra210.c

## Purpose

This file is the Tegra210 SoC-specific pin controller description. It contains no board policy and almost no custom runtime logic; it maps Tegra210 package pins, GPIO-numbered pads, always-on/system pads, mux functions, pad groups, drive groups, register offsets, and bit positions into `struct tegra_pinctrl_soc_data`. The shared Tegra pinctrl core consumes this data to implement pin muxing, GPIO integration, pull-up/down, tristate, input enable, open-drain, lock, receive-select/high-voltage, high-speed mode, Schmitt, drive type, low-power drive, drive strength, and slew-rate controls.

## Important APIs, Types, and Data

The file defines `_GPIO()`, `_PIN()`, `NUM_GPIOS`, Tegra210 pin IDs, `tegra210_pins[]`, one-pin arrays such as `uart1_tx_pu0_pins[]`, drive grouping arrays such as `drive_sdmmc1_pins[]`, `enum tegra_mux`, `tegra210_functions[]`, `PINGROUP`, `DRV_PINGROUP`, `tegra210_groups[]`, and `tegra210_pinctrl`. `tegra210_pins[]` has 162 `PINCTRL_PIN()` entries. `tegra210_groups[]` has 187 entries, combining normal pin groups and dedicated drive-only groups. `tegra210_pinctrl_probe()` calls the common `tegra_pinctrl_probe()`, and the platform driver binds to `nvidia,tegra210-pinmux` with `pm_sleep_ptr(&tegra_pinctrl_pm)`.

## Control Flow

At `arch_initcall`, `tegra210_pinctrl_init()` registers `tegra210_pinctrl_driver`. Device Tree matching invokes `tegra210_pinctrl_probe()`, which passes the static `tegra210_pinctrl` table to the common Tegra pinctrl driver. Subsequent runtime pinctrl operations are handled by the common core by indexing the `pins`, `functions`, and `groups` arrays and by writing the bank/register/bit fields expanded by the group macros.

## State and Persistence

All state in this file is static, const SoC description data. Persistent effects are hardware register writes performed later by the common core, not by this file directly. The SoC data advertises `ngpios = NUM_GPIOS` and `gpio_compatible = "nvidia,tegra210-gpio"`, allowing the common pinctrl layer to coordinate pin ownership with the Tegra GPIO controller.

## Dependencies and Integration Points

It depends on the shared Tegra pinctrl structures and helpers declared in the local Tegra pinctrl headers and implemented by the common Tegra pinctrl driver. It integrates with platform-driver matching, OF compatible strings, Linux pinctrl/pinmux/pinconf consumers, GPIO ranges, and system sleep through `tegra_pinctrl_pm`. Board Device Trees select groups/functions by names generated from the static arrays.

## Risks

The main risk is table correctness. A wrong pin number, group name, function ordinal, register offset, bank, or bit field can silently program the wrong pad, break GPIO muxing, or damage electrical behavior through bad drive-strength or high-voltage settings. Several groups use `-1` for unsupported fields; the common driver must honor those sentinels. Function enum order must stay aligned with `tegra210_functions[]`, because group entries store enum constants rather than strings.

## Test Signals

Useful checks are build coverage for `CONFIG_PINCTRL_TEGRA210`, boot probing on a Tegra210 board with `nvidia,tegra210-pinmux`, pinctrl debugfs inspection of pin/group/function names, DT pin state application for SDMMC/I2C/UART/SPI/PCIe/display pins, suspend/resume checks for saved pin state, and GPIO handoff tests against `nvidia,tegra210-gpio`. Table changes should be reviewed against the Tegra210 TRM and binding examples rather than relying only on compilation.
