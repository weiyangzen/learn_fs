# sources/distributed-fs/ceph-client/arch/mips/rb532/gpio.c

Purpose: RB532 GPIO controller driver for 32 on-chip GPIOs. It exposes direction, value, IRQ mapping, interrupt level/status helpers, and alternate-function configuration.

Important APIs and control flow: `rb532_set_bit()` updates a bit in MMIO with local IRQs disabled. GPIO callbacks implement `get`, `set`, `direction_input`, `direction_output`, and `to_irq`. Exported `rb532_gpio_set_ilevel()`, `rb532_gpio_set_istat()`, and `rb532_gpio_set_func()` are used by IRQ and board code. `rb532_gpio_init()` maps the GPIO register block and registers the chip at arch init.

State, persistence, and integration: state is the mapped GPIO register base and registered `gpio_chip`. Dependencies include rc32434 register definitions, the IRQ controller's GPIO interrupt handling, and consumers using the `"gpio0"` label. Risks include no error handling around `gpiochip_add_data()`, global single-chip assumptions, and direct local IRQ masking instead of a lock. Test signals are `/sys/kernel/debug/gpio`, GPIO-backed CF/button/NAND ready lines, and correct GPIO interrupt polarity.
