# sources/distributed-fs/ceph-client/arch/parisc/include/asm/irqflags.h

Purpose: implements PA-RISC local interrupt enable/disable/save/restore primitives.

Important APIs/types/functions: exports raw local IRQ helpers around control register or PSW interrupt bits, consumed by generic `local_irq_*` APIs.

Control flow: callers save current flags, disable interrupts for critical sections, and restore the prior state; low-level assembly manipulates PA-RISC interrupt mask state.

State and persistence: CPU-local interrupt-enable state persists until changed. Dependencies and integration: used by spinlocks, atomics, scheduler, interrupt entry/exit, and tracing.

Risks and test signals: incorrect flag restoration deadlocks or permits reentrancy. Test with lockdep, IRQ-off tracing, timer interrupt stress, and nested critical sections.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
