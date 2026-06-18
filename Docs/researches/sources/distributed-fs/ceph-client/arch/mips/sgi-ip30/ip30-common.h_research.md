# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-common.h

Purpose: shared IP30 constants and declarations for HEART interrupt lines and SMP/per-CPU hooks.

Important APIs and control flow: it defines power, HEART L0/L1/L2/timer/error CPU IRQ numbers and declares `ip30_install_ipi()`, `ip30_smp_ops`, and `ip30_per_cpu_init()`.

State, persistence, and integration: no state is stored; it provides the internal contract between IP30 IRQ, setup, timer, and SMP code. Dependencies include HEART interrupt definitions and MIPS CPU IRQ base. Risks are hard-coded interrupt-line mapping and tight compile-time coupling. Test signals are compile-time consistency and correct IRQ numbers in boot logs/interrupt tables.
