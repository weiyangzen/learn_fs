# sources/distributed-fs/ceph-client/drivers/resctrl/Makefile

## Purpose

This Makefile defines how the MPAM driver objects are built under `drivers/resctrl`. It creates a composite `mpam.o` object from the device layer and optionally the resctrl bridge.

## Important APIs, Types, And Functions

`obj-$(CONFIG_ARM64_MPAM_DRIVER) += mpam.o` builds the composite driver when the main Kconfig option is enabled. `mpam-y += mpam_devices.o` always includes the MSC/device layer. `mpam-$(CONFIG_ARM64_MPAM_RESCTRL_FS) += mpam_resctrl.o` conditionally includes the resctrl filesystem integration. `ccflags-$(CONFIG_ARM64_MPAM_DRIVER_DEBUG) += -DDEBUG` enables `pr_debug()` output for the driver.

## Control Flow

The build flow is Kbuild-controlled. Kconfig selects decide whether `mpam.o` exists, whether `mpam_resctrl.o` is linked into it, and whether debug macro behavior changes at compile time.

## State And Persistence

There is no runtime state. This file controls object composition and compile flags.

## Dependencies And Integration Points

It depends on the symbols defined by `Kconfig` in the same directory. The composite object links the public functions shared between `mpam_devices.c` and `mpam_resctrl.c` through `mpam_internal.h`.

## Risks And Edge Cases

Because `test_mpam_devices.c` is included from `mpam_devices.c` under KUnit rather than listed here, test compilation depends on C preprocessor inclusion and Kconfig rather than Makefile test objects. Debug behavior is broad for all objects compiled under this directory when the debug option is set.

## Test Signals

Build tests should verify object inclusion for `CONFIG_ARM64_MPAM_DRIVER=y`, optional `CONFIG_ARM64_MPAM_RESCTRL_FS`, and `CONFIG_ARM64_MPAM_DRIVER_DEBUG`.
