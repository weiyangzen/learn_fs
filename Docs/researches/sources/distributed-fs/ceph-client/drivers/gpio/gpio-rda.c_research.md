# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rda.c

## Purpose
This platform driver supports RDA Micro GPIO banks. It uses `gpio_generic_chip` for the simple data, set/clear, and direction registers, and adds optional GPIO interrupt support for banks that expose a parent IRQ.

## Important APIs, Types, and Functions
`struct rda_gpio` wraps `struct gpio_generic_chip`, the MMIO base, a spinlock used by read-modify-write register updates, and an optional parent IRQ. `rda_gpio_update()` updates one bit in a register. IRQ support is implemented by `rda_gpio_set_irq()`, `rda_gpio_irq_mask()`, `rda_gpio_irq_unmask()`, `rda_gpio_irq_ack()`, `rda_gpio_irq_set_type()`, and chained handler `rda_gpio_irq_handler()`.

## Control Flow
`rda_gpio_probe()` reads required `ngpios`, obtains an optional IRQ, maps the MMIO resource, initializes the generic GPIO chip with value/set/clear and output-enable set-in/set-out registers, then registers it. If an IRQ exists, the driver configures a `gpio_irq_chip` with one parent IRQ and the chained parent handler. The IRQ handler reads `RDA_GPIO_INT_STATUS`, masks to the low 8 interrupt-capable lines, and dispatches domain IRQs.

## State and Persistence
GPIO state persists in hardware registers only. Trigger type is programmed directly into `RDA_GPIO_INT_CTRL_SET/CLR`; the driver does not keep software shadow copies beyond the generic chip's internal state. There are no suspend/resume hooks.

## Dependencies and Integration Points
The driver depends on platform device resources, firmware property `ngpios`, gpiolib generic helpers, and chained irqchip support. IRQ-capable variants expose only the lower eight lines as interrupt sources.

## Risks
`ngpios` is required and not bounded against the bank width in this file, so bad firmware can expose nonsensical line counts. Level-high and level-low setup writes only the selected rise/fall bit with the level bit; previous opposite-edge configuration relies on hardware clear behavior and mask calls. Optional parent IRQ handling means consumers must tolerate GPIO-only banks.

## Test Signals
Exercise banks with and without parent IRQs, verify lower-eight IRQ routing only, test all five trigger modes, confirm mask/unmask disables both rise/fall sources, and validate GPIO generic direction/value behavior for the configured `ngpios`.
