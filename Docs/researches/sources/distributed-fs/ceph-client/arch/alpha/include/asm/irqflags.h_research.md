# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irqflags.h

This header implements Alpha local interrupt flag operations using PAL processor status/IPL helpers. It defines IPL levels from minimum through machine check, optionally replaces `IPL_MIN` for broken IRQ masks, and wraps `rdps`, `swpipl`, and `setipl`.

Important APIs are `arch_local_save_flags`, `arch_local_irq_disable`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, and `arch_irqs_disabled`. Disable/save raise IPL to `IPL_MAX`; enable restores `IPL_MIN`; restore sets the saved IPL.

State is processor IPL. Integration is spinlocks, interrupt entry/exit, DMA locking, and HAE updates. Risks include treating saved flags as raw IPL, broken-mask platform minimums, and missing compiler barriers around PAL operations. Tests are interrupt nesting, spinlock IRQ save/restore, and platform IRQ enable behavior.
