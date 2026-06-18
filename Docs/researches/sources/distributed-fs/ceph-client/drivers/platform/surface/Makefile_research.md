# sources/distributed-fs/ceph-client/drivers/platform/surface/Makefile

## Purpose

This Makefile maps Surface platform Kconfig symbols to the object files and subdirectories built under `drivers/platform/surface`.

## Important APIs, Types, And Functions

The key entries bind `CONFIG_SURFACE3_WMI` to `surface3-wmi.o`, `SURFACE_3_POWER_OPREGION` to `surface3_power.o`, `SURFACE_ACPI_NOTIFY` to `surface_acpi_notify.o`, `SURFACE_AGGREGATOR` to the `aggregator/` directory, `SURFACE_AGGREGATOR_CDEV` to `surface_aggregator_cdev.o`, `SURFACE_AGGREGATOR_HUB` to `surface_aggregator_hub.o`, `SURFACE_AGGREGATOR_REGISTRY` to `surface_aggregator_registry.o`, `SURFACE_AGGREGATOR_TABLET_SWITCH` to `surface_aggregator_tabletsw.o`, and the remaining Surface drivers to their corresponding objects.

## Control Flow

There is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` assignments and compiles built-in or module objects according to the current kernel configuration.

## State And Persistence

The file has no runtime state. Its effects persist only in build artifacts and module layout for a configured kernel build.

## Dependencies And Integration Points

It integrates with Kbuild and the Kconfig symbols defined in the neighboring `Kconfig` and aggregator Kconfig. The `aggregator/` subdirectory is included only when `CONFIG_SURFACE_AGGREGATOR` is enabled.

## Risks

The Makefile must stay aligned with Kconfig symbol names and source filenames. A mismatch causes selected options to silently build nothing or fail the build. Since multiple client drivers depend on the aggregator core, missing the `aggregator/` descent would break a large portion of Surface support.

## Test Signals

`make M=drivers/platform/surface`, `allmodconfig`, `allyesconfig`, and module packaging checks should confirm each selected config emits the expected object or module.
