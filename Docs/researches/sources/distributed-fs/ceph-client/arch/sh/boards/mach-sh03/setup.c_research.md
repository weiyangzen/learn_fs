<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c

## Purpose
SH03 setup. It initializes board IRQs, registers CF/IDE and heartbeat platform devices, and integrates the board RTC/machine resources.

## Important APIs, Types, and Functions
- functions: init_sh03_IRQ, sh03_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/pci.h, linux/platform_device.h, linux/ata_platform.h, asm/io.h, asm/rtc.h, mach-sh03/mach/io.h, mach-sh03/mach/sh03.h, asm/addrspace.h.
- resource/data arrays: cf_ide_resources, heartbeat_resources.
- Source-tree integration: mach-sh03; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c -->
