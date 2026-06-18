# sources/distributed-fs/ceph-client/drivers/sh/intc/balancing.c

Purpose: optional support for SH-X3 hardware-managed interrupt auto-distribution.

Important APIs and functions: `intc_set_dist_handle` records a per-IRQ distribution register handle derived by `intc_dist_data`. `intc_balancing_enable` and `intc_balancing_disable` write the distribution bit when IRQ balancing is not globally disabled for that IRQ.

Control flow: during controller registration, the core calls `intc_set_dist_handle` after normal mask/ack setup. Later, `intc_enable` enables distribution after unmasking, and `intc_disable` disables distribution before masking.

State and dependencies: global `dist_handle[INTC_NR_IRQS]` stores encoded handles. Dependencies include mask register descriptors with `dist_reg`, the INTC register dispatch tables, `irq_balancing_disabled`, SMP-capable SH-X3 hardware, and `intc_big_lock` during setup. Risks are silently absent distribution handles, hardware-specific semantics, interaction with CPU affinity, and wrong register width/field index. Test signals are SMP boot with `CONFIG_INTC_BALANCING`, expected distribution register writes on IRQ enable/disable, and no balancing writes for IRQs lacking `dist_reg`.
