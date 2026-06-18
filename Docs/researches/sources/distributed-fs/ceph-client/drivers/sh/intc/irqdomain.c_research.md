# sources/distributed-fs/ceph-client/drivers/sh/intc/irqdomain.c

Purpose: IRQ domain support for SH INTC vectored interrupts.

Important APIs and functions: `intc_evt_xlate` translates a firmware/device-tree interrupt specifier into a Linux hardware IRQ using `evt2irq` and sets type to `IRQ_TYPE_NONE`. `intc_irq_domain_init` chooses a linear domain when vector-derived IRQs start at zero and are contiguous; otherwise it creates a tree domain.

Control flow: controller registration calls `intc_irq_domain_init` before associating each IRQ with its domain. Device tree or other domain users can then translate vector specifiers through the domain ops.

State and dependencies: state is the `irq_domain` pointer stored in `intc_desc_int`. Dependencies include IRQ domain APIs, `evt2irq`, and hardware vector ordering in `intc_hw_desc`. Risks are `BUG_ON` if domain allocation fails, wrong linear-domain selection when vectors are sparse, and type information not propagated beyond `IRQ_TYPE_NONE`. Test signals are successful domain creation, association for every vector, xlate of event-vector cells, and boot on sparse/non-zero IRQ bases.
