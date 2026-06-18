<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c

## Purpose
Provides Tegra124-specific pinctrl descriptor data and platform-driver registration for the common Tegra pinctrl core. It extends the Tegra114-style model with Tegra124 pin names, additional GPIOs, PCIe/DP/DSI-related pins, updated mux functions, drive groups, and a MIPI pad control group.

## Important APIs, Types, And Functions
The file defines GPIO/non-GPIO pin IDs, `tegra124_pins`, one-pin group arrays, drive-group arrays, `mipi_pad_ctrl_dsi_b_pins`, `enum tegra_mux`, `tegra124_functions`, descriptor macros `PINGROUP`, `DRV_PINGROUP`, and `MIPI_PAD_CTRL_PINGROUP`, `tegra124_groups`, and `tegra124_pinctrl`. Runtime registration is via `tegra124_pinctrl_probe`, OF match `nvidia,tegra124-pinmux`, and `arch_initcall(tegra124_pinctrl_init)`.

## Control Flow
At arch init the platform driver registers and later delegates matching devices to `tegra_pinctrl_probe`. The common driver consumes this file's tables to enumerate groups/functions, parse DT pinctrl states, and program mux/pinconf registers. Standard pingroups live in bank 1 relative to `0x3000`, drive groups live in bank 0 relative to `0x868`, and the DSI-B MIPI pad control group lives in bank 2 relative to `0x820`.

## State And Persistence Behavior
This file contributes static read-only hardware layout data. Runtime state and suspend backup are owned by `pinctrl-tegra.c`. Hardware configuration persists in the mux, pull, tristate, drive, and MIPI pad control registers described by the tables.

## Dependencies And Integration Points
Depends on the shared Tegra header/core, platform driver/OF infrastructure, the Tegra124 GPIO compatible `nvidia,tegra124-gpio`, and DT pinctrl group/function names. It also aligns with the separate Tegra124 XUSB padctl driver for related USB/PCIe/SATA pad functions, though that driver owns XUSB lane PHY control.

## Risks And Edge Cases
The large declarative tables are prone to off-by-one GPIO IDs, wrong function-slot ordering, bad register offsets, and mismatched group names. Tegra124 adds a third MMIO bank for MIPI pad control, so platform resources must match the bank indices used here. Some drive groups have unsupported fields encoded as `-1`, which common pinconf must reject cleanly.

## Test Signals
Tegra124 boot/probe, DT states for SDMMC, UART, I2C, display, PCIe, SATA, DP, and DSI-B groups, MIPI pad muxing, drive-group pinconf, GPIO range mapping through `nvidia,tegra124-gpio`, debugfs dumps, and suspend/resume across all three register banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra124.c -->
