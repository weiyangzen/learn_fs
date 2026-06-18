<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c

## Purpose
Implements the Ingenic JZ47xx/X1000 Timer Counter Unit interrupt controller, exposing timer channel interrupts through a regmap-backed generic irqchip and one or more parent IRQs.

## Important APIs, Types, And Functions
`struct ingenic_tcu` stores the regmap, domain, and up to three parent IRQs. `ingenic_tcu_irq_init()` creates the domain and generic chip. `ingenic_tcu_intc_cascade()` reads flag and mask registers and dispatches unmasked timer bits. Custom generic-chip callbacks handle TCU write-one-to-clear, mask, unmask, and mask-ack register semantics.

## Control Flow
OF init obtains the syscon regmap from the node, counts parent interrupts, creates a 32-entry domain, allocates one generic chip, programs disable/enable/ack registers, masks all channels by default, then registers the same cascade handler on every parent IRQ because different SoCs route subsets of timers differently.

## State And Persistence
The regmap and generic chip hold mask cache and hardware register access. All TCU IRQs are masked at init. No PM callbacks are present; wake handling is skipped with `IRQCHIP_SKIP_SET_WAKE` while `IRQCHIP_MASK_ON_SUSPEND` masks the lines on suspend.

## Dependencies And Integration Points
It depends on MFD/syscon regmap lookup, Ingenic TCU register definitions, OF IRQ parsing, generic irqchip, and compatibles `ingenic,jz4740-tcu`, `jz4725b-tcu`, `jz4760-tcu`, `jz4770-tcu`, and `x1000-tcu`.

## Risks
Multiple parent IRQs share one domain and handler; an incorrect DT parent list can drop channels. The custom callbacks update `mask_cache` with unusual polarity because TCU mask clear enables interrupts. Missing regmap access errors are not checked in the fast path.

## Test Signals
Test each compatible's parent IRQ topology, timer channel interrupt delivery, mask/unmask/ack behavior, all-IRQ masking at init, and invalid `interrupts` property counts greater than three.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ingenic-tcu.c -->
