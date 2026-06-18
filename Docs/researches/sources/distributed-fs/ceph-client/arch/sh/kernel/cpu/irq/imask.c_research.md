<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c

Purpose: implements IRQ masking through the SR.IMASK priority field.

Important APIs/types/functions: `make_imask_irq()`, `mask_imask_irq()`, `unmask_imask_irq()`, `set_interrupt_registers()`.

Control flow: registers a level irq_chip; mask/unmask update a bitmap, compute current interrupt priority, and write SR IMASK using inline assembly.

State and persistence: state is `imask_mask`, `interrupt_priority`, and the CPU SR priority bits.

Dependencies/integration: integrates with generic irq_desc handling and SH external IRQ priority model.

Risks: not valid for level 15; priority computation is global and assembly-sensitive.

Test signals: test nested IRQ mask/unmask ordering, level IRQ handling, and CLI-ed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c -->
