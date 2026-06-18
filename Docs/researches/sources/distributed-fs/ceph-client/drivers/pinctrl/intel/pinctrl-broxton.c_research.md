# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-broxton.c

## Purpose
Provides Broxton and Apollo Lake SoC pinctrl/GPIO descriptor data for the shared Intel pinctrl core. It describes multiple ACPI UID-selected communities such as north, northwest, west, southwest, and south banks, including alternate function groups for UART, PWM, I2C, SPI/SSP, eMMC, SDIO, and SD card pins.

## Important APIs, Types, and Functions
The `BXT_*` register offset macros define community register layout. `BXT_COMMUNITY()` uses `INTEL_COMMUNITY_SIZE()` with 32-pin groups and four pad config DWs. Static data includes BXT and APL pin arrays, `intel_pingroup` arrays with modes, `intel_function` arrays, per-bank communities, and `intel_pinctrl_soc_data` arrays for Broxton and Apollo Lake. ACPI IDs `INT3452` and `INT34D1` and platform IDs select the SoC-data list. Probe uses `intel_pinctrl_probe_by_uid`.

## Control Flow
The subsys initcall registers `broxton-pinctrl`. Firmware may enumerate several platform devices with different UIDs; the shared Intel probe selects the matching entry from the data array, maps community resources, and registers pinctrl/GPIO/IRQ support. Function selection and GPIO behavior are then handled by `pinctrl-intel.c` using the group/mode tables.

## State and Persistence Behavior
This file is static descriptor data. Runtime state is in the common Intel driver and hardware registers. The `.uid` fields persist as the selector that binds each ACPI instance to one bank’s pin map.

## Dependencies and Integration Points
Depends on ACPI/platform IDs, `pinctrl-intel.h`, the generic pinctrl framework, and Intel shared PM ops. It integrates with LPSS/I2C/UART/PWM/storage peripherals whose ACPI pin states refer to these groups and with GPIO consumers on Broxton/Apollo Lake boards.

## Risks
UID-to-bank mapping is critical; a wrong UID gives a device the wrong pin table. Group mode arrays must align one-to-one with their pin arrays. Community pin ranges and GPIO bases affect IRQ and GPIO numbering. Broxton and Apollo Lake share driver code but have different banks, so accidental cross-use is a high-risk edit.

## Test Signals
Probe for `INT34D1` and `INT3452`, one gpiochip per expected ACPI UID, pinmux selection for UART/I2C/PWM/storage groups, GPIO numbering across communities, IRQ delivery, suspend/resume via shared PM ops, and build/module init under `PINCTRL_BROXTON` validate this file.
