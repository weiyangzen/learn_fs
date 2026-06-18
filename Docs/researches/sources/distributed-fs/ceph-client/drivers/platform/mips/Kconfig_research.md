# sources/distributed-fs/ceph-client/drivers/platform/mips/Kconfig

## Purpose
Kconfig menu for MIPS platform-specific device drivers. It gates Loongson-related platform support under `MIPS_PLATFORM_DEVICES`, allowing individual CPU hardware monitor, RS780E ACPI controller, and LS2K reset-controller options.

## Important APIs, Types, And Symbols
`menuconfig MIPS_PLATFORM_DEVICES` defaults to `y`, depends on `MIPS`, and controls visibility of the submenu. `CPU_HWMON` depends on `MACH_LOONGSON64`, selects `HWMON`, and defaults to `y`. `RS780E_ACPI` and `LS2K_RESET` depend on `MACH_LOONGSON64 || COMPILE_TEST`.

## Control Flow
There is no runtime control flow. Build-time selection flows from the top-level menu to per-driver config symbols, which then drive objects in the local Makefile.

## State, Dependencies, Integration, Risks, Tests
State is kernel configuration state only. Dependencies connect MIPS/Loongson platform symbols to hwmon, ACPI, and reset-controller source files. Integration is with Kbuild, menuconfig, and compile-test coverage. Risks are overly broad default enabling for `CPU_HWMON`, missing `COMPILE_TEST` for CPU_HWMON, and hidden driver options when `MIPS_PLATFORM_DEVICES` is disabled. Test signals include `olddefconfig`, menu visibility under MIPS and non-MIPS, compile testing RS780E/LS2K, and object inclusion matching the Makefile.
