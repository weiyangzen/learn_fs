<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c

## Purpose
Implements the i.MX IRQSTEER block, which steers many input interrupts through a smaller set of output interrupts, with optional channel-control support and runtime PM.

## Important APIs, Types, And Functions
`struct irqsteer_data` stores registers, IPG clock, output IRQs, register count, selected channel, domain, saved masks, and device-type quirks. Important functions are `imx_irqsteer_probe()`, `imx_irqsteer_irq_handler()`, `imx_irqsteer_irq_mask()`, `imx_irqsteer_irq_unmask()`, `imx_irqsteer_get_hwirq_base()`, `imx_irqsteer_save_regs()`, and `imx_irqsteer_restore_regs()`.

## Control Flow
Probe reads `fsl,num-irqs` and `fsl,channel`, maps registers, enables the clock, optionally writes `CHANCTRL`, creates a linear domain covering all sources, and chains one output IRQ per 64 input interrupts. Runtime dispatch determines which output fired, reads two 32-bit `CHANSTATUS` registers for that output range, and dispatches each pending source.

## State And Persistence
Mask state is held in the hardware `CHANMASK` register set and mirrored into `saved_reg[]` during PM. Suspend saves all mask registers and disables the IPG clock; resume re-enables the clock, rewrites `CHANCTRL` when supported, and restores masks. Bus lock/unlock uses runtime PM around IRQ chip register access.

## Dependencies And Integration Points
It depends on platform devices, OF properties, clocks, runtime PM, generic irqdomains, chained IRQs, and compatibles `fsl,imx-irqsteer` and `nxp,s32n79-irqsteer`. GPIO or peripheral child controllers can sit below this domain.

## Risks
The reverse register-index calculation is easy to break because hwirqs are mapped from the high register down. Output IRQ count is `DIV_ROUND_UP(num_irqs, 64)` and must not exceed 15. Some SoCs lack `CHANCTRL`, controlled by a quirk. Runtime PM must keep the clock enabled across mask/unmask access.

## Test Signals
Test source delivery across 32-bit register boundaries and 64-source output boundaries, channel-control and no-channel-control SoCs, runtime PM register access, suspend/resume state restoration, child GPIO irqchips, and invalid `fsl,num-irqs` or missing output IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-irqsteer.c -->
