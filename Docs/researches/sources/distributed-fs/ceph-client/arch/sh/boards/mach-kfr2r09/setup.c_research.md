<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/setup.c

## Purpose
KFR2R09 board setup for SH7724. It registers NOR/OneNAND, keyscan, LCDC/panel, optional USB gadget, CEU camera, SDHI, fixed regulators, camera clock aliases, I2C board devices, and CEU coherent memory reservation.

## Important APIs, Types, and Functions
- functions: kfr2r09_usb0_gadget_i2c_setup, kfr2r09_serial_i2c_setup, kfr2r09_usb0_gadget_setup, kfr2r09_devices_setup, kfr2r09_mode_pins, kfr2r09_mv_mem_reserve.
- integration hooks: platform_add_devices, platform_device_register, device_initcall, sh_machine_vector, memblock_phys_alloc, dma_declare_coherent_memory, gpiod_add_lookup_table, i2c_register_board_info, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- reserves coherent DMA memory before normal allocation and attaches it to CEU/camera devices.
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: asm/clock.h, asm/io.h, asm/machvec.h, asm/suspend.h, cpu/sh7724.h, linux/clkdev.h, linux/delay.h, linux/gpio.h, linux/gpio/machine.h, linux/i2c.h.
- resource/data arrays: kfr2r09_nor_flash_partitions, kfr2r09_nor_flash_resources, kfr2r09_nand_flash_resources, kfr2r09_sh_keysc_resources, kfr2r09_lcdc_modes, kfr2r09_sh_lcdc_resources, kfr2r09_usb0_gadget_resources, kfr2r09_ceu_resources, fixed3v3_power_consumers, kfr2r09_sh_sdhi0_resources.
- Source-tree integration: mach-kfr2r09; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/setup.c -->
