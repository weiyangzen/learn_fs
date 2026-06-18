# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sa1100.c

## Purpose
This ARM SA-1100 GPIO implementation is board/SoC initialization code rather than a discoverable platform driver. It registers one fixed GPIO chip, maps GPIOs to legacy IRQ numbers, handles edge-detect IRQs, and participates in syscore suspend/resume.

## Important APIs, Types, and Functions
`struct sa1100_gpio_chip` stores the gpio chip, register base, IRQ base, and software masks for enabled, rising, falling, and wake IRQs. Gpiolib callbacks are `sa1100_gpio_get/set()`, direction functions, direction query, and `.to_irq`. IRQ functions include `sa1100_gpio_type()`, ack/mask/unmask/wake operations, IRQ domain mapping, and `sa1100_gpio_handler()`.

## Control Flow
`sa1100_init_gpio()` clears edge detect and pending status, registers the gpio chip, creates a simple IRQ domain for 28 GPIO IRQs starting at `IRQ_GPIO0`, and installs chained handlers for GPIO0-10 and GPIO11-27 summary IRQs. The chained handler repeatedly reads GEDR, clears active bits, and calls `generic_handle_irq()` for each set bit.

## State and Persistence
The driver maintains software copies of IRQ rising/falling/mask/wake state and writes GRER/GFER from their intersections. Syscore suspend limits edge detection to wake-enabled lines and clears pending events; resume restores normal edge registers from software state.

## Dependencies and Integration Points
It depends on SA-1100 architecture headers, hard-coded register symbols like `GPLR`, legacy IRQ constants, `sa11x0_gpio_set_wake()`, syscore ops, and gpiolib/irqdomain. The gpio chip uses base 0 and `GPIO_MAX + 1`.

## Risks
There is no dynamic resource management or platform removal path. Direction updates use local IRQ disabling rather than a per-chip spinlock. IRQ type setup accepts any combination with rising/falling bits and does not reject level triggers explicitly. Fixed GPIO numbering and legacy IRQ assumptions must match the platform.

## Test Signals
Validate GPIO get/set/direction against SA-1100 registers, GPIO-to-IRQ mapping, edge-rising/falling/both programming, chained IRQ delivery for individual and grouped parent IRQs, wake enable/disable interactions, and syscore suspend/resume edge restoration.
