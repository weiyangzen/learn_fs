<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c

## Purpose
Implements the Imagination PowerDown Controller interrupt controller, exposing peripheral wake interrupts and syswake pins with wake routing, trigger programming, and chained parent IRQ handlers.

## Important APIs, Types, And Functions
`struct pdc_intc_priv` stores counts, peripheral IRQ array, shared syswake IRQ, irqdomain, MMIO base, cached `PDC_IRQ_ROUTE`, and a raw spinlock. Important functions are `pdc_intc_probe()`, `pdc_intc_setup()`, `perip_irq_mask()`, `perip_irq_unmask()`, `syswake_irq_set_type()`, `pdc_irq_set_wake()`, `pdc_intc_perip_isr()`, and `pdc_intc_syswake_isr()`.

## Control Flow
Probe reads `num-perips` and `num-syswakes`, maps peripheral parent IRQs plus one syswake parent IRQ, creates a 16-entry linear domain, allocates two generic chips with edge and level chip types for syswake sources, initializes routing with syswakes disabled, then chains all parent lines. Peripheral parent IRQs map one-to-one to hwirqs 0-7; the shared syswake parent reads status and enable registers and dispatches hwirqs 8-15.

## State And Persistence
The cached `irq_route` is persistent software state because the route register contains both mask and wake bits. Syswake trigger mode is programmed in per-pin registers and handler type is updated with `irq_setup_alt_chip()`. Wake enable state is propagated to destination parent IRQs using `irq_set_irq_wake()`.

## Dependencies And Integration Points
It depends on platform devices, OF properties, generic irqchip, chained IRQs, raw spinlocks, and compatible `img,pdc-intc`. It integrates with system suspend through IRQ wake flags and with peripheral/syswake consumers through the PDC irqdomain.

## Risks
Route register sharing makes generic cached mask callbacks unsafe for peripheral masks, hence custom locked route updates. `num-perips` and `num-syswakes` are capped at 8; bad DT counts fail probe. Wake routing must stay synchronized with destination parent wake state to preserve standby wake behavior.

## Test Signals
Validate DT count parsing, surplus peripheral IRQ rejection, edge and level syswake modes, wake enable/disable propagation, chained peripheral fan-out, shared syswake status masking, suspend wake from each source, and removal/domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imgpdc.c -->
