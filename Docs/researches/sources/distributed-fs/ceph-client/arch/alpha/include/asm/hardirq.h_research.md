# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hardirq.h

This header declares Alpha's `ack_bad_irq` hook and then includes generic hardirq definitions. It defines `ack_bad_irq` so generic code uses the arch-provided implementation for unexpected interrupts.

State is generic hardirq per-CPU accounting plus any logging/counting in the implementation elsewhere. Risks are minimal; the key integration point is ensuring bad IRQs are acknowledged in a platform-appropriate way. Test signals are interrupt-controller build coverage and spurious IRQ handling.
