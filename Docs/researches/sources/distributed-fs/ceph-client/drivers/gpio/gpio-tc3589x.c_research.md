<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c

Purpose: exposes Toshiba TC3589x MFD GPIO lines and nested interrupts, including drive-mode configuration for push-pull, open-drain, and open-source modes.

Important APIs, types, and functions: `struct tc3589x_gpio` owns the gpiochip, parent MFD pointer, IRQ mutex, and cached interrupt registers. GPIO callbacks are `tc3589x_gpio_get()`, `tc3589x_gpio_set()`, direction helpers, `tc3589x_gpio_get_direction()`, and `tc3589x_gpio_set_config()`. IRQ callbacks cache `REG_IBE`, `REG_IEV`, `REG_IS`, `REG_IE`, and `REG_DIRECT`, flush them in `tc3589x_gpio_irq_sync_unlock()`, and dispatch nested IRQs in `tc3589x_gpio_irq()`.

Control flow: probe obtains the parent MFD data and parent IRQ, allocates state, brings the GPIO block out of reset, disables direct keyboard interrupts, installs a threaded IRQ handler, configures a threaded nested gpio IRQ chip, and registers the gpiochip. GPIO set uses a two-byte data/mask block write.

State and persistence behavior: hardware registers hold values, directions, drive modes, and interrupt state. Cached IRQ register arrays coalesce bus writes during IRQ bus lock/unlock. No suspend cache is implemented here.

Dependencies and integration points: depends on `linux/mfd/tc3589x.h` register helpers, platform MFD child creation, threaded IRQ handling, gpiolib nested IRQ support, and pinconf drive parameters.

Risks and test signals: failed writes during IRQ cache flush are not propagated. Interrupt cache must remain synchronized with hardware across reset or external modification. Test reset release, direction and get/set paths, open-drain/open-source register programming, IRQ type combinations, mask/unmask cache flushing, threaded nested IRQ dispatch, and status clear after handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tc3589x.c -->
