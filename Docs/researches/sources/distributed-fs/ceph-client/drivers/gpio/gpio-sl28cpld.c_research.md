# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sl28cpld.c

## Purpose
This driver exposes Kontron SL28 CPLD GPIO, input-only, and output-only blocks through the generic `gpio-regmap` core. The full GPIO flavor can also expose an interrupt controller via regmap-irq.

## Important APIs, Types, and Functions
The compatible data maps to `enum sl28cpld_gpio_type` values `SL28CPLD_GPIO`, `SL28CPLD_GPI`, and `SL28CPLD_GPO`. `sl28cpld_gpio_irq_init()` builds a one-register `regmap_irq_chip` with status, unmask, and ack bases. Probe fills `struct gpio_regmap_config` with register bases derived from the child `reg` property.

## Control Flow
Probe validates a parent device, obtains match data, reads the child register base, obtains the parent's regmap, fills common config with eight GPIOs, then switches on type. Full GPIO sets input, output, and direction register bases and optionally initializes IRQs if `interrupt-controller` is present. GPO sets only output; GPI sets only input. Finally it calls `devm_gpio_regmap_register()`.

## State and Persistence
The driver keeps no runtime state beyond the managed regmap-gpio registration. GPIO and IRQ state live in CPLD registers and regmap-irq state.

## Dependencies and Integration Points
It depends on a parent MFD regmap, DT child `reg`, optional platform IRQ, `gpio-regmap`, `regmap_irq`, and Open Firmware compatibles for the three block types.

## Risks
A real direction register at offset zero requires `GPIO_REGMAP_ADDR()` so the generic core does not treat zero as absent; the driver handles this for full GPIO. Interrupt support is conditional on the firmware `interrupt-controller` property and requires a parent IRQ. GPI/GPO variants intentionally lack direction changes.

## Test Signals
Test all three compatibles, child `reg` parsing, missing parent regmap, full GPIO direction/value operations, input-only/output-only limitations, optional interrupt-controller path, regmap IRQ domain attachment, and shared IRQ/oneshot behavior.
