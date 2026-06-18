<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/Makefile

## Purpose

`drivers/thermal/Makefile` maps thermal subsystem Kconfig symbols to core, governor, cooling, platform, and testing object files. It is the Kbuild assembly point for the thermal framework and platform thermal drivers.

## Important APIs, Types, and Functions

The main `thermal_sys.o` composite is built when `CONFIG_THERMAL` is enabled and includes core files such as `thermal_core.o`, `thermal_sysfs.o`, `thermal_trip.o`, `thermal_helpers.o`, and `thermal_thresholds.o`. Conditional additions include netlink, debugfs, hwmon, OF, governors, CPU cooling, devfreq cooling, and PCIe cooling. Platform entries include `obj-$(CONFIG_AIROHA_THERMAL) += airoha_thermal.o` and `obj-$(CONFIG_AMLOGIC_THERMAL) += amlogic_thermal.o`, along with many other vendors and subdirectories.

## Control Flow

Kbuild expands each `obj-$(CONFIG_...)` and `thermal_sys-$(CONFIG_...)` according to the resolved configuration. Core and selected optional pieces are linked into `thermal_sys.o`; platform drivers become separate built-in or module objects depending on their symbols. Include flags are set for thermal core and power allocator governor sources.

## State and Persistence Behavior

The Makefile has no runtime state. It determines which object code is present in the kernel or modules.

## Dependencies and Integration Points

It integrates with `drivers/thermal/Kconfig`, Linux Kbuild, platform subdirectories, and optional subsystem configs. The Airoha and Amlogic driver source files in this work item are selected here.

## Risks and Edge Cases

Spacing is mostly conventional but mixed in a few entries, which is harmless to make. Unconditional `obj-y` subdirectories rely on their own Kconfig/Makefile guards. Missing entries here would make a Kconfig option ineffective; stale entries would cause build failures when source files are moved or renamed.

## Test Signals

Build tests should verify `thermal_sys.o` composition for major option combinations, module vs built-in output for platform drivers, inclusion of `airoha_thermal.o` and `amlogic_thermal.o` under their symbols, and absence of unresolved objects when optional submenus are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Makefile -->
