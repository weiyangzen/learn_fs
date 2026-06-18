<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c

## Purpose
SH7721 Solution Engine setup. It registers heartbeat and CF/IDE platform devices and supplies setup plus init_irq callbacks in the machine vector.

## Important APIs, Types, and Functions
- functions: se7721_devices_setup, se7721_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, mach-se/mach/se7721.h, mach-se/mach/mrshpc.h, asm/machvec.h, asm/io.h, asm/heartbeat.h.
- resource/data arrays: heartbeat_bit_pos, cf_ide_resources.
- Source-tree integration: mach-se/7721; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c -->
