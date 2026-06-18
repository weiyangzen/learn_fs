# sources/distributed-fs/ceph-client/drivers/power/supply/Kconfig

Purpose: this Kconfig file defines the Linux power supply class menu and the selectable battery, charger, fuel-gauge, and power-source drivers under `drivers/power/supply`. It gates compilation, dependency visibility, and helper selection for all drivers in this subsystem.

Important APIs, types, and functions: the file is declarative Kconfig rather than C. The top-level `menuconfig POWER_SUPPLY` enables the class. `POWER_SUPPLY_DEBUG` adds debug compilation, `POWER_SUPPLY_HWMON` exposes sensors as hwmon, and `ADC_BATTERY_HELPER` is a silent helper. Relevant symbols for this subset include `BATTERY_88PM860X`, `CHARGER_88PM860X`, and `AB8500_BM`. `BATTERY_88PM860X` depends on `MFD_88PM860X`; `CHARGER_88PM860X` depends on both `MFD_88PM860X` and `BATTERY_88PM860X`; `AB8500_BM` is bool and depends on `AB8500_CORE`, `AB8500_GPADC`, built-in `IIO`, and `OF`, and selects `THERMAL` plus `THERMAL_OF`.

Control flow: Kconfig evaluation controls which Makefile object rules become active. Many entries are tristate modules, while some platform data or shared data options are bool. Dependencies constrain menu visibility and prevent impossible link combinations, such as the 88PM860x charger without the matching battery monitor. `select` is used for helper subsystems like `REGMAP_I2C`, `AUXILIARY_BUS`, `THERMAL`, and `THERMAL_OF` when a driver requires them.

State and persistence: there is no runtime state. Configuration state persists in kernel `.config`, generated headers, and module build decisions. Because `AB8500_BM` is bool, its five-object battery-management group is built into the kernel rather than as separate modules when selected.

Dependencies and integration points: this file integrates with `drivers/power/supply/Makefile`, generated `include/generated/autoconf.h`, Kbuild, and subsystem menus for MFD, IIO, OF, ACPI, USB, extcon, thermal, hwmon, and regmap. It documents expected module names in help text for many drivers.

Risks: dependency drift here can produce link failures or runtime probe failures if a driver uses a subsystem not expressed in Kconfig. `select` can force subsystems on without their own dependencies being met if used carelessly; the AB8500 entry handles this partly by requiring `IIO = y`. The large single menu increases merge-conflict risk and makes alphabetical or subsystem grouping mistakes easy. Help text typos do not affect builds but can mislead users about module names or hardware support.

Test signals: run Kconfig dependency checks through representative configs: minimal `POWER_SUPPLY=n`, 88PM860x battery only, 88PM860x battery plus charger, and AB8500 built-in with OF/IIO/thermal. Build tests should confirm enabled symbols produce the objects named in Makefile and disabled symbols leave no unresolved references.
