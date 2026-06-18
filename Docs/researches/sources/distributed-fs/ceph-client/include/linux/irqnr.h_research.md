# sources/distributed-fs/ceph-client/include/linux/irqnr.h

## Purpose
`irqnr.h` exposes IRQ count/query helpers and iteration macros over descriptors, active IRQs, and numeric IRQ ranges.

## Important APIs, types, and functions
It declares `irq_get_nr_irqs`, `irq_set_nr_irqs`, `irq_to_desc`, and `irq_get_next_irq`, plus macros `for_each_irq_desc`, `for_each_irq_desc_reverse`, `for_each_active_irq`, and `for_each_irq_nr`.

## Control flow
Core and diagnostic code obtain the current IRQ upper bound, resolve descriptors by number, and iterate either all possible numbers, all descriptors, reverse descriptors, or active IRQs.

## State and persistence
The header declares accessors for global IRQ-number state but owns none itself.

## Dependencies and integration points
It depends on UAPI IRQ number definitions and integrates with generic IRQ descriptor storage, proc/debugfs iteration, and kexec/suspend code.

## Risks and test signals
Risks include unsigned/signed reverse iteration corner cases, sparse descriptor NULL handling, and stale upper-bound values. Tests should cover sparse IRQ configs, descriptor allocation beyond legacy IRQs, active IRQ iteration, and reverse iteration at zero.
