# sources/distributed-fs/ceph-client/drivers/acpi/acpi_apd.c

## Purpose
`acpi_apd.c` creates platform devices for selected ACPI-described AMD, Hygon, and ARM64 SoC peripherals that need platform-device representation, fixed input clocks, or built-in device properties.

## Important APIs, Types, And Functions
The main descriptors are `struct apd_device_desc` and `struct apd_private_data`. Setup functions include `acpi_apd_setup()` for fixed-rate clocks and `fch_misc_setup()` for AMD FCH clock data. `acpi_apd_create_device()` is the scan-handler attach callback. The ACPI ID table maps HIDs such as `AMD0010`, `AMD0020`, `AMDI0010`, `AMDI0015`, `HYGO0010`, `APMC0D0F`, `BRCM900D`, `CAV900D`, `HISI02A*`, and `NXP0001` to descriptors.

## Control Flow
`acpi_apd_init()` registers an ACPI scan handler. When a matching ACPI node is scanned, `acpi_apd_create_device()` either directly calls `acpi_create_platform_device()` for descriptor-less devices or allocates private data, runs the descriptor setup hook, stores it in `adev->driver_data`, and creates a platform device with optional properties. Fixed-clock setup registers a clock named after the ACPI device. FCH setup parses memory resources, obtains an optional `clk-name` device property, maps the MMIO resource, and registers a `clk-fch` platform device.

## State And Persistence
State is in the created platform devices, optional fixed clocks, `clk-fch` child device data, and `adev->driver_data`. There is no explicit detach cleanup in this file, so lifetime follows ACPI scan/platform-device lifetime and devm-managed allocations where used.

## Dependencies And Integration Points
It depends on ACPI scan handlers, platform device creation in `acpi_platform.c`, Linux clock APIs, ACPI property/resource helpers, and architecture config symbols `CONFIG_X86_AMD_PLATFORM_DEVICE` and `CONFIG_ARM64`. UART descriptors provide properties consumed by serial drivers.

## Risks
Clock registration failures are not checked in `acpi_apd_setup()`, so a bad fixed clock can propagate as a later driver issue. Non-devm `pdata` allocated by `kzalloc_obj()` needs matching lifetime assumptions. FCH setup maps the first memory resource and returns errors for missing resources or allocation failures. Adding IDs must use correct fixed clock rates and properties or downstream platform drivers can misconfigure hardware.

## Test Signals
Builds should cover x86 AMD and ARM64 configurations. Runtime tests should verify platform-device creation for each HID, fixed-clock registration, UART property propagation, FCH `clk-fch` registration, and failure paths for missing `_CRS` resources.
