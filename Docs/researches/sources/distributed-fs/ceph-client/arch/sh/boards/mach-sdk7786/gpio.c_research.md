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
