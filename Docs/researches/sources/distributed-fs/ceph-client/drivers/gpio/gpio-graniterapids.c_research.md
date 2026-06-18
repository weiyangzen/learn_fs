
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-graniterapids.c

Purpose: supports Intel Granite Rapids-D virtual GPIO, exposing 128 pad-configuration-backed GPIOs and a shared interrupt handler.

Important APIs/types/functions: `struct gnr_gpio` stores gpiochip, register bases, read-only bitmap, raw spinlock, and PM pad backup. Important functions are `gnr_gpio_configure_line()`, `gnr_gpio_request()`, `gnr_gpio_get()`, `gnr_gpio_direction_input()`, `gnr_gpio_direction_output()`, `gnr_gpio_irq_set_type()`, `gnr_gpio_irq()`, `gnr_gpio_probe()`, `gnr_gpio_suspend()`, and `gnr_gpio_resume()`.

Control flow: probe maps the register resource, reads `GNR_CFG_PADBAR` to locate pad configuration registers, requests a shared non-threaded IRQ, loads read-only pin bits from lock registers, initializes a 128-line gpiochip, attaches a non-parent gpio_irq_chip, and registers. Requests require host software ownership. Set/direction/type changes modify pad config bits under raw spinlock, rejecting read-only pins. IRQ handling scans four status/enable register pairs and dispatches enabled pending bits to the GPIO IRQ domain.

State and persistence behavior: read-only pins are represented by `ro_bitmap`; writable pad config words are saved on suspend and restored on resume. Hardware pad config holds value, direction, ownership, RX mode, and IRQ select. Raw spinlock protects pad and IRQ register RMW operations.

Dependencies and integration points: depends on ACPI ID `INTC1109`, platform IRQ/resources, gpiolib, shared IRQ core, bitmap helpers, and PM sleep ops.

Risks: only rising-edge and high-level IRQ types are supported; falling/low requests fail. IRQs require nonzero `INTSEL`. Read-only lock bits prevent writes but still allow reads. Shared IRQ handling must return accurate handled status to avoid interrupt storms.

Test signals: ACPI binding, host-ownership request rejection, read-only pin write rejection, direction/value programming, rising/high IRQ handling, status ack and enable masking, shared IRQ return behavior, and suspend/resume pad restore.
