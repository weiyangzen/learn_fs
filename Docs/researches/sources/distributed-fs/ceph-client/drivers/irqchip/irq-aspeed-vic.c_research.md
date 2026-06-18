# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-vic.c

Purpose: Implements the root Aspeed VIC for AST2400/AST2500 systems as a 64-source interrupt controller with top-level ARM IRQ handling.

Important APIs/types/functions: `struct aspeed_vic`, `vic_init_hw()`, `avic_handle_irq()`, `avic_ack_irq()`, `avic_mask_irq()`, `avic_unmask_irq()`, `avic_mask_ack_irq()`, `avic_map()`, and `avic_of_init()`.

Control flow: OF init rejects non-root/duplicate controllers, maps registers, allocates state, masks all sources, clears software triggers, selects IRQ mode, records which sources are edge-triggered from sense registers, clears edge latches, installs `set_handle_irq()`, and creates a simple IRQ domain. Runtime handling loops over low then high status registers, dispatching the first set pending bit until none remain.

State and persistence: Global `system_avic` points to the single controller. Per-controller state stores base, edge source masks for low/high banks, and the domain. Hardware enable, trigger, sense, and edge-latch state persists until explicitly changed.

Dependencies/integration: Uses OF, ARM exception IRQ hook, irqdomain, syscore-related includes, and generic edge/level handlers.

Risks and test signals: Test both 32-bit banks, firmware-provided sense configuration, edge latch clearing, duplicate-root rejection, and mixed edge/level source handling under interrupt load.
