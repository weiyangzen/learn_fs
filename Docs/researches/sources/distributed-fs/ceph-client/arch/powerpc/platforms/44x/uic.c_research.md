<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c

Purpose: implements the IBM PPC4xx Universal Interrupt Controller irqchip and irq-domain support, including primary and cascaded UIC initialization and top-level interrupt retrieval.

Important APIs/types/functions: `struct uic` stores index, DCR base, lock, and irq domain; irqchip callbacks `uic_unmask_irq()`, `uic_mask_irq()`, `uic_ack_irq()`, `uic_mask_ack_irq()`, and `uic_set_irq_type()` manipulate UIC ER/SR/TR/PR registers; `uic_host_map()` maps hardware IRQs to Linux IRQs; `uic_irq_cascade()` handles secondary UIC interrupts; `uic_init_tree()` initializes primary and cascaded controllers; `uic_get_irq()` returns the mapped pending primary IRQ.

Control flow: initialization finds the top-level `ibm,uic` node by selecting an interrupt-controller without an `interrupts` property, initializes it, sets it as the default domain, then scans for cascaded UIC nodes with `interrupts`, maps their cascade IRQ, and installs chained handlers. Runtime top-level IRQ reads `UIC_MSR`, computes the source with `32 - ffs(msr)`, and finds the virq. Cascades mask/ack the parent, read child MSR, dispatch the child domain IRQ, then ack/unmask parent as appropriate.

State and persistence: global `primary_uic` persists the root controller. Each `struct uic` persists DCR base, lock, and irq domain. Hardware ER/SR/TR/PR/CR registers persist interrupt enable, status, trigger, polarity, and critical configuration.

Dependencies and integration: depends on OF `cell-index` and `dcr-reg`, DCR accessors, Linux irq domains/chained handlers, two-cell interrupt spec translation, and machine descriptors using `uic_init_tree()`/`uic_get_irq()`.

Risks and test signals: `uic_get_irq()` can compute an invalid source when MSR is zero; default `handle_level_irq()` is used for both edge and level; missing properties return NULL and can panic in tree init; level IRQ ack timing is special. Test primary/cascaded UIC boot, edge/level polarity configuration, spurious interrupts, interrupt storms, cascaded device interrupts, and DT property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c -->
