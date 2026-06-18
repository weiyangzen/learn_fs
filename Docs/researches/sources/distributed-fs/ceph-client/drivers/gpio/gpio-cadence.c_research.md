
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cadence.c

Purpose: supports the Cadence GPIO IP block, including generic MMIO GPIO operations, optional interrupt demultiplexing, bypass-mode handling, and an AX3000 quirk that skips boot-time pinmux initialization.

Important APIs/types/functions: `struct cdns_gpio_chip` embeds `struct gpio_generic_chip`, MMIO base, saved bypass register, and quirk data. Key functions are `cdns_gpio_request()`, `cdns_gpio_free()`, `cdns_gpio_irq_mask()`, `cdns_gpio_irq_unmask()`, `cdns_gpio_irq_set_type()`, `cdns_gpio_irq_handler()`, `cdns_gpio_probe()`, and `cdns_gpio_remove()`.

Control flow: probe maps registers, reads optional `ngpios`, selects quirks by compatible, optionally forces all pins to input before generic-chip init, configures input/output data and direction registers, enables the peripheral clock, optionally attaches a parent IRQ to a gpio_irq_chip, registers the chip, snapshots bypass mode, and optionally enables output and clears bypass. Request clears bypass for a line; free restores that line's original bypass bit.

State and persistence behavior: `bypass_orig` is persistent software state used to restore bypass on free/remove. Generic-chip state tracks directions/values. IRQ type state lives in hardware `IRQ_VALUE`, `IRQ_TYPE`, and `IRQ_ANY_EDGE` registers. Probe reverts direction if initialization fails before registration.

Dependencies and integration points: integrates with gpiolib generic MMIO, clk framework, OF match data, platform IRQs, and hierarchical gpio_irq_chip setup. Compatible strings are `cdns,gpio-r1p02` and `axiado,ax3000-gpio`.

Risks: only up to 32 GPIOs are supported. The AX3000 quirk trusts firmware boot configuration and skips important register initialization. Both-edge IRQs use a dedicated any-edge bit; platforms without that behavior would misfire. Remove only restores bypass mode, not direction/output state.

Test signals: device-tree probe with and without IRQ, `ngpios` > 32 rejection, request/free bypass transitions, GPIO direction/value tests, IRQ type tests for all supported modes, and AX3000 boot-preserved configuration tests.
