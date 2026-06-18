# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-2.c

Purpose: interrupt controller support for ColdFire parts with 56 programmable plus 7 fixed edge-port interrupts, optionally across two controllers.

Important APIs and data: `intc_irq_mask()`, `intc_irq_unmask()`, `intc_irq_ack()`, `intc_irq_startup()`, `intc_irq_set_type()`, `intc_irq_chip`, `intc_irq_chip_edge_port`, and `init_IRQ()`. `intc_intpri` assigns decreasing level/priority values to vectors when first started.

Control flow and state: `init_IRQ()` masks all sources by setting IMRL mask-all bit, then installs chips and level handlers for `MCFINT_VECBASE..NR_VECS`. Startup lazily programs an ICR byte if unset, configures edge-port lines as inputs and interrupt sources, and unmasks the IRQ. Edge-port ack writes the corresponding EPFR bit. Type changes program EPPAR and switch to `handle_edge_irq` for edge modes.

Dependencies and integration: Linux IRQ core, ColdFire INTC/edge-port registers, vector base definitions, and `do_IRQ()` from entry assembly. Hardware mask bits and priority registers are the only mutable state.

Risks and test signals: vector-to-controller arithmetic must match SoC layout. The shared `intc_intpri--` can underflow if many interrupts start, though priority uniqueness is the intent. Edge-port type writes assume IRQs in EINT range. Test by requesting internal and edge-port IRQs, toggling edge polarities, validating mask/unmask registers, and confirming no spurious mask-all behavior.
