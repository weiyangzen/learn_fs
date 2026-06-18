# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgs-iproc.c

## Purpose
Supports Broadcom XGS iProc CCA GPIO controllers using generic MMIO GPIO helpers plus an optional shared parent interrupt line for level and edge GPIO interrupts.

## Important APIs, Types, And Functions
- `struct iproc_gpio_chip` embeds `gpio_generic_chip`, lock, device pointer, GPIO register base, and interrupt-controller register base.
- `iproc_gpio_irq_ack`, `iproc_gpio_irq_mask`, `iproc_gpio_irq_unmask`, and `iproc_gpio_irq_set_type` manipulate event, level, polarity, and mask registers.
- `iproc_gpio_irq_handler` services the shared parent IRQ and dispatches child GPIO IRQs.
- `iproc_gpio_probe` initializes the generic GPIO chip, optional IRQ support, and registers the chip.
- `iproc_gpio_remove` disables the CCA GPIO interrupt bit when the interrupt block was mapped.

## Control Flow
Probe maps the GPIO resource, initializes generic data/output/direction registers, optionally overrides `ngpio`, and if a platform IRQ exists maps the interrupt resource, enables the CCA GPIO interrupt bit, requests a shared IRQ, and installs a simple child irqchip. The handler checks the top-level CCA status bit, combines enabled edge-event bits and active level bits, and dispatches all pending child interrupts through the gpio IRQ domain.

## State And Persistence
Hardware registers hold data, output enable, event/level polarity, masks, and top-level interrupt enable. The driver keeps no shadow state; it uses the spinlock for interrupt register RMW operations. Remove clears the top-level GPIO interrupt enable bit.

## Dependencies And Integration Points
Uses gpiolib generic MMIO, shared IRQ registration, simple child IRQ domains, OF compatible `brcm,iproc-gpio-cca`, and optional `ngpios` device-tree property.

## Risks And Edge Cases
The parent IRQ is shared and requested directly, so the handler must return `IRQ_NONE` when no GPIO status is present. Edge ack writes to the event status register only for edge-triggered lines. Level status is synthesized from input data XOR polarity and mask bits. Concurrent type/mask/ack changes are protected by a spinlock but normal GPIO generic operations may also touch nearby registers.

## Test Signals
Probe with and without IRQ resource, custom `ngpios`, shared IRQ no-status path, edge rising/falling ack and polarity programming, level high/low status synthesis, mask/unmask register changes, and top-level interrupt disable on remove.
