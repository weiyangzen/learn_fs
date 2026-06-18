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
