<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c

Purpose: provides the reusable Intel Tangier-family GPIO core, including MMIO GPIO direction/value handling, debounce configuration, chained interrupt handling, wake mask programming, pinctrl range registration, and suspend/resume context save.

Important APIs, types, and functions: `struct tng_gpio_context` stores saved per-32-line registers. The exported entry point is `devm_tng_gpio_probe()`, and exported PM ops are `tng_gpio_pm_ops`. GPIO callbacks include `tng_gpio_get()`, `tng_gpio_set()`, direction helpers, `tng_gpio_get_direction()`, and `tng_gpio_set_config()`. IRQ callbacks are `tng_irq_ack()`, `tng_irq_mask()`, `tng_irq_unmask()`, `tng_irq_set_type()`, `tng_irq_set_wake()`, and chained `tng_irq_handler()`.

Control flow: platform wrapper code fills `struct tng_gpio` from `gpio-tangier.h` and calls `devm_tng_gpio_probe()`. The core allocates context storage, initializes gpiochip callbacks and a nested gpio IRQ chip, wires one parent IRQ to `tng_irq_handler()`, then registers the chip. IRQ type programming updates rising/falling/level polarity registers and switches the Linux IRQ flow handler. Suspend snapshots level, direction, edge, mask, and wake registers; resume restores them.

State and persistence behavior: line state lives in MMIO, with register snapshots in `ctx` only across system sleep. `raw_spinlock_t lock` serializes register RMW sequences. Wake status is cleared when wake is configured.

Dependencies and integration points: depends on gpiolib, irqchip helpers, pinconf generic bias delegation, pinctrl ranges from platform data, and namespace export `GPIO_TANGIER` for wrappers.

Risks and test signals: wrapper-provided `ngpio`, wake register offsets, IRQ number, and pin ranges must match hardware. Level-trigger programming intentionally writes polarity before type to avoid glitches. Test GPIO input/output, debounce enable/disable, each IRQ type, wake mask changes, chained IRQ fan-out, pin range registration, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tangier.c -->
