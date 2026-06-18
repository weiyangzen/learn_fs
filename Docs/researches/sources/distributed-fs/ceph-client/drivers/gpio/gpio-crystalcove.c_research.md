
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-crystalcove.c

Purpose: supports Intel Crystal Cove PMIC GPIOs, including 16 physical GPIOs, selected virtual ACPI GPIOs, nested interrupt handling, and debugfs GPIO state display.

Important APIs/types/functions: `struct crystalcove_gpio` stores the gpiochip, PMIC regmap, IRQ bus mutex, deferred IRQ update flags, trigger value, and mask flag. Key functions are `to_reg()`, `crystalcove_gpio_dir_in()`, `crystalcove_gpio_dir_out()`, `crystalcove_gpio_get()`, `crystalcove_gpio_set()`, `crystalcove_irq_type()`, `crystalcove_bus_sync_unlock()`, `crystalcove_gpio_irq_handler()`, `crystalcove_gpio_dbg_show()`, and `crystalcove_gpio_probe()`.

Control flow: probe gets the MFD parent regmap and IRQ, initializes a 95-line can-sleep gpiochip, configures a threaded gpio_irq_chip with no automatic parent handler, requests the PMIC IRQ, and registers the chip. GPIO operations translate a logical line to control/input registers; physical GPIOs map to per-port registers and virtual GPIO 0x5e maps to panel control. IRQ type/mask changes are staged under bus lock and committed in bus-sync-unlock, while the threaded parent reads/acks PMIC IRQ status and dispatches nested IRQs for physical GPIOs.

State and persistence behavior: PMIC registers hold GPIO and IRQ state. Software staging fields `update`, `intcnt_value`, and `set_irq_mask` persist only across genirq bus-lock windows. Virtual GPIOs outside supported mapping return success/zero for direction/set/get paths rather than hard errors.

Dependencies and integration points: depends on Intel SoC PMIC MFD, regmap, gpiolib, nested threaded IRQ handling, and `DOMAIN_BUS_WIRED` to distinguish its IRQ domain on a shared MFD fwnode.

Risks: `to_reg()` silently ignores unsupported virtual GPIO operations in several callbacks. IRQ state staging uses single fields, so it relies on genirq bus locking serializing one IRQ update at a time. Only edge triggers are supported for physical GPIO IRQs.

Test signals: physical GPIO get/set/direction, virtual panel GPIO access, threaded IRQ dispatch for both GPIO IRQ status registers, mask/type bus-lock batching, debug output fields, and shared-fwnode IRQ-domain token behavior.
