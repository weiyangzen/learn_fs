# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mb86s7x.c

Purpose: provides a 32-line GPIO controller for Fujitsu MB86S7x/MB86S70 hardware, with optional ACPI interrupt hookup. The controller uses groups of 8 bits spread across PDR, DDR, and PFR register banks.

Important APIs/types/functions: `struct mb86s70_gpio_chip` stores the `gpio_chip`, MMIO base, and spinlock. Register helpers `PDR()`, `DDR()`, `PFR()`, and `OFFSET()` map a GPIO offset to the right 8-bit lane within 32-bit-spaced registers. GPIO callbacks cover request/free, direction, get, set, and `to_irq()`. Probe and remove are `mb86s70_gpio_probe()` and `mb86s70_gpio_remove()`.

Control flow: probe allocates state, maps resource 0, enables an optional clock, initializes the spinlock, fills `gpio_chip` callbacks, registers the chip, then calls `acpi_gpiochip_request_interrupts()`. Request clears the corresponding PFR bit, handing the pin to GPIO mode; free restores that PFR bit. Direction output writes the desired output value into PDR before setting the DDR bit. Direction input clears the DDR bit. `to_irq()` scans platform IRQ resources and returns the IRQ whose irq_data hardware number equals the GPIO offset.

State and persistence behavior: state is hardware-resident in PFR/PDR/DDR. There is no suspend/resume save path; the optional clock is devm-managed and stays enabled while the device is bound. Spinlocks protect read/modify/write sequences on PFR, PDR, and DDR against concurrent gpiolib callers and interrupt context.

Dependencies and integration points: integrates with platform devices, OF compatible `fujitsu,mb86s70-gpio`, ACPI HID `SCX0007`, optional clocks, and `gpiolib-acpi.h` interrupt helpers. The IRQ integration relies on firmware-provided platform IRQs and their `hwirq` values matching GPIO offsets.

Risks: `to_irq()` loops over platform IRQs until `platform_get_irq()` fails; incorrect firmware IRQ metadata can make GPIO-to-IRQ unavailable. `readl()` values are stored in `unsigned char` in several paths, intentionally using only the low 8 bits but losing any unexpected upper-bit state. No PM restore means GPIO mux/direction/value state must survive platform suspend or be restored elsewhere.

Test signals: probe should register 32 GPIOs with dynamic base and set PFR on request/free. Tests should validate output-before-direction ordering, PDR reads for get, ACPI interrupt request/free on bind/unbind, optional clock handling, and `to_irq()` behavior with matching and missing platform IRQ hwirqs.
