<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/setup.c

## Purpose
SH770x Solution Engine setup. It configures the SMSC Super I/O, registers CF/IDE, heartbeat, and two SH Ethernet devices, then exposes machine-vector setup/IRQ hooks.

## Important APIs, Types, and Functions
- functions: smsc_config, smsc_setup, se_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/sh_eth.h, mach-se/mach/se.h, mach-se/mach/mrshpc.h, asm/machvec.h, asm/io.h, asm/smc37c93x.h, asm/heartbeat.h.
- resource/data arrays: cf_ide_resources, heartbeat_bit_pos, sh_eth0_resources, sh_eth1_resources.
- Source-tree integration: mach-se/770x; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/setup.c -->
