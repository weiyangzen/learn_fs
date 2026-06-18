# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpc8xxx.c

Purpose: supports 32-line GPIO blocks on Freescale/NXP MPC512x, MPC8xxx, QorIQ, and compatible ACPI-described controllers, including generic MMIO GPIO operations, cascaded IRQ domains, and wakeup handling.

Important APIs/types/functions: `struct mpc8xxx_gpio_chip` wraps a `gpio_generic_chip`, MMIO base, raw spinlock, saved direction-output callback, IRQ domain, and parent IRQ number. `mpc_pin2mask()` maps GPIO line 0 to bit 31. Variant hooks in `struct mpc8xxx_gpio_devtype` override direction output, get, or irq_set_type for MPC512x/5125/8572. IRQ flow is implemented by `mpc8xxx_gpio_irq_cascade()`, mask/unmask/ack helpers, `mpc8xxx_irq_set_type()`, and `mpc512x_irq_set_type()`.

Control flow: probe maps registers, initializes a big-endian-bit generic chip over GPIO_DAT and GPIO_DIR, applies little-endian byte-order override when requested, installs variant callbacks, enables QorIQ/ACPI input buffers, registers the gpiochip, obtains the parent IRQ, creates a linear IRQ domain, clears/masks all hardware IRQs, requests a shared cascade IRQ, and enables device wakeup. The cascade handler intersects pending status `IER` with mask `IMR`, then dispatches domain IRQs using reversed bit numbering.

State and persistence behavior: generic chip shadows output data and direction. For MPC8572 errata, output reads use `sdata` for output pins and hardware DAT for input pins. Suspend/resume only toggles parent IRQ wake when device wakeup is enabled; it does not save GPIO register state.

Dependencies and integration points: integrates with OF compatibles for many Freescale/NXP SoCs, ACPI HID `NXP0031`, `gpio-mmio`, generic IRQ domains/chips, runtime PM macros, and gpiolib IRQ resource helpers. It uses `arch_initcall()` for early availability.

Risks: `mpc8xxx_irq_chip.irq_set_type` is a global mutable struct overwritten by probe based on devtype, relying on the assumption that only one controller type exists per machine. `mpc8xxx_remove()` clears a chained handler even though probe used `devm_request_irq()`, suggesting stale cleanup style. IRQ trigger support differs by variant; default accepts falling/low and both-edge only, while MPC512x supports more modes through two-bit fields. No register PM restore is present.

Test signals: variant matching, big-endian bit mapping, QorIQ input buffer enable, MPC5121/5125 input-only restrictions, MPC8572 shadow get behavior, IRQ domain mapping and cascade dispatch, mask/unmask/ack register writes, wakeup enable/disable on suspend/resume, and ACPI probe.
