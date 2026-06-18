# sources/distributed-fs/ceph-client/drivers/hwmon/Makefile

## Purpose
`drivers/hwmon/Makefile` maps Kconfig symbols to hwmon core objects, individual sensor-driver objects, composite module object lists, subdirectories, and debug compiler flags. It is the build-system counterpart to `drivers/hwmon/Kconfig`.

## Important APIs, types, and functions
The primary interface is Kbuild syntax. `obj-$(CONFIG_HWMON) += hwmon.o` and `obj-$(CONFIG_HWMON_VID) += hwmon-vid.o` build core/helper objects. Hundreds of `obj-$(CONFIG_SENSORS_*) += <driver>.o` entries map symbols to modules or built-in objects. Composite modules include `nct6775-objs := nct6775-platform.o` followed by `obj-$(CONFIG_SENSORS_NCT6775) += nct6775.o`. Subdirectories `occ/`, `peci/`, and `pmbus/` are entered through their controlling symbols. `ccflags-$(CONFIG_HWMON_DEBUG_CHIP) := -DDEBUG` enables directory-wide debug messages.

## Control flow
During Kbuild traversal, selected `CONFIG_*` values expand the matching `obj-*` variables. Built-in selections add objects to `built-in.a`; module selections produce loadable modules using the listed object names. Ordering is mostly alphabetical by driver family but has an explicit early ordering comment: `asb100` and then `w83781d` should go first because they can override other drivers' addresses. Child directories are traversed only when their controlling symbols are enabled.

## State and persistence behavior
The Makefile does not create runtime state. Its persistent effects are build artifacts and module names. The object names determine resulting `.ko` names for modular builds, except composite modules where the left-hand module name collects objects listed in `*-objs`.

## Dependencies and integration points
This file depends on Kconfig symbols from the sibling `Kconfig` and child Kconfig files. It integrates with Kbuild, the hwmon subsystem core, and every C source file in the directory and subdirectories. Help text in Kconfig often promises module names that must match these object mappings.

## Risks
Symbol/object mismatches cause missing drivers, unexpected module names, or link failures. A driver requiring common code must have both the common helper object and frontend object selected, as with `adt7x10`, `ltc2947-core`, `nct6775-core`, and `sch56xx-common`. Ordering changes near drivers that probe overlapping addresses can alter hardware binding behavior. Global `-DDEBUG` can materially increase log volume and expose timing differences in low-level sensor probing.

## Test signals
Useful checks include comparing every `obj-$(CONFIG_...)` symbol against Kconfig definitions, verifying referenced `.c` files or subdirectories exist, running `make M=drivers/hwmon` for targeted module builds, allmodconfig/allyesconfig builds, checking composite module link contents, confirming `HWMON_DEBUG_CHIP` adds `-DDEBUG`, and validating module names mentioned in Kconfig help text.
