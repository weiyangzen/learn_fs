# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpfs.c

Purpose: supports Microchip PolarFire SoC GPIO and CoreGPIO RTL v3 blocks, exposing up to 32 GPIOs with regmap-backed value/direction and optional parent IRQs.

Important APIs/types/functions: `struct mpfs_gpio_reg_offsets` selects input/output register offsets for MPFS versus CoreGPIO. `struct mpfs_gpio_chip` stores the regmap, offsets, and gpiochip. GPIO callbacks are direction_input/output, get_direction, get, and set. IRQ callbacks are `mpfs_gpio_irq_set_type()`, mask/unmask, and chained parent `mpfs_gpio_irq_handler()`.

Control flow: probe selects offset data from the OF match, maps resource 0, creates a raw-spinlock regmap, enables the clock, reads optional `ngpios` clamped to 32, fills the gpiochip, counts OF IRQs, and if any exist configures a gpio_irq_chip with one parent per IRQ. Direction input writes `EN_IN` into per-line control. Direction output enables output and output buffer, then updates the output register. IRQ unmask forces the line to input and sets `EN_INT`; the handler reads `MPFS_IRQ_REG`, clears each pending bit by writing it back, and dispatches the domain IRQ.

State and persistence behavior: per-line control registers hold direction and interrupt type/enable. Output and input registers are selected by match data. No explicit PM save/restore exists; the clock is devm-enabled for the device lifetime.

Dependencies and integration points: depends on OF compatibles `microchip,mpfs-gpio` and `microchip,coregpio-rtl-v3`, regmap MMIO, clock framework, OF IRQ counting, and gpiolib hierarchical parent IRQ support.

Risks: `mpfs_gpio_irq_set_type()` lacks a default case that initializes `interrupt_type` for unsupported trigger values, so invalid types can use an uninitialized value rather than returning `-EINVAL`. `mpfs_gpio_set()` calls `mpfs_gpio_get()` before and after updating output but ignores the results, likely leftover debugging or readback flushing. Multiple parent IRQs all share the same handler data and status register scan, so firmware IRQ topology must match hardware expectations.

Test signals: both compatible offset maps, ngpio clamping, direction and value register writes, get using output register for outputs and input register for inputs, IRQ type programming for all supported modes, invalid type behavior, chained IRQ status clear/dispatch, and clock/regmap probe failures.
