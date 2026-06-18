<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/setup.c

## Purpose
Common RSK setup. It provides NOR flash partition/resources, dummy regulators, platform_add_devices, and a generic RSK machine vector.

## Important APIs, Types, and Functions
- functions: rsk_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/interrupt.h, linux/mtd/mtd.h, linux/mtd/partitions.h, linux/mtd/physmap.h, linux/mtd/map.h, linux/regulator/fixed.h, linux/regulator/machine.h.
- resource/data arrays: dummy_supplies, rsk_partitions.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/setup.c -->
