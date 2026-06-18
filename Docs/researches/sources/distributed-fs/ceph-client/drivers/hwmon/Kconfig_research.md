# sources/distributed-fs/ceph-client/drivers/hwmon/Kconfig

## Purpose
`drivers/hwmon/Kconfig` defines the configuration menu for the Linux hardware monitoring subsystem and its large set of sensor drivers. It controls whether the core hwmon subsystem is built, whether helper/debug options are available, and which individual temperature, voltage, current, power, fan, humidity, and platform-specific drivers can be compiled in or as modules.

## Important APIs, types, and functions
This is Kconfig, so its main APIs are symbols and dependency relationships rather than C functions. The top-level `menuconfig HWMON` is a tristate gated by `HAS_IOMEM` and defaults to `y`. Within `if HWMON`, helper symbols include `HWMON_VID` and `HWMON_DEBUG_CHIP`. The file then defines many `SENSORS_*` tristate/bool symbols, helper/common symbols such as `SENSORS_ADT7X10`, `SENSORS_LTC2947`, `SENSORS_NCT6775_CORE`, `SENSORS_SCH56XX_COMMON`, and feature suboptions such as `I8K`, `SENSORS_W83795_FANCTRL`, and `SENSORS_SPD5118_DETECT`.

## Control flow
Kconfig evaluation starts with `HWMON`; if disabled, all nested hwmon driver choices are hidden. Native drivers are listed first, then child Kconfig files are included with `source "drivers/hwmon/occ/Kconfig"`, `source "drivers/hwmon/peci/Kconfig"`, and `source "drivers/hwmon/pmbus/Kconfig"`. At the end, an `if ACPI` block exposes ACPI-backed hwmon drivers. Each symbol uses `depends on` to constrain visibility/buildability, `select` to force lower-level helpers, and occasional `imply`/`default` rules for optional integration.

## State and persistence behavior
The persistent output is the kernel configuration. Selected symbols flow into generated config headers and drive object inclusion in `drivers/hwmon/Makefile`. Tristate values determine built-in versus module builds, and helper symbols can be selected by multiple drivers. No runtime state is created directly by this file, but incorrect dependencies produce persistent build combinations that can expose compile, link, or runtime probe failures.

## Dependencies and integration points
The file integrates with architecture/platform symbols, buses such as I2C/SPI/USB/HID/PCI/ACPI/OF/I3C, subsystems such as MFD, IPMI, WATCHDOG, THERMAL, IIO, PWM, REGMAP, and GPIOLIB, and documentation references under `Documentation/hwmon/`. Its symbol names must stay aligned with Makefile `obj-$(CONFIG_...)` entries and driver source expectations.

## Risks
The main risks are dependency drift and invalid symbol-to-object mappings. `select` can force dependencies without their own prerequisites, so helper selections must be used carefully. Some drivers use hardware-specific port I/O or platform firmware and depend on guards such as `HAS_IOPORT`, `DMI`, `ACPI_WMI`, or `COMPILE_TEST`. Hidden helper symbols must remain selected by all frontend drivers that require their common code. Included child Kconfig files must match child directory Makefile entries.

## Test signals
Validation should include `make olddefconfig`, `allmodconfig`, `allyesconfig`, targeted `CONFIG_HWMON=m/y` builds, `COMPILE_TEST` builds across non-native architectures, module name checks against help text and Makefile objects, dependency linting if available, and spot builds for helper split drivers such as ADT7x10, LTC2947, NCT6775, SCH56xx, PMBus, PECI, and OCC.
