<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c

## Purpose
SDK7780 setup. It registers heartbeat and SMC91x Ethernet, tweaks GPIO registers for board setup, and exposes a machine vector with SDK7780 IRQ initialization.

## Important APIs, Types, and Functions
- functions: sdk7780_devices_setup, sdk7780_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/ata_platform.h, asm/machvec.h, mach/sdk7780.h, asm/heartbeat.h, asm/io.h, asm/addrspace.h.
- resource/data arrays: smc91x_eth_resources.
- Source-tree integration: mach-sdk7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c -->
