# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Kconfig

Purpose: defines the HP submenu for x86 platform-specific drivers and the build-time feature gates for HP accelerometer, HP WMI extras, TC1100 tablet WMI extras, and HP BIOS configuration support.

Important APIs/types/functions: Kconfig symbols are `X86_PLATFORM_DRIVERS_HP`, `HP_ACCEL`, `HP_WMI`, `TC1100_WMI`, and `HP_BIOSCFG`. Their dependency/select clauses wire each driver to required kernel subsystems: ACPI, WMI, input, i8042/serio, rfkill, power supply, sparse keymap, platform profile, hwmon, firmware attributes class, and NLS.

Control flow: this file has no runtime control flow. At configuration time, enabling `X86_PLATFORM_DRIVERS_HP` reveals the submenu; individual tristate symbols decide whether object files are built-in, modular, or absent.

State and persistence: state is the generated kernel configuration. Defaults are `m` for the driver symbols when dependencies are met, making the HP support modules available without forcing built-in code.

Dependencies and integration: `HP_ACCEL` selects the LIS3LV02D sensor core plus LED classes; `HP_WMI` selects user-visible subsystems used by `hp-wmi.c`; `HP_BIOSCFG` selects firmware attribute class support for `hp-bioscfg`.

Risks and test signals: incorrect dependencies surface as build failures or missing symbols in the corresponding C files. Kconfig testing should cover `allmodconfig`, dependency-disabled configs, and modular/built-in combinations, especially `RFKILL=n`, `ACPI_WMI` absent, and non-32-bit TC1100 configurations.
