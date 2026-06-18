# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-simr.c

Purpose: interrupt-controller support for ColdFire parts with SIMR/CIMR mask/unmask registers, including M520x and M53xx-style one to three INTC units.

Important APIs and functions: `irq2ebit()`, `intc_irq_mask()`, `intc_irq_unmask()`, `intc_irq_ack()`, `intc_irq_startup()`, `intc_irq_set_type()`, `intc_irq_chip`, `intc_irq_chip_edge_port`, and `init_IRQ()`.

Control flow and state: mask/unmask choose controller 0, 1, or 2 by subtracting `MCFINT_VECBASE` and writing the local vector number to SIMR/CIMR. Startup enables edge-port lines when applicable, writes a priority value of 5 into the appropriate ICR byte, then unmasks. Type changes program edge-port polarity bits in EPPAR and switch edge IRQs to `handle_edge_irq`. Init masks all controllers, computes the IRQ span from available ICR bases, then installs chips and level handlers.

Dependencies and integration: Linux IRQ core and ColdFire INTC/edge-port register definitions. M520x has sparse edge-port mapping through `irqebitmap`; other parts map directly.

Risks and test signals: compile-time zero register addresses are used to optimize away absent controllers, so header accuracy matters. Edge-port range tests for M520x include compressed IRQ numbers, not physical line numbers. Test controller boundary IRQs at 63/64/127/128, edge-port IRQs, and type programming.
