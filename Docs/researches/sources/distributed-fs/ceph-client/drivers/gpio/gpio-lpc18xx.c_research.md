<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c

## Purpose
`gpio-lpc18xx.c` supports NXP LPC18xx/LPC43xx GPIO ports and their optional eight-line GPIO pin interrupt controller.

## Important APIs, types, and functions
`struct lpc18xx_gpio_chip` holds the gpiochip, main MMIO base, optional pin interrupt controller, and direction lock. `struct lpc18xx_gpio_pin_ic` holds interrupt-controller MMIO, irqdomain, raw lock, and backpointer. GPIO callbacks read/write byte-addressed line data and direction port registers. IRQ domain callbacks allocate parent NVIC IRQs 32-39.

## Control flow
Probe maps the main `gpio` resource by name or legacy index, enables the clock, registers a 256-line gpiochip, then attempts optional pin-IC setup. Pin-IC probe finds the parent IRQ domain, maps the `gpio-pin-ic` resource, creates a hierarchical domain, and stores it for removal. IRQ mask/unmask update rising/falling enable registers and parent masking; EOI clears edge status.

## State and persistence behavior
GPIO line values and direction are in MMIO. Pin interrupt trigger mode is in pin-IC registers. The optional irqdomain persists until remove, where it is explicitly removed.

## Dependencies and integration points
The driver binds to `nxp,lpc1850-gpio`, depends on DT `reg-names`, clocks, pinctrl generic request/free, irqdomain hierarchy, and the parent Cortex-M NVIC domain.

## Risks and edge cases
Pin-IC registration failure is intentionally non-fatal, so GPIO works without IRQs. The `lpc18xx_gpio_pin_ic_isel()` helper has inverted naming around set/clear semantics and must match hardware. Byte-addressed line data writes assume the hardware exposes one byte per GPIO offset.

## Test signals
Test legacy and named resource mapping, clock failure, 256-line get/set/direction, optional pin-IC absent/present cases, IRQ allocation bounds, rising/falling/both/level type behavior, and domain removal on driver remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc18xx.c -->
