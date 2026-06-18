# sources/distributed-fs/ceph-client/drivers/platform/surface/Kconfig

## Purpose

This Kconfig file defines the Microsoft Surface platform-driver menu and the user-selectable options for Surface-specific WMI, ACPI, hotplug, power, input, platform-profile, DTX, and Surface Aggregator support.

## Important APIs, Types, And Functions

The top-level `menuconfig SURFACE_PLATFORMS` gates the menu on `ARM64 || X86 || COMPILE_TEST` and defaults to enabled on ARM64/X86. Configs include `SURFACE3_WMI`, `SURFACE_3_POWER_OPREGION`, `SURFACE_ACPI_NOTIFY`, `SURFACE_AGGREGATOR_CDEV`, `SURFACE_AGGREGATOR_HUB`, `SURFACE_AGGREGATOR_REGISTRY`, `SURFACE_AGGREGATOR_TABLET_SWITCH`, `SURFACE_DTX`, `SURFACE_GPE`, `SURFACE_HOTPLUG`, `SURFACE_PLATFORM_PROFILE`, and `SURFACE_PRO3_BUTTON`. It sources `drivers/platform/surface/aggregator/Kconfig` for the SSAM core.

## Control Flow

There is no runtime control flow. Build-time selection controls which object files in the Surface Makefile and aggregator subdirectory are compiled. Dependency declarations force required subsystems such as ACPI, WMI, DMI, SPI, INPUT, GPIOLIB, and Surface Aggregator support.

## State And Persistence

The only state is Kconfig build configuration. It persists in `.config` and determines available modules or built-in drivers.

## Dependencies And Integration Points

The file integrates the Surface platform subtree with kernel Kconfig, the Surface Aggregator Kconfig, ACPI/WMI/input/GPIO/SPI support, and ACPI platform profile support. Several drivers depend on `SURFACE_AGGREGATOR` or `SURFACE_AGGREGATOR_BUS`.

## Risks

Incorrect dependencies can allow invalid builds or hide needed drivers. `SURFACE_DTX` can be built without the aggregator bus, but help text warns that some devices will then be unsupported. Options that instantiate client devices require both registry/hub providers and actual client drivers, so users can select incomplete combinations.

## Test Signals

Validation is mostly configuration-matrix testing: `allyesconfig`, `allmodconfig`, targeted Surface configs, `COMPILE_TEST`, and module-name checks. Runtime signals are successful probing of selected Surface devices and absence of unresolved symbols when options are built as modules.
