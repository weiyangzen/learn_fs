<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c

### Purpose
`irq-msc01.c` supports the MIPS SOC-it MSC01 interrupt controller. It maps the controller registers, configures edge or level IRQ lines, dispatches vector interrupts, and optionally binds EIC vectors.

### Important APIs, Types, And Functions
Public functions are `ll_msc_irq()` and `init_msc_irqs()`. Important callbacks are `mask_msc_irq()`, `unmask_msc_irq()`, `level_mask_and_ack_msc_irq()`, `edge_mask_and_ack_msc_irq()`, and `msc_bind_eic_interrupt()`. Two IRQ chips are defined: `msc_levelirq_type` and `msc_edgeirq_type`.

### Control Flow
Initialization maps the controller, resets it, installs `board_bind_eic_interrupt`, loops over a board-provided `msc_irqmap_t` array, sets chip/handler type, configures edge or level support registers, records `irq_base`, and enables interrupt generation. Runtime dispatch reads `MSC01_IC_VEC`, converts valid vectors below 64 to Linux IRQs, and calls `do_IRQ()`.

### State, Persistence, And Dependencies
State includes `_icctrl_msc`, macro-derived register addresses, global `irq_base`, controller registers, and board EIC binding callback. The code depends on `ioremap`, `asm/msc01_ic.h`, `cpu_has_veic`, IRQ core, and board-provided interrupt maps.

### Integration Points
This file is called by board-specific arch init code for SOC-it systems. It integrates with EIC/VEIC modes, the generic IRQ subsystem, and platform interrupt dispatch.

### Risks
The code uses direct volatile register pointers rather than accessor wrappers, and the edge clear path differs for VEIC versus non-VEIC. The `MSC01_IC_SUP + irq * 8` expression uses the full Linux IRQ in the VEIC edge clear path, so the register map and base assumptions must match board usage.

### Test Signals
Test edge and level sources, VEIC and non-VEIC configurations, EOI behavior, spurious vector handling, and board map entries that cover low and high interrupt banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c -->
