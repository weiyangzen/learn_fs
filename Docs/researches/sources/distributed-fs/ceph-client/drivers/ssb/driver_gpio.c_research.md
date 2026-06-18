# sources/distributed-fs/ceph-client/drivers/ssb/driver_gpio.c

## Purpose
GPIO provider for SSB systems, exposing ChipCommon or EXTIF GPIO registers through gpiolib and, on embedded SSB buses, mapping GPIO lines to Linux IRQs.

## Important APIs, Types, and Functions
Public functions are `ssb_gpio_init` and `ssb_gpio_unregister`. Backend functions implement gpiolib callbacks for get/set/direction/request/free for ChipCommon and get/set/direction for EXTIF. Embedded builds add `ssb_gpio_to_irq`, irq chips, IRQ handlers, domain init/exit for both backends.

## Control Flow
`ssb_gpio_init` prefers ChipCommon when available, otherwise EXTIF. Backend init fills `bus->gpio`, sets deterministic base 0 for SoC SSB buses or dynamic base for others, initializes IRQ domain if embedded, then registers with `gpiochip_add_data`. IRQ handlers compute pending lines from `(GPIOIN ^ polarity) & mask`, dispatch each line through the irqdomain, then update polarity to current values for edge-like behavior. Unregister removes the gpiochip; domain exit runs on init failure paths.

## State and Persistence
State is `bus->gpio`, optional `bus->irq_domain`, and backend hardware GPIO output, enable, pull, polarity, and interrupt mask registers. ChipCommon request/free also changes pull-up/down state.

## Dependencies and Integration Points
Depends on gpiolib, irqdomain, generic IRQ handling, SSB ChipCommon/EXTIF helpers, and `ssb_mips_irq` for parent interrupt selection.

## Risks
The unregister path removes only the gpiochip and does not explicitly call backend IRQ domain exit, so teardown depends on gpiolib/lifetime expectations. `free_irq` passes `chipco`/`extif` while `request_irq` used `bus` as `dev_id`, which looks suspicious for shared IRQ removal. IRQ polarity-toggling must be correct or edges can be lost/repeated.

## Test Signals
GPIO chip appears with 16 ChipCommon or 5 EXTIF lines, direction/value operations update hardware, `to_irq` works only for SoC SSB buses, GPIO IRQs dispatch through the domain, and module/bus removal does not leave IRQ mappings behind.
