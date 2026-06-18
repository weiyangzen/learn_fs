<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile

## Purpose
Build glue for SDK7786. FPGA, IRQ, NMI, and setup are always included; GPIO and SRAM support are conditional on GPIOLIB and HAVE_SRAM_POOL.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	:= fpga.o irq.o nmi.o setup.o, obj-$(CONFIG_GPIOLIB)		+= gpio.o, obj-$(CONFIG_HAVE_SRAM_POOL)	+= sram.o.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile -->
