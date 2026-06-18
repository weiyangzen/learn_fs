# sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera.c

## Purpose
This platform driver supports Altera PIO memory-mapped GPIO controllers. It exposes up to 32 software-controlled GPIOs and optionally wires a parent interrupt into child GPIO IRQs.

## Important APIs, types, and functions
`struct altera_gpio_chip` stores the `gpio_chip`, MMIO base, raw spinlock, and configured interrupt trigger. GPIO callbacks are `altera_gpio_get()`, `altera_gpio_set()`, `altera_gpio_direction_input()`, and `altera_gpio_direction_output()`. IRQ callbacks include mask/unmask, set type, startup, edge handler, level-high handler, and `altera_gpio_irq_chip`.

## Control flow
Probe allocates state, reads `altr,ngpio` with a 32-line maximum, maps MMIO, sets GPIO callbacks, and optionally sets up an irqchip if a parent IRQ exists. Interrupt setup requires `altr,interrupt-type`; the parent handler is chosen based on level-high versus edge capture behavior. The driver registers during `subsys_initcall`.

## State and persistence behavior
Direction, data, interrupt mask, and edge-capture state are hardware MMIO registers. The raw spinlock serializes read-modify-write sequences for data, direction, and IRQ masks. The configured interrupt trigger is stored in driver memory and treated as immutable hardware synthesis.

## Dependencies and integration points
Dependencies are platform MMIO resources, OF compatible `altr,pio-1.0`, gpiolib, generic IRQ domains via `gpio_irq_chip`, and chained interrupt handling. It integrates with gpiolib as a normal memory-mapped controller.

## Risks and edge cases
The hardware supports only one synthesized IRQ trigger type, so `irq_set_type()` rejects mismatches. Edge handling loops until no masked edge status remains, while level-high handling samples data once. Overlarge `altr,ngpio` is capped with a warning. Missing `altr,interrupt-type` with an IRQ present fails probe.

## Test signals
Test GPIO direction/value RMW under concurrent access, ngpio default/cap behavior, no-IRQ probe path, each supported interrupt trigger type, edge capture clearing, and level-high child IRQ dispatch.
