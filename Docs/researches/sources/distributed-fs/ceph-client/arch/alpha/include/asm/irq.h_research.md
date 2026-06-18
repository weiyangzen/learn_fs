# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irq.h

This header defines Alpha IRQ count limits and IRQ canonicalization. `NR_IRQS` is selected by platform config, ranging from 16 on small systems to `32768 + 16` for Marvel, with generic kernels using an upper bound unless legacy start address excludes large platforms.

`irq_canonicalize` maps IRQ 2 to IRQ 9 for old PC-compatible serial/ISA behavior. The header also declares `perf_irq`, a performance interrupt hook taking a vector and pt_regs.

State is compile-time IRQ table sizing and an external performance IRQ callback. Integration is with `hw_irq.h`, machine-vector actual IRQ counts, platform interrupt controllers, and legacy drivers. Risks are static array over/under-sizing, generic upper-bound memory cost, and old ISA IRQ alias assumptions. Test signals are interrupt controller init, device IRQ mapping, and perf interrupt delivery.
