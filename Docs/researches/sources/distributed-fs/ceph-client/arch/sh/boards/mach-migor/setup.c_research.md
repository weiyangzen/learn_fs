<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/setup.c

## Purpose
Migo-R board setup. It declares SMC91x Ethernet, keyscan, NOR/NAND flash, LCDC, CEU camera, SDHI, regulators, camera I2C devices, GPIO lookup tables, and CEU DMA reservation.

## Important APIs, Types, and Functions
- functions: migor_nand_flash_cmd_ctl, migor_nand_flash_ready, migor_devices_setup, migor_mode_pins, migor_mv_mem_reserve.
- integration hooks: platform_add_devices, arch_initcall, sh_machine_vector, memblock_phys_alloc, dma_declare_coherent_memory, gpiod_add_lookup_table, i2c_register_board_info, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- reserves coherent DMA memory before normal allocation and attaches it to CEU/camera devices.
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/clkdev.h, linux/dma-map-ops.h, linux/init.h, linux/platform_data/tmio.h, linux/platform_device.h, linux/interrupt.h, linux/input.h, linux/input/sh_keysc.h, linux/memblock.h, linux/mmc/host.h.
- resource/data arrays: smc91x_eth_resources, sh_keysc_resources, migor_nor_flash_partitions, migor_nor_flash_resources, migor_nand_flash_partitions, migor_nand_flash_resources, migor_lcd_modes, migor_lcdc_resources, migor_ceu_resources, fixed3v3_power_consumers.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.
- static bus addresses and board straps must match hardware for probe success.
- early memory reservation failure panics or leaves capture devices without coherent buffers.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/setup.c -->
