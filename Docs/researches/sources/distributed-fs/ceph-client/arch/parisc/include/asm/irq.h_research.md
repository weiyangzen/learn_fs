# sources/distributed-fs/ceph-client/arch/parisc/include/asm/irq.h

Purpose: defines PA-RISC interrupt numbering limits and architecture IRQ initialization hooks.

Important APIs/types/functions: declares IRQ count constants, `irq_canonicalize`, and architecture IRQ initialization/dispatch functions used by generic irq core.

Control flow: platform setup initializes interrupt controllers and maps firmware/device IRQs into Linux IRQ numbers; runtime handlers dispatch through generic irq_descs.

State and persistence: IRQ mappings and controller state persist after boot. Dependencies and integration: used by IOSAPIC, SuperIO, SMP IPI, and generic interrupt code.

Risks and test signals: IRQ-number mismatches cause lost or misdelivered interrupts. Test with timer, IPI, PCI device, and legacy IRQ delivery.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
