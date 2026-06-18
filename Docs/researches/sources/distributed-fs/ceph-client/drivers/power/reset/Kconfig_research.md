# sources/distributed-fs/ceph-client/drivers/power/reset/Kconfig

## Purpose
`drivers/power/reset/Kconfig` defines the board-level reset, restart, poweroff, reboot-mode, and related embedded-controller driver configuration symbols. The menu is gated by `POWER_RESET` and covers platform-specific PMIC, syscon, GPIO, firmware, PCI, I2C, and generic reboot-mode drivers.

## Important APIs, Types, and Functions
Important symbols include `POWER_RESET`, per-driver selectors such as `POWER_RESET_GPIO`, `POWER_RESET_SYSCON`, `POWER_RESET_AT91_RESET`, `POWER_RESET_QCOM_PON`, `POWER_RESET_TORADEX_EC`, `POWER_RESET_QEMU_VIRT_CTRL`, framework symbol `REBOOT_MODE`, and storage backends `SYSCON_REBOOT_MODE` and `NVMEM_REBOOT_MODE`. Dependencies encode architecture, MFD, OF, regmap, I2C, PCI, regulator, and compile-test constraints.

## Control Flow
Kconfig exposes the parent menu, then conditionally offers each driver while applying `depends on`, `default`, and `select` rules. Enabling a driver later maps to an object in `drivers/power/reset/Makefile`. Some options are bool because they are intended built-in restart handlers, while others are tristate modules.

## State and Persistence Behavior
Configuration choices persist in `.config`. There is no runtime behavior, but selecting symbols controls whether shutdown/restart handlers and reboot-mode providers exist in a kernel image.

## Dependencies and Integration Points
It integrates with architecture symbols, MFD/regmap/provider subsystems, OF, ACPI/I2C/PCI, and the reset directory Makefile. `select REBOOT_MODE` couples qcom/syscon/nvmem reboot-mode consumers to the generic reboot-mode core.

## Risks and Edge Cases
Incorrect dependencies can create link failures or hide valid hardware support. Bool restart handlers may need to be built-in for early/critical reset paths. `select` can force framework code without all optional runtime dependencies, so dependency minimalism matters.

## Test Signals
Run Kconfig dependency checks, allmodconfig/allyesconfig across ARM, ARM64, MIPS, x86 compile-test, and targeted configs for AT91, Qualcomm, Broadcom, Renesas, Toradex, QEMU virt, and generic syscon/nvmem reboot modes.
