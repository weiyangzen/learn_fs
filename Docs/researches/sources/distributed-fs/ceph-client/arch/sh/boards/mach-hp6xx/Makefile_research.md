<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile

## Purpose
Build glue for HP6xx handheld support: setup.o always, suspend/resume files under CONFIG_PM, and the APM emulation bridge under CONFIG_APM_EMULATION.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y			:= setup.o, obj-$(CONFIG_PM)	+= pm.o pm_wakeup.o, obj-$(CONFIG_APM_EMULATION)	+= hp6xx_apm.o.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile -->
