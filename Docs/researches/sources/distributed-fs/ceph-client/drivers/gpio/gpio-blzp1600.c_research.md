# sources/distributed-fs/ceph-client/drivers/gpio/gpio-blzp1600.c

## Purpose
This platform driver supports the Blaize BLZP1600 memory-mapped GPIO controller. It uses `gpio-generic` for basic GPIO operations and adds debounce and optional interrupt-controller support.

## Important APIs, types, and functions
`struct blzp1600_gpio` stores the MMIO base, generic GPIO chip, and parent IRQ. Helpers wrap relaxed read/write and read-modify-write. IRQ callbacks are mask/unmask, ack, enable/disable, set type, and `blzp1600_gpio_irqhandler()`. Pinconf support is `blzp1600_gpio_set_config()` for `PIN_CONFIG_INPUT_DEBOUNCE`.

## Control flow
Probe maps the MMIO resource, initializes a generic GPIO chip using input, set, clear, and direction registers, attaches debounce config, and if `interrupt-controller` is present, gets the parent IRQ and fills `gpio_irq_chip`. IRQ enable forces the line to input and enables it; the chained handler reads raw interrupt status and dispatches each pending child IRQ.

## State and persistence behavior
GPIO direction/value, interrupt enable/mask/type/status, and debounce bits live in MMIO registers. The generic chip lock protects RMW operations. No cache or nonvolatile storage is maintained.

## Dependencies and integration points
The driver depends on OF compatible `blaize,blzp1600-gpio`, platform MMIO and IRQ resources, `gpio-generic`, gpiolib irqchip helpers, and chained IRQ handling.

## Risks and edge cases
The mask register semantics are inverted relative to some controllers: mask writes set bits and unmask clears them. Debounce config treats any nonzero debounce argument as enabling one bit and does not scale time. The IRQ handler reads raw status, while ack clears through `GPIO_IC_REG`; ordering should be verified under level interrupts.

## Test signals
Test generic GPIO set/clear/direction, interrupt-controller absent/present paths, all IRQ trigger types and handler selection, mask/unmask semantics, IRQ enable forcing input direction, debounce config, and pending status dispatch.
