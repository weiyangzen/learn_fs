# File Research: sources/cow-pools/bcachefs-tools/include/linux/irqflags.h

This header maps interrupt flag operations to user-space no-ops. `local_irq_save()` writes zero to the flags variable; restore/disable/enable do nothing.

It defines an `irqsave` cleanup guard with `DEFINE_LOCK_GUARD_0()`, allowing kernel code that uses guard-style IRQ sections to compile even though no hardware interrupt masking occurs.
