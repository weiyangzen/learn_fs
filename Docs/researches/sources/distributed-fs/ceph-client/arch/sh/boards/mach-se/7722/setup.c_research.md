<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c

## Purpose
SH7722 Solution Engine setup. It registers heartbeat, SMC91x, CF/IDE, and keyscan devices, resolves FPGA IRQ domain mappings for resources, and sets up board pins.

## Important APIs, Types, and Functions
- functions: se7722_devices_setup, se7722_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, irq_domain.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/ata_platform.h, linux/input.h, linux/input/sh_keysc.h, linux/irqdomain.h, linux/smc91x.h, linux/sh_intc.h, mach-se/mach/se7722.h, mach-se/mach/mrshpc.h.
- resource/data arrays: smc91x_eth_resources, cf_ide_resources, sh_keysc_resources.
- Source-tree integration: mach-se/7722; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c -->
