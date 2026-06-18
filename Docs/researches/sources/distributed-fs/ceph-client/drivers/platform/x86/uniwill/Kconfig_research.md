# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Kconfig

Purpose: Kconfig menu for Uniwill-derived laptop platform support. `X86_PLATFORM_DRIVERS_UNIWILL` opens the submenu and `UNIWILL_LAPTOP` builds the extras driver.

Important APIs and control flow: `UNIWILL_LAPTOP` is tristate, defaults to module, depends on ACPI, WMI, ACPI battery, hwmon, input, multicolor LED, and DMI support, and selects `REGMAP` plus `INPUT_SPARSEKMAP`.

State and dependencies: configuration state decides whether the composite `uniwill-laptop` driver builds. The dependency list mirrors runtime subsystems used by `uniwill-acpi.c` and `uniwill-wmi.c`.

Risks and test signals: missing dependencies surface as compile or link failures in hwmon, LED, input, battery hook, or WMI paths. Test by compiling `UNIWILL_LAPTOP=m` and `=y` in representative x86 configs.
