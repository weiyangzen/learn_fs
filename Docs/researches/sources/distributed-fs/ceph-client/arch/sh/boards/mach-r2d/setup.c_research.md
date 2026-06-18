<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/setup.c

## Purpose
RTS7751R2D setup for CF/IDE, SCI SPI, heartbeat, SM501 display/controller, NOR flash partitions, trapped I/O, and board power-off behavior.

## Important APIs, Types, and Functions
- functions: r2d_chip_select, rts7751r2d_devices_setup, rts7751r2d_power_off, rts7751r2d_setup.
- integration hooks: platform_add_devices, platform_device_register, device_initcall, sh_machine_vector, spi_register_board_info, pm_power_off, register_trapped_io.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/mtd/mtd.h, linux/mtd/partitions.h, linux/mtd/physmap.h, linux/ata_platform.h, linux/sm501.h, linux/sm501-regs.h, linux/pm.h, linux/fb.h.
- resource/data arrays: cf_ide_resources, spi_bus, spi_sh_sci_resources, heartbeat_resources, sm501_resources, r2d_partitions.
- Source-tree integration: mach-r2d; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- static bus addresses and board straps must match hardware for probe success.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/setup.c -->
