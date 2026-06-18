<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c

## Purpose
Implements the NXP i.MX GPCv2 interrupt mask/wakeup controller as a hierarchical irqchip above a parent GIC domain, mainly to control wake sources and per-core interrupt mask registers.

## Important APIs, Types, And Functions
`struct gpcv2_irqchip_data` stores the raw spinlock, MMIO base, wakeup source masks, saved IRQ masks, and selected wakeup CPU register offset. Important functions are `imx_gpcv2_irqchip_init()`, `imx_gpcv2_domain_alloc()`, `imx_gpcv2_irq_mask()`, `imx_gpcv2_irq_unmask()`, `imx_gpcv2_irq_set_wake()`, `gpcv2_wakeup_source_save()`, and `gpcv2_wakeup_source_restore()`.

## Control Flow
OF init requires a parent domain, matches the compatible to a 2-core or 4-core layout, maps registers, creates a 128-entry hierarchical domain, masks all per-core interrupts, selects CORE0 as default wake CPU, applies the GPR interrupt workaround, registers syscore suspend/resume, and clears OF populated state so the GPC power-domain driver can bind later. Child allocations copy the fwspec to the parent after installing the GPCv2 chip data.

## State And Persistence
Wakeup source masks are kept in `wakeup_sources[]`, where clearing a bit enables wake. Suspend saves current IMR registers and replaces them with wake masks; resume restores saved run-time masks. Normal mask/unmask updates the GPC IMR and then delegates to the parent IRQ chip.

## Dependencies And Integration Points
It depends on OF irq init, parent irqdomains, syscore ops, GIC parent callbacks, and compatibles `fsl,imx7d-gpc` and `fsl,imx8mq-gpc`. It integrates with the i.MX power-domain driver by clearing `OF_POPULATED` and resetting fwnode initialized state.

## Risks
Wake mask polarity is inverted and easy to regress. The hard-coded GPR interrupt workaround keeps IRQ 32 unmasked in run mode. The single global `imx_gpcv2_instance` means only one instance is supported by syscore save/restore. Parent translation rejects PPIs.

## Test Signals
Test boot with i.MX7D/i.MX8MQ DTs, hierarchy allocation under GIC, normal mask/unmask, wake-source programming across suspend/resume, GPR interrupt behavior, power-domain driver later binding, and invalid SPI numbers beyond 128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-gpcv2.c -->
