# sources/distributed-fs/ceph-client/drivers/gpio/gpio-zevio.c

## Purpose
Implements GPIO support for the LSI ZEVIO SoC's four-section, 32-line memory-mapped GPIO controller. Interrupts are intentionally disabled and not exposed due to known lockups.

## Important APIs, Types, And Functions
- `struct zevio_gpio` stores the gpiochip, spinlock, and MMIO base.
- `zevio_gpio_port_get` and `zevio_gpio_port_set` calculate the eight-line section offset and access per-section registers.
- `zevio_gpio_get`, `zevio_gpio_set`, `zevio_gpio_direction_input`, and `zevio_gpio_direction_output` implement gpiolib callbacks.
- `zevio_gpio_to_irq` returns `-ENXIO` because IRQ support is not implemented.
- `zevio_gpio_probe` maps registers, registers the chip, initializes locking, and masks interrupts in all sections.

## Control Flow
Probe copies a static chip template, assigns parent and fwnode-derived label, maps the MMIO resource, registers the 32-line chip, initializes the spinlock, and writes `0xFF` to each section's interrupt-mask register. Reads choose the input register for pins whose direction bit is set and the output register otherwise. Direction output writes the requested output value first, then clears the direction bit.

## State And Persistence
Hardware registers store direction, output, input, and interrupt mask/status state. The driver has no shadow state. Interrupts are masked at probe and remain unsupported through gpiolib.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF compatible `lsi,zevio-gpio`, gpiolib, fwnode labeling, and built-in platform driver registration.

## Risks And Edge Cases
The spinlock is initialized after `devm_gpiochip_add_data`, leaving a small theoretical window if callbacks could run immediately during registration. IRQ-related registers are present but intentionally disabled, so consumers requiring interrupts will fail. The section math assumes exactly four sections and 32 lines.

## Test Signals
Check section/bit mapping at pins 7, 8, 15, 16, 31, direction bit polarity, output-before-direction behavior, interrupt mask writes for each section, `to_irq` failure, and callback safety around probe ordering.
