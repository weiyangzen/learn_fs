<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h

Purpose: Provides a minimal placeholder `struct irq_alloc_info` for SGI SN IRQ allocation interfaces.

Important APIs/types/functions: `struct irq_alloc_info { };`.

Control flow: Code can pass or declare IRQ allocation metadata uniformly even when this architecture variant has no fields.

State and persistence: No state is represented in this empty structure.

Dependencies and integration points: Integrated by IRQ allocation call sites that need an architecture-specific type.

Risks: Adding fields changes API expectations and may require initializer changes across IRQ setup code.

Test signals: Build coverage for SN IRQ allocation paths is sufficient.

Source read size: 11 lines, 199 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h -->
