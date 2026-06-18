# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lewisburg.c

## Purpose

`pinctrl-lewisburg.c` describes Intel Lewisburg GPIO/pinctrl hardware for the common Intel core. It covers 247 pins across server PCH groups including LPC/eSPI, SATA, SMBus, GBE, fan, GSX, and platform-management signals.

## Important APIs, Types, And Functions

`LBG_COMMUNITY()` uses `INTEL_COMMUNITY_SIZE()` rather than explicit GPP tables, so the core generates pad groups with size 24 and three PAD_OWN registers per group. `lbg_soc_data` is matched by ACPI HID `INT3536` and consumed by `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers through `module_platform_driver()`. During probe, the shared core maps communities with BAR numbers 0, 1, 3, 4, and 5, then calls `intel_pinctrl_add_padgroups_by_size()` for each because `.gpps` is NULL. GPIO and IRQ handling proceed through generated groups.

## State And Persistence

This file is static data only. Runtime state and suspend/resume persistence are in the common core. Generated pad groups make GPIO bases match pin bases for each 24-pin group unless the final group is smaller.

## Dependencies And Integration Points

The driver depends on ACPI `INT3536`, Intel common pinctrl APIs, and PM. Lewisburg's server-focused pins integrate with LPC/eSPI, SATA/SSATA, SMBus, GBE, fan PWM/tach, reset/error, and clock request hardware.

## Risks

Using fixed-size generated groups requires the hardware's status, enable, lock, host ownership, and PAD_OWN register packing to match 24-pin groups. Any deviation would break GPIO lookup or IRQ dispatch. Sparse BAR numbering means resource ordering in firmware/platform data must match community `.barno`.

## Test Signals

Probe should map five communities and register GPIO lines through generated 24-pin groups. Tests should cover GPIO and IRQ operation near 24-pin boundaries, especially community transitions and final partial groups. Debugfs should expose pin names and generated GPIO ranges consistent with the table.
