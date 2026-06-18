<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile

## Purpose
Build glue for Highlander board support. setup.o is always included for the machine; variant-specific IRQ files and R7785RP pinmux support are selected by board Kconfig, and psw.o is included for push switches on non-R7785RP builds.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y				:= setup.o, obj-$(CONFIG_SH_R7780RP)	+= irq-r7780rp.o, obj-$(CONFIG_SH_R7780MP)	+= irq-r7780mp.o, obj-$(CONFIG_SH_R7785RP)	+= irq-r7785rp.o pinmux-r7785rp.o, obj-$(CONFIG_PUSH_SWITCH)	+= psw.o.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile -->
