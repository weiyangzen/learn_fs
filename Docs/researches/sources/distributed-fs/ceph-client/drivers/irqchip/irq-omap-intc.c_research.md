<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c

### Purpose
`irq-omap-intc.c` implements the OMAP2/OMAP3/AM33xx INTC controller. It handles root IRQ dispatch, generic-chip allocation, legacy and linear irqdomain modes, context save/restore, and OMAP idle workarounds.

### Important APIs, Types, And Functions
Global state includes `domain`, `omap_irq_base`, `omap_nr_pending`, `omap_nr_irqs`, and saved `intc_context`. `intc_of_init()` selects 96 or 128 IRQ mode. `omap_intc_handle_irq()` reads `INTC_SIR` and dispatches active IRQs. `omap_alloc_gc_of()` and `omap_alloc_gc_legacy()` configure generic chips. Exported helpers include `omap_intc_save_context()`, `omap_intc_restore_context()`, `omap_irq_pending()`, and OMAP3 idle/suspend helpers.

### Control Flow
OF init sets controller size based on compatible, initializes either legacy domains for OMAP2/3 DMA compatibility or linear domains for newer SoCs, soft-resets the hardware, enables protection, and installs the exception handler. Generic chips use MIR clear/set registers for unmask/mask and `omap_mask_ack_irq()` for ack. Dispatch reads the sorted active IRQ register, detects spurious values, acknowledges spurious interrupts, otherwise handles the active IRQ through the domain.

### State, Persistence, And Dependencies
State includes saved sysconfig/protection/idle/threshold/ILR/MIR registers, mapped INTC base, domain mappings, and generic-chip mask caches. Dependencies include ARM exception handling, OF matching, legacy IRQ descriptor allocation, generic-chip helpers, and OMAP PM/idle callers.

### Integration Points
This is the root interrupt controller on supported OMAP families. PM code calls context and idle helpers, while older DMA code drives the legacy-domain decision.

### Risks
OMAP2/3 legacy mode is retained for DMA compatibility, so changing domain mode can break old platform code. Spurious IRQs are expected under posted-write timing and are only logged once. Context restore comments note MIRs are also saved/restored elsewhere, so PM ordering matters.

### Test Signals
Boot OMAP2/3 and AM33xx/DM81xx, validate 96 vs 128 IRQ sizing, legacy and OF linear domains, spurious SIR handling, mask/ack/unmask registers, context save/restore, idle workaround calls, and pending IRQ detection during suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c -->
