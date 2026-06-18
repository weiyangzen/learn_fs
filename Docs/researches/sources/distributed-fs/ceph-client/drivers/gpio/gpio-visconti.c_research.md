# sources/distributed-fs/ceph-client/drivers/gpio/gpio-visconti.c

## Purpose
Supports the Toshiba Visconti GPIO controller as a memory-mapped generic GPIO block with hierarchical interrupt forwarding to a parent interrupt controller.

## Important APIs, Types, And Functions
- `struct visconti_gpio` stores MMIO base, spinlock, generic GPIO chip, and device pointer.
- `gpio_generic_chip_init` supplies basic data, set, clear, and direction-output operations using `GPIO_IDATA`, `GPIO_OSET`, `GPIO_OCLR`, and `GPIO_DIR`.
- `visconti_gpio_irq_set_type` programs `GPIO_ODATA` and `GPIO_INTMODE` to model rising, falling, both-edge, and level triggers.
- `visconti_gpio_child_to_parent_hwirq` maps child GPIO IRQs 0-15 to parent hwirqs 24-39.
- `visconti_gpio_populate_parent_fwspec` builds the three-cell parent fwspec.
- `visconti_gpio_mask_irq`, `visconti_gpio_unmask_irq`, and `visconti_gpio_irq_chip` wrap parent IRQ masking with gpiolib IRQ resource tracking.

## Control Flow
Probe maps the GPIO register resource, locates the OF IRQ parent node and domain, initializes a generic GPIO chip, installs an immutable hierarchical irqchip, and registers the chip. IRQ type changes take the controller lock, adjust output-data/intmode bits used by the hardware interrupt logic, set the parent view to level-high where required, then delegate type programming to the parent chip.

## State And Persistence
Only hardware registers persist while powered: direction, output data, interrupt mode, and interrupt polarity emulation state. The driver keeps no software shadow beyond the spinlock and generic-chip structure.

## Dependencies And Integration Points
Uses OF IRQ parent discovery, parent IRQ domains, gpiolib generic MMIO helpers, hierarchical gpio irqchip callbacks, and the platform bus compatible `toshiba,gpio-tmpv7708`.

## Risks And Edge Cases
Only child interrupts 0-15 are mappable; higher GPIOs return `-EINVAL`. The driver maps low-level child interrupts by programming the parent as level-high and inverting controller data bits, so polarity handling is easy to regress. `irq_set_irq_type(offset, intc_type)` uses the offset as an IRQ number, which is a point to scrutinize against hierarchical parent semantics. Concurrent GPIO and IRQ register changes rely on a single spinlock.

## Test Signals
Validate GPIO data/set/clear/direction operations, IRQ mappings for child 0 and 15, failure for child 16, all supported IRQ trigger types, parent fwspec contents, and interrupt masking/unmasking order with `gpiochip_enable_irq` and parent mask calls.
