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
