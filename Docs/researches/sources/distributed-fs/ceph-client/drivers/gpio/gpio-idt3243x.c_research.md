<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c

## Purpose
`gpio-idt3243x.c` supports the GPIO block and optional interrupt controller on IDT/Renesas 79RC3243x SoCs. It uses gpio-generic for GPIO register access and a chained irqchip for level-triggered GPIO interrupts through the SoC PIC.

## Important APIs, types, and functions
`struct idt_gpio_ctrl` embeds `gpio_generic_chip`, stores PIC and GPIO MMIO bases, and caches the interrupt mask. GPIO setup uses `gpio_generic_chip_init()`. IRQ flow uses `idt_gpio_dispatch()`, `idt_gpio_irq_set_type()`, `idt_gpio_ack()`, `idt_gpio_mask()`, `idt_gpio_unmask()`, and `idt_gpio_irq_init_hw()`.

## Control flow
Probe maps the named `gpio` resource, initializes the generic chip, optionally applies firmware `ngpios`, and, when `interrupt-controller` is present, maps the named `pic` resource, gets a parent IRQ, initializes all interrupts masked, and installs a chained child domain. Dispatch reads PIC pending bits, removes masked bits, and forwards mapped GPIO IRQs.

## State and persistence behavior
GPIO direction and data live in hardware registers. `mask_cache` mirrors PIC mask state so dispatch can filter pending bits and mask/unmask can update registers atomically under the generic lock.

## Dependencies and integration points
The driver binds to `idt,32434-gpio`, depends on named platform resources `gpio` and optionally `pic`, gpiolib, gpio-generic, and chained IRQ support.

## Risks and edge cases
Hardware only supports level-triggered interrupts; edge requests fail. `idt_gpio_ack()` writes `~BIT(hwirq)` to `ISTAT`, which depends on the SoC's write-one/zero-clear semantics and is high risk if reused on variants. Optional IRQ support means DT property/resource mismatches can remove interrupt capability.

## Test signals
Test GPIO get/set/direction, `ngpios` override, level-high/low IRQ type setup, rejection of edge triggers, mask cache behavior, chained dispatch with masked pending bits, and resource-name failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idt3243x.c -->
