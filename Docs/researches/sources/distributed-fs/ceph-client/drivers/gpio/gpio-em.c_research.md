
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-em.c

Purpose: implements Renesas Emma Mobile GIO GPIO and interrupt support, including two MMIO windows, pinctrl integration, and an IRQ domain.

Important APIs/types/functions: `struct em_gio_priv` stores two bases, sense lock, platform device, gpiochip, irqchip, and IRQ domain. Key functions are `em_gio_irq_set_type()`, `em_gio_irq_handler()`, `em_gio_direction_input()`, `em_gio_direction_output()`, `em_gio_set()`, `em_gio_to_irq()`, `em_gio_free()`, `em_gio_irq_domain_map()`, and `em_gio_probe()`.

Control flow: probe obtains two parent IRQs and two MMIO resources, reads `ngpios`, sets GPIO callbacks and pinctrl request/free, builds an IRQ domain, requests low and high parent IRQs with the same handler, and registers the gpiochip. IRQ type programming disables a line in `GIO_IIA`, updates its 4-bit sense field in one of four `GIO_IDT` registers, clears pending state, and reenables it. Parent IRQ handling drains `GIO_MST`, clears each bit in `GIO_IIR`, and dispatches through the domain.

State and persistence behavior: no suspend context is saved. Sense programming is serialized by `sense_lock`. `em_gio_free()` returns the line to input after freeing pinctrl, avoiding stale output drive on later requests. Output values are written through low/high masked registers.

Dependencies and integration points: depends on OF property `ngpios`, pinctrl GPIO helpers, platform IRQs/resources, gpiolib, irqdomain, and postcore initcall ordering.

Risks: no PM restore means sleep states that reset GIO hardware would lose configuration. The IRQ domain handler uses level handling by default while type-specific sense is programmed separately. Both parent IRQs use the same status register and handler, so hardware status semantics must be correct.

Test signals: two-resource/two-IRQ probe, pinctrl request/free, input-on-free behavior, all supported trigger types, low/high output register writes, domain mapping, and draining multiple pending IRQ bits.
