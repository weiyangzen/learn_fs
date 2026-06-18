# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sch.c

## Purpose
This driver supports Intel Poulsbo SCH, Tunnel Creek, Centerton, and Quark-style GPIO blocks behind LPC/iLB platform devices. It handles core and resume-powered banks, GPIO direction/value operations, and optional IRQ delivery via ACPI GPE.

## Important APIs, Types, and Functions
`struct sch_gpio` stores the gpio chip, mapped I/O registers, spinlock, resume-bank base, GPE number, and GPE handler. `sch_gpio_offset()` and `sch_gpio_bit()` map logical GPIO numbers to banked 8-bit registers. GPIO callbacks operate on GEN/GIO/GLV. IRQ support includes `sch_irq_type()`, ack, mask/unmask, immutable `sch_irqchip`, and `sch_gpio_gpe_handler()`.

## Control Flow
Probe maps an IORESOURCE_IO range, copies the template gpio chip, selects GPIO count and resume-bank split from `pdev->id`, performs model-specific enable writes, configures a GPIO IRQ chip without a direct parent handler, installs an ACPI GPE handler if possible, and registers the chip. The GPE handler reads core and resume status registers, merges them into logical pending bits, dispatches domain IRQs, and asks ACPICA to re-enable the GPE.

## State and Persistence
GPIO and IRQ configuration live in I/O registers. The driver has no explicit suspend/resume hooks. GPE installation is devm-managed and removed by disabling/removing the ACPI handler.

## Dependencies and Integration Points
It uses platform devices identified by Intel PCI IDs, ACPI GPE APIs, I/O port mapping, gpiolib IRQ domains, and immutable irqchip helpers. IRQ delivery depends on ACPI GPE0E GPIO bit 14.

## Risks
If ACPI GPE setup fails, the driver still registers GPIOs but warns that IRQ support is unavailable. Direction-output cannot preset the output value before switching direction because hardware makes GLV read-only for inputs, so a short low pulse is documented. Logical-to-bank mapping depends on correct `resume_base` per device ID.

## Test Signals
Test all supported `pdev->id` variants, core/resume bank offset mapping, model-specific enable writes, direction-output pulse-sensitive consumers, edge rising/falling/both programming, GPE failure fallback, and pending status dispatch across both banks.
