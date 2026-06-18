<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7269.c

## Purpose
RSK7269 extra devices. It registers SMSC911x Ethernet resources and uses GPIO-related setup for the board revision.

## Important APIs, Types, and Functions
- functions: rsk7269_devices_setup.
- integration hooks: platform_add_devices, device_initcall.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/interrupt.h, linux/input.h, linux/smsc911x.h, linux/gpio.h, asm/machvec.h, asm/io.h.
- resource/data arrays: smsc911x_resources.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7269.c -->
