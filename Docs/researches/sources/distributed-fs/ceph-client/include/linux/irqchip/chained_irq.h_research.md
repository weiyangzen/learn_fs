# sources/distributed-fs/ceph-client/include/linux/irqchip/chained_irq.h

## Purpose
`chained_irq.h` provides common entry and exit helpers for chained interrupt handlers whose parent chip may use either fasteoi or level-triggered mask/ack flow control.

## Important APIs, types, and functions
It defines `chained_irq_enter(struct irq_chip *chip, struct irq_desc *desc)` and `chained_irq_exit(struct irq_chip *chip, struct irq_desc *desc)`.

## Control flow
On entry, FastEOI chips need no action. Other chips use `irq_mask_ack` if available, otherwise mask then ack. On exit, FastEOI chips call `irq_eoi`; other chips unmask the parent line.

## State and persistence
No state is owned by the header; it mutates parent IRQ chip hardware state through callbacks.

## Dependencies and integration points
It depends on `linux/irq.h` and is used by GPIO and secondary interrupt controllers chained under a parent IRQ.

## Risks and test signals
Risks include passing a chip lacking needed callbacks, double masking/eoi, and wrong parent descriptor. Tests should cover fasteoi and level parent chips, nested child interrupt storms, and teardown while the chained line is active.
