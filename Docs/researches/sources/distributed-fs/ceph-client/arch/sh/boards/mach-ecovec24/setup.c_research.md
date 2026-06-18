<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/setup.c

## Purpose
Full EcoVec24 board description for SH7724: NOR, Ethernet, USB host/function/USBHS, LCD/DVI, CEU cameras, keys, touchscreen, regulators, SDHI/MMC/SPI, FSI audio, IrDA, VOU, and CEU DMA reservations. It performs large GPIO mux setup in arch_setup, registers I2C/SPI/gpiod tables, reads the Ethernet MAC from EEPROM over I2C, and exposes an sh_machine_vector with CEU memory reservation.

## Important APIs, Types, and Functions
- functions: usb0_port_power, usb1_port_power, usbhs_get_id, usbhs_phy_reset, ts_get_pendown_state, ts_init, mmc_spi_setpower, mac_read, sh_eth_init, arch_setup, devices_setup, ecovec_mv_mem_reserve.
- integration hooks: platform_add_devices, platform_device_register, arch_initcall, device_initcall, sh_machine_vector, memblock_phys_alloc, dma_declare_coherent_memory, gpiod_add_lookup_table, i2c_register_board_info, spi_register_board_info, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- reserves coherent DMA memory before normal allocation and attaches it to CEU/camera devices.
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: asm/clock.h, asm/heartbeat.h, asm/suspend.h, cpu/sh7724.h, linux/delay.h, linux/device.h, linux/i2c.h, linux/io.h, linux/init.h, linux/input.h.
- resource/data arrays: led_pos, nor_flash_partitions, nor_flash_resources, sh_eth_resources, usb0_host_resources, usb1_common_resources, usbhs_resources, ecovec_lcd_modes, ecovec_dvi_modes, lcdc_resources.
- Source-tree integration: mach-ecovec24; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.
- static bus addresses and board straps must match hardware for probe success.
- early memory reservation failure panics or leaves capture devices without coherent buffers.
- timing delays encode hardware settle requirements and are difficult to validate without the board.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/setup.c -->
