# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/Makefile

## Purpose
The Makefile composes the `ti-soc-thermal` object from the shared bandgap driver, optional thermal framework bridge, and selected per-SoC data tables.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TI_SOC_THERMAL)` builds `ti-soc-thermal.o`. Component objects are `ti-bandgap.o`, optional `ti-thermal-common.o`, and per-family data objects for DRA752, OMAP3, OMAP4, and OMAP5.

## Control Flow
Build-system control flow is entirely Kconfig driven. The runtime OF match table in `ti-bandgap.c` references only data symbols whose configs are enabled.

## State and Persistence Behavior
No runtime state is owned by the Makefile. The built module or built-in object persists according to kernel build configuration.

## Dependencies and Integration Points
It is tightly coupled to `Kconfig` and conditional extern macros in `ti-bandgap.h`.

## Risks and Edge Cases
Missing an object for an enabled compatible would fail link or probe. Enabling `TI_SOC_THERMAL` without `TI_THERMAL` builds hardware support without thermal-zone exposure callbacks.

## Test Signals
Build matrix across `TI_THERMAL` and each family symbol; verify link coverage for all OF match data references.
