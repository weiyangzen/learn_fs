# sources/distributed-fs/ceph-client/drivers/platform/x86/Kconfig

Purpose: Defines the top-level x86 platform-device driver menu and a large set of vendor/platform driver build options, including the Acer drivers in this work item.

Important APIs and types: `menuconfig X86_PLATFORM_DEVICES` gates the submenu on `X86`. Local entries include `ACER_WIRELESS` and `ACER_WMI`; many vendor submenus are sourced for AMD, Dell, HP, Intel, Lenovo, Siemens, Tuxedo, Uniwill, and Android tablets. Several options select helper frameworks such as `INPUT_SPARSEKMAP`, `LEDS_CLASS`, `ACPI_PLATFORM_PROFILE`, `FW_ATTR_CLASS`, or hwmon/backlight/rfkill dependencies.

Control flow: Kconfig dependencies decide which platform drivers can be built. `ACER_WIRELESS` depends on ACPI and INPUT; `ACER_WMI` depends on backlight, i8042, input, optional rfkill/video, ACPI EC/WMI, and hwmon, and selects sparse keymap, LED class, and platform profile support.

State and persistence: No runtime state. Kernel `.config` selections persist build decisions and module availability.

Dependencies and integration points: Closely coupled to `drivers/platform/x86/Makefile` object entries and subsystem Kconfig symbols for ACPI, WMI, backlight, input, rfkill, hwmon, watchdog, GPIO, PCI, and vendor subdirectories.

Risks: This file is broad and dependency-sensitive; wrong dependencies can create link failures or expose drivers without required subsystems. `ACER_WMI` has many hard dependencies because the single driver can expose rfkill, backlight, LED, input, hwmon, and platform-profile features.

Test signals: Kconfig visibility for Acer and other platform drivers; allmodconfig/build coverage; dependency checks when toggling ACPI_WMI, RFKILL, ACPI_VIDEO, HWMON, and X86; generated modules matching Makefile object names.
