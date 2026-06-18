# sources/distributed-fs/ceph-client/drivers/resctrl/Kconfig

## Purpose

This Kconfig fragment defines build-time configuration for the Arm MPAM driver and its optional resctrl filesystem bridge. It gates the MPAM MSC discovery/control code, debug logging, KUnit tests, and automatic resctrl integration.

## Important APIs, Types, And Functions

`menuconfig ARM64_MPAM_DRIVER` enables the MPAM driver on `ARM64 && ARM64_MPAM` and selects `ACPI_MPAM` when ACPI is enabled. `ARM64_MPAM_DRIVER_DEBUG` adds debug messages. `MPAM_KUNIT_TEST` enables MPAM KUnit tests when KUnit is built in, defaulting to `KUNIT_ALL_TESTS`. `ARM64_MPAM_RESCTRL_FS` is a hidden bool defaulting to yes when both `ARM64_MPAM_DRIVER` and `RESCTRL_FS` are enabled; it selects `RESCTRL_RMID_DEPENDS_ON_CLOSID` and `RESCTRL_ASSIGN_FIXED`.

## Control Flow

The configuration flow is compile-time only. Enabling the main driver opens the nested debug and test options. If resctrl is present, the hidden bridge option automatically includes `mpam_resctrl.o` through the Makefile.

## State And Persistence

There is no runtime state in this file. It determines which objects, debug flags, and resctrl capabilities are compiled into the kernel.

## Dependencies And Integration Points

The fragment integrates Arm64 architectural MPAM support, ACPI MPAM discovery, Linux resctrl, and KUnit. The selected resctrl flags are important because MPAM RMID identity depends on both CLOSID/PARTID and PMG, and because monitor assignment is fixed rather than dynamically assigned like some x86 features.

## Risks And Edge Cases

`ARM64_MPAM_RESCTRL_FS` is hidden and automatic, so enabling `RESCTRL_FS` with MPAM compiles the bridge even if a platform has limited MPAM features. `MPAM_KUNIT_TEST` requires `KUNIT=y`, not module KUnit. Debug logging is compile-time through `-DDEBUG`.

## Test Signals

Build matrix signals are main driver on/off, ACPI on/off selection, debug flag compilation, KUnit inclusion, and resctrl bridge inclusion only when both MPAM driver and resctrl are enabled.
