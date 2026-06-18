<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/setup.c

## Purpose
LANDISK machine setup. It registers CF/IDE and RTC platform devices, installs a board-specific pm_power_off routine, and exposes the machine vector.

## Important APIs, Types, and Functions
- functions: landisk_power_off, landisk_devices_setup, landisk_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, pm_power_off.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/ata_platform.h, linux/pm.h, linux/mm.h, asm/machvec.h, mach-landisk/mach/iodata_landisk.h, asm/io.h.
- resource/data arrays: cf_ide_resources.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/setup.c -->
