<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/setup.c

## Purpose
Common Highlander machine setup for R7780RP, R7780MP, and R7785RP. It describes USB host/peripheral, CF/IDE, heartbeat LEDs, AX88796 Ethernet, NOR flash, SMBus, trapped I/O, an IVDR clock, power-off hooks, IRQ demux, and the sh_machine_vector.

## Important APIs, Types, and Functions
- functions: r7780rp_devices_setup, ivdr_clk_enable, ivdr_clk_disable, r7780rp_power_off, highlander_setup, highlander_irq_demux, highlander_init_irq.
- integration hooks: platform_add_devices, platform_device_register, device_initcall, sh_machine_vector, i2c_register_board_info, pm_power_off, clk_register, clkdev_add, register_trapped_io.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/io.h, linux/platform_device.h, linux/ata_platform.h, linux/types.h, linux/mtd/physmap.h, linux/i2c.h, linux/irq.h, linux/interrupt.h, linux/usb/r8a66597.h.
- resource/data arrays: r8a66597_usb_host_resources, m66592_usb_peripheral_resources, cf_ide_resources, heartbeat_resources, heartbeat_bit_pos, ax88796_resources, nor_flash_partitions, nor_flash_resources, smbus_resources, lookups.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- static bus addresses and board straps must match hardware for probe success.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/setup.c -->
