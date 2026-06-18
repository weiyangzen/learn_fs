<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c

## Purpose
Provides the Tegra114-specific pin, function, group, drive-group, and platform-driver descriptors consumed by the shared Tegra pinctrl core.

## Important APIs, Types, And Functions
The file defines Tegra114 GPIO-numbered pins, non-GPIO pins, `tegra114_pins`, one-pin group arrays, multi-pin drive groups, `enum tegra_mux`, `tegra114_functions`, `PINGROUP` and `DRV_PINGROUP` descriptor macros, `tegra114_groups`, and `tegra114_pinctrl`. Runtime registration is through `tegra114_pinctrl_probe`, `tegra114_pinctrl_driver`, and `arch_initcall(tegra114_pinctrl_init)`.

## Control Flow
At arch init, the platform driver registers for compatible `nvidia,tegra114-pinmux`. Probe delegates to `tegra_pinctrl_probe`, which uses this file's static tables to register pins, groups, functions, and GPIO ranges. Each `PINGROUP` maps one logical pin group to a mux register in bank 1 and records pull, tristate, input, open-drain, lock, IO reset, and receiver-select bits. Each `DRV_PINGROUP` maps a drive group to bank 0 drive-strength/slew/schmitt/high-speed fields.

## State And Persistence Behavior
The file is static descriptor data only. Persistent runtime state is created by the common driver from these tables. Hardware state affected by the descriptors includes Tegra114 mux registers based at `0x3000` and drive registers based at `0x868`.

## Dependencies And Integration Points
Depends on `pinctrl-tegra.h`, Linux platform/OF matching, and a Tegra114 GPIO controller compatible string `nvidia,tegra114-gpio`. It integrates with DT pinctrl properties whose group and function names must match the static table names.

## Risks And Edge Cases
This file is table-heavy and correctness depends on exact GPIO numbering, register offsets, mux-slot ordering, and feature bits. Empty drive pin arrays still define configurable groups. Function enum ordering must match `tegra114_functions` and every `TEGRA_MUX_*` value used in group macros. A wrong compatible string or GPIO count breaks pinctrl/GPIO integration.

## Test Signals
Boot/probe on Tegra114 DT, pinctrl state application for UART/I2C/SDMMC/GMI/display groups, drive strength and slew config on drive groups, GPIO range mapping, debugfs group function dumps, and suspend/resume through the common Tegra PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra114.c -->
