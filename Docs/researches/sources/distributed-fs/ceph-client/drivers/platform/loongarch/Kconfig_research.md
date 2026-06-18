<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig

## Purpose

This Kconfig file defines LoongArch platform-specific device-driver options, currently including the generic Loongson laptop/all-in-one ACPI driver.

## Important APIs, Types, And Functions

`LOONGARCH_PLATFORM_DEVICES` gates the menu and defaults to yes on LoongArch. `LOONGSON_LAPTOP` is a tristate depending on `ACPI_EC`, `BACKLIGHT_CLASS_DEVICE`, `INPUT`, and `MACH_LOONGSON64`; it selects `ACPI_VIDEO` and `INPUT_SPARSEKMAP`.

## Control Flow

When enabled, the Loongson laptop driver is built and can register ACPI hotkey, input, and backlight support.

## State And Persistence

The file has no runtime state. It determines whether the Loongson ACPI driver is available.

## Dependencies And Integration Points

It integrates LoongArch platform support with ACPI EC, input sparse keymap, ACPI video, and backlight subsystems.

## Risks

The option defaults to enabled for the platform, so compile/runtime issues affect default Loongson laptop kernels. Dependency selection must avoid exposing the driver without ACPI EC or input support.

## Test Signals

Check Kconfig visibility on LoongArch, dependency pruning, default selection, and module/built-in builds for `LOONGSON_LAPTOP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig -->
