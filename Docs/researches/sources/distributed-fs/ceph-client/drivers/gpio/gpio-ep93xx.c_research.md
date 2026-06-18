
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ep93xx.c

Purpose: supports Cirrus EP93xx GPIO blocks with generic MMIO data/direction handling and optional per-port interrupt support.

Important APIs/types/functions: `struct ep93xx_gpio_chip` wraps MMIO base, generic chip, and optional `struct ep93xx_gpio_irq_chip`. Important functions include `ep93xx_gpio_update_int_params()`, `ep93xx_gpio_irq_type()`, `ep93xx_gpio_irq_ack()`, `ep93xx_gpio_set_config()`, `ep93xx_setup_irqs()`, and `ep93xx_gpio_probe()`.

Control flow: probe maps named `data` and `dir` resources, initializes a byte-wide generic gpiochip, and if IRQ resources exist, maps the named `intr` resource and configures a gpio_irq_chip. A/B ports request one shared parent IRQ and scan an 8-bit status register. F-port style configurations use multiple parent IRQs and a chained handler that maps parent index to GPIO offset. IRQ type sets type/polarity shadow fields, forces the line input, selects edge or level handler, and updates hardware by disabling then rewriting registers.

State and persistence behavior: interrupt configuration is shadowed in `int_unmasked`, `int_enabled`, `int_type1`, `int_type2`, and `int_debounce`. GPIO state is in generic MMIO registers. There is no PM context. Debounce state is one byte per IRQ chip and is updated immediately.

Dependencies and integration points: depends on named platform resources, gpiolib generic helpers, gpio_irq_chip, OF compatible `cirrus,ep9301-gpio`, and postcore initcall registration.

Risks: both-edge IRQs are emulated by toggling polarity on ack and can miss rapid transitions. F-port parent mapping assumes parent IRQ order equals line order. IRQ setup logs but does not abort registration if `ep93xx_setup_irqs()` returns an error before final gpiochip add.

Test signals: data/dir-only probe, A/B shared IRQ dispatch, F-port multi-parent dispatch, all trigger types including both-edge toggling, debounce config, and generic byte-wide GPIO value/direction behavior.
