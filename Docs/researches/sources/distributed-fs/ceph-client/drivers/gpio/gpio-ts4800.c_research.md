<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c

Purpose: supports the Technologic Systems TS-4800 FPGA GPIO block through the generic GPIO MMIO helper.

Important APIs, types, and functions: `ts4800_gpio_probe()` is the only substantive function. It configures `gpio_generic_chip_config` with 16-bit register width, separate input, output, and direction-output registers.

Control flow: probe allocates a generic chip, maps the MMIO resource, initializes generic GPIO with `dat`, `set`, and `dirout` offsets, then registers the gpiochip. The platform driver uses `module_platform_driver_probe()`.

State and persistence behavior: no private state beyond the generic chip; GPIO value and direction are in FPGA registers. No IRQ or PM support is implemented.

Dependencies and integration points: depends on OF compatible `technologic,ts4800-gpio`, platform MMIO resource mapping, and `gpio_generic_chip_init()`.

Risks and test signals: `dat` points at the input register while `set` points at output; readback behavior depends on generic GPIO semantics and hardware mirroring. The static driver struct also sets `.probe`, while the macro supplies probe registration. Test resource mapping failure, generic-chip initialization, 16-bit register access, direction-output register polarity, and OF match loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4800.c -->
