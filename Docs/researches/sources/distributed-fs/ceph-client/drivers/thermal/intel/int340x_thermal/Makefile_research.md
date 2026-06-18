# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/Makefile

## Purpose
Kbuild map for ACPI INT340x thermal drivers and related processor thermal components.

## Important APIs, Types, and Functions
No runtime APIs. `INT340X_THERMAL` builds `int3400_thermal.o`, `int340x_thermal_zone.o`, `int3402_thermal.o`, `int3403_thermal.o`, `processor_thermal_device.o`, `int3401_thermal.o`, PCI processor thermal variants, RFIM/mailbox/workload/power-floor/SOC-slider components, and platform temperature control. Optional symbols build `processor_thermal_rapl.o`, `int3406_thermal.o`, and `acpi_thermal_rel.o`.

## Control Flow
Kbuild expands all `obj-$(CONFIG_...)` lines based on selected INT340x symbols. Many implementation files are compiled together under the single main symbol.

## State and Persistence
No runtime state. Build artifacts persist in the build directory.

## Dependencies and Integration Points
Must align with int340x Kconfig and all listed source files. It wires the ACPI relationship helper into the same subdirectory build.

## Risks and Edge Cases
The broad object list under `INT340X_THERMAL` means build failures in one component affect the whole feature. Renames or symbol splits need careful Makefile updates.

## Test Signals
Build tests should cover `INT340X_THERMAL` alone, with `PROC_THERMAL_MMIO_RAPL`, with `INT3406_THERMAL`, and with `ACPI_THERMAL_REL` selected indirectly.
