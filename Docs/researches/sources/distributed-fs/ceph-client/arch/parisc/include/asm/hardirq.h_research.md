# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardirq.h

Purpose: defines PA-RISC hard IRQ accounting and per-CPU interrupt state integration.

Important APIs/types/functions: provides `ack_bad_irq`, IRQ stack/accounting definitions, and includes generic hardirq helpers.

Control flow: low-level interrupt handlers update per-CPU counts and call generic interrupt dispatch; bad IRQs are reported through the architecture hook.

State and persistence: per-CPU IRQ counters and nesting state persist across interrupt handling. Dependencies and integration: used by irq core, `/proc/interrupts`, and PA-RISC interrupt entry code.

Risks and test signals: accounting mistakes hide interrupt storms or break preemption state. Test with timer/IPI/device interrupts and procfs interrupt count inspection.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
