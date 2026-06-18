# subset-b-000833 Research

Grouped source-tree-aligned research for SuperH board support files under `sources/distributed-fs/ceph-client/arch/sh/boards`. Each section is bounded for reconciliation into the mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/sdram.S

## Purpose
SH7724 EcoVec24 suspend self-refresh helper code. The exported enter/leave ranges are registered by setup.c for standby, self-refresh, and R-standby; the assembly writes SDRAM controller timing, loops for hardware settle delays, and returns through the common suspend trampoline.

## Important APIs, Types, and Functions
- assembly/entry labels: resume_rstandby, WAIT_400NS, WAIT_400NS_2, DUMMY.

## Control Flow
- The suspend framework jumps into exported enter/leave ranges; assembly performs register programming and delay loops, then returns to the common resume path.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/sys.h, linux/errno.h, linux/linkage.h, asm/asm-offsets.h, asm/suspend.h, asm/romimage-macros.h.
- Source-tree integration: mach-ecovec24; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/sdram.S -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig

## Purpose
Highlander board revision selector under SH_HIGHLANDER. It chooses one of R7780RP, R7780MP, or R7785RP and constrains each to the matching SH7780/SH7785 CPU subtype, with R7785RP selecting GPIOLIB.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_R7780RP, SH_R7780MP, SH_R7785RP.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile

## Purpose
Build glue for Highlander board support. setup.o is always included for the machine; variant-specific IRQ files and R7785RP pinmux support are selected by board Kconfig, and psw.o is included for push switches on non-R7785RP builds.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y				:= setup.o, obj-$(CONFIG_SH_R7780RP)	+= irq-r7780rp.o, obj-$(CONFIG_SH_R7780MP)	+= irq-r7780mp.o, obj-$(CONFIG_SH_R7785RP)	+= irq-r7785rp.o pinmux-r7785rp.o, obj-$(CONFIG_PUSH_SWITCH)	+= psw.o.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780mp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780mp.c

## Purpose
Interrupt routing for the R7780MP Highlander board. It defines INTC vectors, mask registers, an IRL-to-Linux-IRQ table, and highlander_plat_irq_setup to register the board FPGA/external interrupt controller.

## Important APIs, Types, and Functions
- functions: highlander_plat_irq_setup.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, mach/highlander.h.
- resource/data arrays: vectors, mask_registers, irl2irq.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c

## Purpose
Interrupt routing for the R7780RP Highlander board, parallel to the R7780MP file but with the R7780RP external lines and masks. It supplies highlander_plat_irq_setup for the machine vector path in setup.c.

## Important APIs, Types, and Functions
- functions: highlander_plat_irq_setup.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, mach/highlander.h.
- resource/data arrays: vectors, mask_registers, irl2irq.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7785rp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7785rp.c

## Purpose
Interrupt routing for the R7785RP Highlander board. It maps board IRL levels through the FPGA/INTC mask tables and supplies highlander_plat_irq_setup for init_irq.

## Important APIs, Types, and Functions
- functions: highlander_plat_irq_setup.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, mach/highlander.h.
- resource/data arrays: vectors, mask_registers, irl2irq.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7785rp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c

## Purpose
Minimal R7785RP board pinmux setup. highlander_plat_pinmux_setup requests the needed FPGA/GPIO pins for the SH7785 Highlander variant before device drivers depend on them.

## Important APIs, Types, and Functions
- functions: highlander_plat_pinmux_setup.
- integration hooks: gpio_request.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/gpio.h, cpu/sh7785.h, mach/highlander.h.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/psw.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/psw.c

## Purpose
Push-switch platform devices for Highlander S2/S3/S4 buttons. A shared IRQ handler samples FPGA switch status and three platform devices expose push-switch data/resources to the generic push-switch driver.

## Important APIs, Types, and Functions
- functions: psw_irq_handler, psw_init.
- assembly/entry labels: out.
- integration hooks: platform_add_devices, module_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/io.h, linux/module.h, linux/interrupt.h, linux/platform_device.h, mach/highlander.h, asm/push-switch.h.
- resource/data arrays: psw_resources.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/psw.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile

## Purpose
Build glue for HP6xx handheld support: setup.o always, suspend/resume files under CONFIG_PM, and the APM emulation bridge under CONFIG_APM_EMULATION.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y			:= setup.o, obj-$(CONFIG_PM)	+= pm.o pm_wakeup.o, obj-$(CONFIG_APM_EMULATION)	+= hp6xx_apm.o.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/hp6xx_apm.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/hp6xx_apm.c

## Purpose
HP6xx APM emulation provider. It reads battery and AC status from ADC/GPIO, maps values into APM percentage/status states, hooks apm_get_power_status, and uses an interrupt to notify power changes.

## Important APIs, Types, and Functions
- functions: hp6x0_apm_get_power_status, hp6x0_apm_interrupt, hp6x0_apm_init, hp6x0_apm_exit.
- integration hooks: module_init, apm_get_power_status.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/module.h, linux/kernel.h, linux/init.h, linux/interrupt.h, linux/apm-emulation.h, linux/io.h, asm/adc.h, mach/hp6xx.h.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/hp6xx_apm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm.c

## Purpose
HP6xx suspend implementation. It programs SH standby/refresh registers, saves time around suspend, invokes the assembly wakeup path, and registers platform_suspend_ops for PM sleep entry.

## Important APIs, Types, and Functions
- functions: pm_enter, hp6x0_pm_enter, hp6x0_pm_init.
- integration hooks: suspend_set_ops.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.

## Dependencies and Integration Points
- headers: linux/init.h, linux/suspend.h, linux/errno.h, linux/time.h, linux/delay.h, linux/gfp.h, asm/io.h, asm/hd64461.h, asm/bl_bit.h, mach/hp6xx.h.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- timing delays encode hardware settle requirements and are difficult to validate without the board.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm_wakeup.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm_wakeup.S

## Purpose
Low-level wakeup trampoline for HP6xx suspend. The assembly restores MMU/context details needed after standby before C code resumes.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The suspend framework jumps into exported enter/leave ranges; assembly performs register programming and delay loops, then returns to the common resume path.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/linkage.h, cpu/mmu_context.h.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/pm_wakeup.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/setup.c

## Purpose
HP6xx machine setup: HD64461 interrupt controller hookup, CF/IDE platform device, Jornada keyboard, SH DAC audio device, and machine vector setup for the handheld board.

## Important APIs, Types, and Functions
- functions: dac_audio_start, dac_audio_stop, hp6xx_init_irq, hp6xx_devices_setup, hp6xx_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/types.h, linux/init.h, linux/platform_device.h, linux/irq.h, linux/sh_intc.h, sound/sh_dac_audio.h, asm/hd64461.h, asm/io.h, mach/hp6xx.h, cpu/dac.h.
- resource/data arrays: cf_ide_resources.
- Source-tree integration: mach-hp6xx; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-hp6xx/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/Makefile

## Purpose
Build glue for KFR2R09. setup.o and sdram.o are always built; LCD panel command support is added when the SH Mobile LCDC framebuffer driver is enabled.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	:= setup.o sdram.o, obj-y	+=  lcd_wqvga.o.
- Source-tree integration: mach-kfr2r09; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/lcd_wqvga.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/lcd_wqvga.c

## Purpose
KFR2R09 Hitachi TX07D34VM0AAA/R61517 LCD panel command sequencer. It drives the LCDC SYS bus, reads the panel ID, writes initialization tables, clears frame memory, and starts transfer callbacks used by setup.c.

## Important APIs, Types, and Functions
- functions: read_reg, write_reg, write_data, read_device_code, write_memory_start, clear_memory, display_on, kfr2r09_lcd_setup, kfr2r09_lcd_start.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/delay.h, linux/err.h, linux/fb.h, linux/init.h, linux/kernel.h, linux/module.h, linux/gpio.h, video/sh_mobile_lcdc.h, mach/kfr2r09.h, cpu/sh7724.h.
- resource/data arrays: data_frame_if, data_panel, data_timing, data_timing_src, data_gamma, data_power.
- Source-tree integration: mach-kfr2r09; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- timing delays encode hardware settle requirements and are difficult to validate without the board.

## Test Signals
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/lcd_wqvga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/sdram.S

## Purpose
KFR2R09 SH7724 SDRAM self-refresh helper. The exported symbols are registered during device setup to support standby/self-refresh/R-standby transitions.

## Important APIs, Types, and Functions
- assembly/entry labels: resume_rstandby.

## Control Flow
- The suspend framework jumps into exported enter/leave ranges; assembly performs register programming and delay loops, then returns to the common resume path.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/sys.h, linux/errno.h, linux/linkage.h, asm/asm-offsets.h, asm/suspend.h, asm/romimage-macros.h.
- Source-tree integration: mach-kfr2r09; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-kfr2r09/sdram.S -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/Makefile

## Purpose
Build glue for LANDISK series. It unconditionally links setup, IRQ, push-switch, and GIO character-device support for this board family.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o psw.o gio.o.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/gio.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/gio.c

## Purpose
LANDISK GIO character device. It registers a cdev and file operations so userspace ioctl calls can access board GPIO/GIO control registers.

## Important APIs, Types, and Functions
- functions: gio_open, gio_close, gio_ioctl, gio_init, gio_exit.
- integration hooks: module_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- keeps runtime allocation/locking state for exported GPIO, ILSEL, or char-device operations.

## Dependencies and Integration Points
- headers: linux/module.h, linux/init.h, linux/kdev_t.h, linux/cdev.h, linux/fs.h, asm/io.h, linux/uaccess.h, mach-landisk/mach/gio.h, mach-landisk/mach/iodata_landisk.h.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/gio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c

## Purpose
LANDISK board interrupt setup. It defines the board INTC vectors and mask registers and registers them through init_landisk_IRQ.

## Important APIs, Types, and Functions
- functions: init_landisk_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach-landisk/mach/iodata_landisk.h.
- resource/data arrays: vectors_landisk, mask_registers_landisk.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c

## Purpose
LANDISK push-switch devices. It wires power and front-panel switches to the push-switch driver with platform_data and shared IRQ resource handling.

## Important APIs, Types, and Functions
- functions: psw_irq_handler, psw_init.
- assembly/entry labels: out.
- integration hooks: platform_add_devices, device_initcall.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/io.h, linux/init.h, linux/interrupt.h, linux/platform_device.h, mach-landisk/mach/iodata_landisk.h, asm/push-switch.h.
- resource/data arrays: psw_power_resources, psw_usl5p_resources.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/Makefile

## Purpose
Build glue for L-BOX RE2: setup.o and irq.o are linked for the board.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-lboxre2; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/irq.c

## Purpose
L-BOX RE2 interrupt initialization. It programs the board interrupt controller and unmasks/routes external IRQs for platform devices.

## Important APIs, Types, and Functions
- functions: init_lboxre2_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/interrupt.h, linux/irq.h, asm/irq.h, asm/io.h, mach/lboxre2.h.
- Source-tree integration: mach-lboxre2; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/setup.c

## Purpose
L-BOX RE2 machine setup. It registers a CF/IDE platform device using board address resources and supplies an sh_machine_vector with init IRQ support.

## Important APIs, Types, and Functions
- functions: lboxre2_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/ata_platform.h, asm/machvec.h, asm/addrspace.h, mach/lboxre2.h, asm/io.h.
- resource/data arrays: cf_ide_resources.
- Source-tree integration: mach-lboxre2; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-lboxre2/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig

## Purpose
Migo-R LCD-panel selector, choosing between QVGA and RTA WVGA panel configurations under SH_MIGOR.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_MIGOR_QVGA, SH_MIGOR_RTA_WVGA.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Makefile

## Purpose
Build glue for Migo-R. setup.o and sdram.o are always built; QVGA LCD panel sequencing is compiled only for CONFIG_SH_MIGOR_QVGA.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o sdram.o, obj-$(CONFIG_SH_MIGOR_QVGA)	+=  lcd_qvga.o.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/lcd_qvga.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/lcd_qvga.c

## Purpose
Migo-R QVGA LCD setup sequencer. It resets the LCD module over GPIO, writes 8/16-bit panel register tables through LCDC SYS bus ops, adjusts register 0x18, and exposes setup callback to sh_mobile_lcdc.

## Important APIs, Types, and Functions
- functions: reset_lcd_module, adjust_reg18, write_reg, write_reg16, read_reg16, migor_lcd_qvga_seq, migor_lcd_qvga_setup.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/delay.h, linux/err.h, linux/fb.h, linux/init.h, linux/kernel.h, linux/module.h, linux/gpio.h, video/sh_mobile_lcdc.h, cpu/sh7722.h, mach/migor.h.
- resource/data arrays: sync_data, magic0_data, magic1_data, magic2_data, magic3_data.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- timing delays encode hardware settle requirements and are difficult to validate without the board.

## Test Signals
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/lcd_qvga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/sdram.S

## Purpose
Migo-R SDRAM suspend helper. It provides enter/leave self-refresh symbol ranges for the SH Mobile suspend framework.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The suspend framework jumps into exported enter/leave ranges; assembly performs register programming and delay loops, then returns to the common resume path.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/sys.h, linux/errno.h, linux/linkage.h, asm/asm-offsets.h, asm/suspend.h, asm/romimage-macros.h.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/sdram.S -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Kconfig

## Purpose
RTS7751R2D board revision menu. It lets the build choose R2D-PLUS or R2D-1, reflecting PCI slot and interrupt/resource differences.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: RTS7751R2D_PLUS, RTS7751R2D_1.
- Source-tree integration: mach-r2d; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Makefile

## Purpose
Build glue for RTS7751R2D board support, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-r2d; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c

## Purpose
RTS7751R2D interrupt routing. It provides revision-specific vector/mask/IRL tables, demultiplexes external IRL interrupts, and registers board INTC descriptors.

## Important APIs, Types, and Functions
- functions: rts7751r2d_irq_demux, init_rts7751r2d_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach/r2d.h.
- resource/data arrays: vectors_r2d_1, mask_registers_r2d_1, irl2irq_r2d_1, vectors_r2d_plus, mask_registers_r2d_plus, irl2irq_r2d_plus, irl2irq.
- Source-tree integration: mach-r2d; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Kconfig

## Purpose
Renesas Starter Kit board selector for RSK7201, RSK7203, RSK7264, and RSK7269 with CPU subtype dependencies and GPIOLIB selection where needed.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_RSK7201, SH_RSK7203, SH_RSK7264, SH_RSK7269.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Makefile

## Purpose
Build glue for RSK boards: common setup.o plus per-CPU device files for RSK7203, RSK7264, and RSK7269.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y				:= setup.o, obj-$(CONFIG_SH_RSK7203)	+= devices-rsk7203.o, obj-$(CONFIG_SH_RSK7264)	+= devices-rsk7264.o, obj-$(CONFIG_SH_RSK7269)	+= devices-rsk7269.o.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c

## Purpose
RSK7203 extra devices. It registers SMSC911x Ethernet, GPIO LEDs, and GPIO keys through platform devices during device_initcall.

## Important APIs, Types, and Functions
- functions: rsk7203_devices_setup.
- integration hooks: platform_add_devices, device_initcall, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/interrupt.h, linux/smsc911x.h, linux/input.h, linux/gpio.h, linux/gpio_keys.h, linux/leds.h, asm/machvec.h.
- resource/data arrays: smsc911x_resources, rsk7203_gpio_leds, rsk7203_gpio_keys_table.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7264.c

## Purpose
RSK7264 extra devices. It registers the SMSC911x Ethernet platform device with board memory and IRQ resources.

## Important APIs, Types, and Functions
- functions: rsk7264_devices_setup.
- integration hooks: platform_add_devices, device_initcall.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/interrupt.h, linux/input.h, linux/smsc911x.h, asm/machvec.h, asm/io.h.
- resource/data arrays: smsc911x_resources.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7264.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Kconfig

## Purpose
SDK7780 baseboard option selector under SH_SDK7780, gated to CPU_SUBTYPE_SH7780.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_SDK7780_BASE.
- Source-tree integration: mach-sdk7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Makefile

## Purpose
Build glue for SDK7780, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-sdk7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/irq.c

## Purpose
SDK7780 FPGA interrupt setup. It defines FPGA vector and mask tables and registers them through init_sdk7780_IRQ.

## Important APIs, Types, and Functions
- functions: init_sdk7780_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, mach/sdk7780.h.
- resource/data arrays: fpga_vectors, fpga_mask_registers.
- Source-tree integration: mach-sdk7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c

## Purpose
SDK7780 setup. It registers heartbeat and SMC91x Ethernet, tweaks GPIO registers for board setup, and exposes a machine vector with SDK7780 IRQ initialization.

## Important APIs, Types, and Functions
- functions: sdk7780_devices_setup, sdk7780_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/ata_platform.h, asm/machvec.h, mach/sdk7780.h, asm/heartbeat.h, asm/io.h, asm/addrspace.h.
- resource/data arrays: smc91x_eth_resources.
- Source-tree integration: mach-sdk7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7780/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile

## Purpose
Build glue for SDK7786. FPGA, IRQ, NMI, and setup are always included; GPIO and SRAM support are conditional on GPIOLIB and HAVE_SRAM_POOL.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	:= fpga.o irq.o nmi.o setup.o, obj-$(CONFIG_GPIOLIB)		+= gpio.o, obj-$(CONFIG_HAVE_SRAM_POOL)	+= sram.o.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/fpga.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/fpga.c

## Purpose
SDK7786 FPGA mapping and identification. It ioremaps the FPGA register window, reads board/FPGA revision values, and makes the register block available to other SDK7786 helpers.

## Important APIs, Types, and Functions
- functions: sdk7786_fpga_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/io.h, linux/bcd.h, mach/fpga.h, linux/sizes.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/gpio.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/gpio.c

## Purpose
SDK7786 FPGA GPIO driver. It exposes user GPIO pins through gpio_chip callbacks, protects FPGA register access with a spinlock, and registers during device_initcall.

## Important APIs, Types, and Functions
- functions: usrgpir_gpio_direction_input, usrgpir_gpio_get, usrgpir_gpio_setup.
- integration hooks: device_initcall.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- keeps runtime allocation/locking state for exported GPIO, ILSEL, or char-device operations.

## Dependencies and Integration Points
- headers: linux/init.h, linux/interrupt.h, linux/gpio/driver.h, linux/irq.h, linux/kernel.h, linux/spinlock.h, linux/io.h, mach/fpga.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- gpiochip visibility and input value/IRQ behavior can be checked through gpiolib users and board buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c

## Purpose
SDK7786 IRQ initialization. It initializes FPGA-backed interrupt routing using mach/fpga.h and mach/irq.h definitions.

## Important APIs, Types, and Functions
- functions: sdk7786_init_irq.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/irq.h, mach/fpga.h, mach/irq.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c

## Purpose
SDK7786 NMI mode parser and initializer. It parses an nmi_mode setup option, programs FPGA NMI routing/mode bits, and reports invalid mode strings.

## Important APIs, Types, and Functions
- functions: nmi_mode_setup, sdk7786_nmi_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/kernel.h, linux/string.h, mach/fpga.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c

## Purpose
SDK7786 board setup. It registers heartbeat, SMSC911x, FPGA SMBus devices, I2C board data, PCIe clocks, restart/power-off hooks, and machine-vector callbacks for mode pins, clock init, and IRQ init.

## Important APIs, Types, and Functions
- functions: sdk7786_i2c_setup, sdk7786_devices_setup, sdk7786_mode_pins, sdk7786_pcie_clk_enable, sdk7786_pcie_clk_disable, sdk7786_clk_init, sdk7786_restart, sdk7786_power_off, sdk7786_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, i2c_register_board_info, pm_power_off, clk_register, clkdev_add.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/io.h, linux/regulator/fixed.h, linux/regulator/machine.h, linux/smsc911x.h, linux/i2c.h, linux/irq.h, linux/clk.h, linux/clkdev.h.
- resource/data arrays: dummy_supplies, smsc911x_resources.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- static bus addresses and board straps must match hardware for probe success.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/sram.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/sram.c

## Purpose
SDK7786 FPGA SRAM registration. It maps/validates SRAM windows and registers them with the SH SRAM allocator when HAVE_SRAM_POOL is enabled.

## Important APIs, Types, and Functions
- functions: fpga_sram_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/kernel.h, linux/types.h, linux/io.h, linux/string.h, mach/fpga.h, asm/sram.h, linux/sizes.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/Makefile

## Purpose
Build glue for the SH7206 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7206; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c

## Purpose
SH7206 Solution Engine custom external IRQ controller support. It defines register addresses, enable/disable/eoi callbacks, installs irq_chip behavior, and sets interrupt sense/priority during init_se7206_IRQ.

## Important APIs, Types, and Functions
- functions: disable_se7206_irq, enable_se7206_irq, eoi_se7206_irq, make_se7206_irq, init_se7206_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, linux/interrupt.h, mach-se/mach/se7206.h.
- Source-tree integration: mach-se/7206; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/Makefile

## Purpose
Build glue for the SH7343 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7343; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c

## Purpose
SH7343 Solution Engine CPLD interrupt domain. It demultiplexes CPLD status bits, creates a linear irq_domain, initializes generic-chip mask handling, and hooks init_7343se_IRQ.

## Important APIs, Types, and Functions
- functions: se7343_irq_demux, se7343_domain_init, se7343_gc_init, init_7343se_IRQ.
- integration hooks: irq_domain, generic_handle_domain_irq.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/irqdomain.h, linux/io.h, linux/sizes.h, mach-se/mach/se7343.h.
- Source-tree integration: mach-se/7343; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/setup.c

## Purpose
SH7343 Solution Engine setup. It registers heartbeat, NOR flash, 8250 serial, ISP116x USB host, irq_domain-dependent resources, and the board machine vector.

## Important APIs, Types, and Functions
- functions: isp116x_delay, sh7343se_devices_setup, sh7343se_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, irq_domain.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/mtd/physmap.h, linux/serial_8250.h, linux/serial_reg.h, linux/usb/isp116x.h, linux/delay.h, linux/irqdomain.h, asm/machvec.h, mach-se/mach/se7343.h.
- resource/data arrays: nor_flash_partitions, nor_flash_resources, serial_platform_data, usb_resources.
- Source-tree integration: mach-se/7343; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/Makefile

## Purpose
Build glue for the SH770x Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/770x; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/irq.c

## Purpose
SH770x Solution Engine IPR interrupt table. It declares IPR IRQ descriptors and registers them from init_se_IRQ.

## Important APIs, Types, and Functions
- functions: init_se_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/interrupt.h, linux/irq.h, asm/irq.h, asm/io.h, mach-se/mach/se.h.
- resource/data arrays: ipr_irq_table.
- Source-tree integration: mach-se/770x; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/770x/irq.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/Makefile

## Purpose
Build glue for the SH7721 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7721; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/irq.c

## Purpose
SH7721 Solution Engine INTC descriptor with vector and priority registers for board interrupts, registered by init_se7721_IRQ.

## Important APIs, Types, and Functions
- functions: init_se7721_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach-se/mach/se7721.h.
- resource/data arrays: vectors, prio_registers.
- Source-tree integration: mach-se/7721; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c

## Purpose
SH7721 Solution Engine setup. It registers heartbeat and CF/IDE platform devices and supplies setup plus init_irq callbacks in the machine vector.

## Important APIs, Types, and Functions
- functions: se7721_devices_setup, se7721_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, mach-se/mach/se7721.h, mach-se/mach/mrshpc.h, asm/machvec.h, asm/io.h, asm/heartbeat.h.
- resource/data arrays: heartbeat_bit_pos, cf_ide_resources.
- Source-tree integration: mach-se/7721; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7721/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/Makefile

## Purpose
Build glue for the SH7722 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7722; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/irq.c

## Purpose
SH7722 Solution Engine FPGA IRQ domain. It demultiplexes IRQ status bits into domain IRQs, creates mappings, and initializes generic-chip mask registers.

## Important APIs, Types, and Functions
- functions: se7722_irq_demux, se7722_domain_init, se7722_gc_init, init_se7722_IRQ.
- integration hooks: irq_domain, generic_handle_domain_irq.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/irqdomain.h, linux/io.h, linux/err.h, linux/sizes.h, mach-se/mach/se7722.h.
- Source-tree integration: mach-se/7722; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c

## Purpose
SH7722 Solution Engine setup. It registers heartbeat, SMC91x, CF/IDE, and keyscan devices, resolves FPGA IRQ domain mappings for resources, and sets up board pins.

## Important APIs, Types, and Functions
- functions: se7722_devices_setup, se7722_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, irq_domain.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/ata_platform.h, linux/input.h, linux/input/sh_keysc.h, linux/irqdomain.h, linux/smc91x.h, linux/sh_intc.h, mach-se/mach/se7722.h, mach-se/mach/mrshpc.h.
- resource/data arrays: smc91x_eth_resources, cf_ide_resources, sh_keysc_resources.
- Source-tree integration: mach-se/7722; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7722/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/Makefile

## Purpose
Build glue for the SH7724 Solution Engine sub-board, linking setup.o and irq.o plus sdram.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o sdram.o.
- Source-tree integration: mach-se/7724; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c

## Purpose
SH7724 Solution Engine FPGA interrupt support. It maps FPGA interrupt bits to Linux IRQs, provides enable/disable callbacks, demultiplexes chained IRQs, and exports helper mapping functions.

## Important APIs, Types, and Functions
- functions: fpga2irq, get_fpga_irq, disable_se7724_irq, enable_se7724_irq, se7724_irq_demux, init_se7724_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/export.h, linux/topology.h, linux/io.h, linux/err.h, mach-se/mach/se7724.h.
- Source-tree integration: mach-se/7724; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/sdram.S -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/sdram.S

## Purpose
SH7724 Solution Engine SDRAM self-refresh code. It exports enter/leave ranges used by setup.c and contains wait loops and controller register programming for standby resume.

## Important APIs, Types, and Functions
- assembly/entry labels: resume_rstandby, WAIT_LSTATS, WAIT_400NS, WAIT_400NS_2, DUMMY, FRQCRA, KICK, LSTATS.

## Control Flow
- The suspend framework jumps into exported enter/leave ranges; assembly performs register programming and delay loops, then returns to the common resume path.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/sys.h, linux/errno.h, linux/linkage.h, asm/asm-offsets.h, asm/suspend.h, asm/romimage-macros.h.
- Source-tree integration: mach-se/7724; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- suspend/resume cycles should be tested with serial console and memory/peripheral checks after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/sdram.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/setup.c

## Purpose
SH7724 Solution Engine setup. It registers heartbeat, SMC91x and SH Ethernet, NOR flash, LCDC, CEU0/1, FSI audio, keyscan, USB, SDHI, IrDA, VOU, I2C codec data, switch-driven display mode selection, and CEU DMA reservations.

## Important APIs, Types, and Functions
- functions: sh_eth_is_eeprom_ready, sh_eth_init, arch_setup, devices_setup, ms7724se_mv_mem_reserve.
- integration hooks: platform_add_devices, arch_initcall, device_initcall, sh_machine_vector, memblock_phys_alloc, dma_declare_coherent_memory, i2c_register_board_info, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- reserves coherent DMA memory before normal allocation and attaches it to CEU/camera devices.
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: asm/clock.h, asm/heartbeat.h, asm/io.h, asm/suspend.h, cpu/sh7724.h, linux/delay.h, linux/device.h, linux/gpio.h, linux/init.h, linux/input.h.
- resource/data arrays: smc91x_eth_resources, nor_flash_partitions, nor_flash_resources, lcdc_720p_modes, lcdc_vga_modes, lcdc_resources, ceu0_resources, ceu1_resources, fsi_resources, keysc_resources.
- Source-tree integration: mach-se/7724; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/Makefile

## Purpose
Build glue for the SH7751 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7751; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/irq.c

## Purpose
SH7751 Solution Engine IPR IRQ table registration. It supplies init_7751se_IRQ for machine vector interrupt setup.

## Important APIs, Types, and Functions
- functions: init_7751se_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, asm/irq.h, mach-se/mach/se7751.h.
- resource/data arrays: ipr_irq_table.
- Source-tree integration: mach-se/7751; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/setup.c

## Purpose
SH7751 Solution Engine setup. It registers heartbeat LED resources and exposes them through platform_add_devices during device_initcall.

## Important APIs, Types, and Functions
- functions: se7751_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, asm/machvec.h, mach-se/mach/se7751.h, asm/io.h, asm/heartbeat.h.
- resource/data arrays: heartbeat_bit_pos, heartbeat_resources.
- Source-tree integration: mach-se/7751; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7751/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/Makefile

## Purpose
Build glue for the SH7780 Solution Engine sub-board, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o irq.o.
- Source-tree integration: mach-se/7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c

## Purpose
SH7780 Solution Engine external interrupt register setup. It programs interrupt control/priority/mask registers in init_se7780_IRQ.

## Important APIs, Types, and Functions
- functions: init_se7780_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach-se/mach/se7780.h.
- Source-tree integration: mach-se/7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/setup.c

## Purpose
SH7780 Solution Engine setup. It registers heartbeat and SMC91x Ethernet resources, configures GPIO registers, and supplies machine vector setup.

## Important APIs, Types, and Functions
- functions: se7780_devices_setup, se7780_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, asm/machvec.h, mach-se/mach/se7780.h, asm/io.h, asm/heartbeat.h.
- resource/data arrays: smc91x_eth_resources.
- Source-tree integration: mach-se/7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/Makefile

## Purpose
Top-level Solution Engine build dispatcher. It routes CONFIG_SH_*_SOLUTION_ENGINE selections to the correct board subdirectory and includes the SE7619 board file.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-$(CONFIG_SH_7619_SOLUTION_ENGINE)	+= board-se7619.o, obj-$(CONFIG_SH_SOLUTION_ENGINE)	+= 770x/, obj-$(CONFIG_SH_7206_SOLUTION_ENGINE)	+= 7206/, obj-$(CONFIG_SH_7722_SOLUTION_ENGINE)	+= 7722/, obj-$(CONFIG_SH_7751_SOLUTION_ENGINE)	+= 7751/, obj-$(CONFIG_SH_7780_SOLUTION_ENGINE)	+= 7780/, obj-$(CONFIG_SH_7343_SOLUTION_ENGINE)	+= 7343/, obj-$(CONFIG_SH_7721_SOLUTION_ENGINE)	+= 7721/, obj-$(CONFIG_SH_7724_SOLUTION_ENGINE)	+= 7724/.
- Source-tree integration: mach-se; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/board-se7619.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/board-se7619.c

## Purpose
SE7619 board shim. It exposes mode pin handling for the SH7619 Solution Engine without registering extra platform devices in this file.

## Important APIs, Types, and Functions
- functions: se7619_mode_pins.
- integration hooks: sh_machine_vector.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, asm/io.h, asm/machvec.h.
- Source-tree integration: mach-se; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/board-se7619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/Makefile

## Purpose
Build glue for Interface CTP/PCI-SH03. setup.o is always built; the board RTC file is conditional on RTC_DRV_GENERIC.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y	 := setup.o, obj-$(CONFIG_RTC_DRV_GENERIC) += rtc.o.
- Source-tree integration: mach-sh03; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/rtc.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/rtc.c

## Purpose
SH03 legacy RTC implementation. It reads and writes BCD time fields from board registers, provides rtc_generic_ops, and registers time initialization through arch_initcall.

## Important APIs, Types, and Functions
- functions: sh03_rtc_gettimeofday, set_rtc_mmss, sh03_rtc_settimeofday, sh03_time_init.
- integration hooks: platform_device_register, arch_initcall, rtc_generic_ops.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.
- keeps runtime allocation/locking state for exported GPIO, ILSEL, or char-device operations.

## Dependencies and Integration Points
- headers: linux/init.h, linux/kernel.h, linux/sched.h, linux/time.h, linux/bcd.h, linux/spinlock.h, linux/io.h, linux/rtc.h, linux/platform_device.h.
- Source-tree integration: mach-sh03; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- time read/write tests should verify BCD conversion and busy/stop register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c

## Purpose
SH03 setup. It initializes board IRQs, registers CF/IDE and heartbeat platform devices, and integrates the board RTC/machine resources.

## Important APIs, Types, and Functions
- functions: init_sh03_IRQ, sh03_devices_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/pci.h, linux/platform_device.h, linux/ata_platform.h, asm/io.h, asm/rtc.h, mach-sh03/mach/io.h, mach-sh03/mach/sh03.h, asm/addrspace.h.
- resource/data arrays: cf_ide_resources, heartbeat_resources.
- Source-tree integration: mach-sh03; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh03/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/Makefile

## Purpose
Build glue for SH7763RDP, linking setup.o and irq.o.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y    := setup.o irq.o.
- Source-tree integration: mach-sh7763rdp; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/irq.c

## Purpose
SH7763RDP interrupt setup. It programs secondary interrupt priority/mask registers for board external interrupts.

## Important APIs, Types, and Functions
- functions: init_sh7763rdp_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, asm/io.h, asm/irq.h, mach/sh7763rdp.h.
- Source-tree integration: mach-sh7763rdp; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/setup.c

## Purpose
SH7763RDP board setup. It registers NOR flash, SH Ethernet, framebuffer resources, and board pin/configuration setup through device_initcall and machine vector hooks.

## Important APIs, Types, and Functions
- functions: sh7763rdp_devices_setup, sh7763rdp_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/interrupt.h, linux/input.h, linux/mtd/physmap.h, linux/fb.h, linux/io.h, linux/sh_eth.h, linux/sh_intc.h, mach/sh7763rdp.h.
- resource/data arrays: sh7763rdp_nor_flash_partitions, sh7763rdp_nor_flash_resources, sh_eth_resources, sh7763rdp_fb_resources.
- Source-tree integration: mach-sh7763rdp; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
- display bring-up is validated by framebuffer registration and visible panel output at the configured mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sh7763rdp/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/Makefile

## Purpose
Build glue for X3PROTO. It links setup.o and ILSEL support, with GPIO support conditional on GPIOLIB.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- Kbuild evaluates configuration symbols and includes the listed objects or subdirectories in the board image.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kbuild objects: obj-y += setup.o ilsel.o, obj-$(CONFIG_GPIOLIB)		+= gpio.o.
- Source-tree integration: mach-x3proto; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- build tests should compare expected object lists across relevant CONFIG_* combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/gpio.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/gpio.c

## Purpose
X3PROTO GPIO and key interrupt bridge. It exposes FPGA/key GPIOs through gpio_chip, maps GPIOs to IRQs with an irq_domain, and dispatches key-detect interrupts via ILSEL.

## Important APIs, Types, and Functions
- functions: x3proto_gpio_direction_input, x3proto_gpio_get, x3proto_gpio_to_irq, x3proto_gpio_irq_handler, x3proto_gpio_irq_map, x3proto_gpio_setup.
- assembly/entry labels: err_irq, err_gpio.
- integration hooks: irq_domain, generic_handle_domain_irq.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- keeps runtime allocation/locking state for exported GPIO, ILSEL, or char-device operations.

## Dependencies and Integration Points
- headers: linux/init.h, linux/interrupt.h, linux/gpio/driver.h, linux/irq.h, linux/kernel.h, linux/spinlock.h, linux/irqdomain.h, linux/io.h, mach/ilsel.h, mach/hardware.h.
- Source-tree integration: mach-x3proto; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- gpiochip visibility and input value/IRQ behavior can be checked through gpiolib users and board buttons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/ilsel.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/ilsel.c

## Purpose
X3PROTO interrupt level selector allocator. It tracks ILSEL slots in a bitmap, computes register offsets/shifts, enables fixed or allocated levels, and disables them when released.

## Important APIs, Types, and Functions
- functions: ilsel_offset, mk_ilsel_addr, mk_ilsel_shift, __ilsel_enable, ilsel_enable, ilsel_enable_fixed, ilsel_disable.
- integration hooks: EXPORT_SYMBOL.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- keeps runtime allocation/locking state for exported GPIO, ILSEL, or char-device operations.

## Dependencies and Integration Points
- headers: linux/init.h, linux/kernel.h, linux/module.h, linux/bitmap.h, linux/io.h, mach/ilsel.h.
- Source-tree integration: mach-x3proto; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/ilsel.c -->
