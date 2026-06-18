
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ftgpio010.c

Purpose: implements Faraday FTGPIO010-compatible controllers, including generic GPIO operations, interrupt demultiplexing, and optional debounce programming based on clock rate.

Important APIs/types/functions: `struct ftgpio_gpio` stores device, generic chip, MMIO base, and optional clock. Key functions are `ftgpio_gpio_ack_irq()`, `ftgpio_gpio_mask_irq()`, `ftgpio_gpio_unmask_irq()`, `ftgpio_gpio_set_irq_type()`, `ftgpio_gpio_irq_handler()`, `ftgpio_gpio_set_config()`, and `ftgpio_gpio_probe()`.

Control flow: probe maps MMIO, gets parent IRQ, optionally enables the clock, initializes a generic GPIO chip using input, set, clear, and direction-output registers, adds debounce config only if a clock is available, configures gpio_irq_chip with a chained parent handler, disables/unmasks/clears all interrupts, clears debounce enable, and registers the chip. IRQ type programs type, level/polarity, both-edge registers, selects edge/level handler, and acks pending state.

State and persistence behavior: no software state beyond MMIO base and clock pointer. Debounce has one shared prescaler register; the first nonmatching debounce user wins, while later users need the same divisor or receive `-ENOTSUPP`. No PM context is saved.

Dependencies and integration points: depends on OF compatibles for Cortina Gemini, Moxa Moxart, and Faraday FTGPIO010, gpiolib generic MMIO, clk framework, and IRQ core.

Risks: debounce calculation uses the requested microsecond argument as a divisor target and returns unsupported for divisors beyond 24 bits or conflicting existing users. IRQ status uses raw status and relies on individual ack callbacks. No locking protects interrupt register RMW paths.

Test signals: GPIO direction/value operations, interrupt type programming for all supported modes, parent IRQ demux, debounce same/divergent intervals, operation with missing non-deferred clock, and reset of interrupt/debounce registers at probe.
