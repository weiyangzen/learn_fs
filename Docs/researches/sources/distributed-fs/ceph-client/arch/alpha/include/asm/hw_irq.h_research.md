# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hw_irq.h

This header declares low-level Alpha interrupt counters and actual IRQ count selection. It exposes `irq_err_count`, per-CPU `irq_pmi_count`, and `ACTUAL_NR_IRQS`, which resolves to `alpha_mv.nr_irqs` for generic kernels or `NR_IRQS` for fixed-platform builds.

State is interrupt error/performance-monitor counters and platform vector configuration. Integration is with `machvec.h`, `irq.h`, and interrupt handling code. Risks include static array sizing versus actual platform IRQ count and generic-kernel machine-vector initialization. Tests are interrupt init, `/proc/interrupts` style accounting, and platform-specific IRQ routing.
