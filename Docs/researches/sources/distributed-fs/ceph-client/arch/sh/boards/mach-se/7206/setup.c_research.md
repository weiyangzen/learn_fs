<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/setup.c

## Purpose
SH7206 Solution Engine setup. It registers SMC91x Ethernet and heartbeat LEDs, exposes mode pins, and adds board platform devices during device_initcall.

## Important APIs, Types, and Functions
- functions: se7206_devices_setup, se7206_mode_pins.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/smc91x.h, mach-se/mach/se7206.h, asm/io.h, asm/machvec.h, asm/heartbeat.h.
- resource/data arrays: smc91x_resources, heartbeat_bit_pos.
- Source-tree integration: mach-se/7206; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/setup.c -->
