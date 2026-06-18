<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c

## Purpose
Implements the NXP i.MX INTMUX interrupt multiplexer, where each channel accepts 32 sources and emits one parent interrupt.

## Important APIs, Types, And Functions
`struct intmux_data` stores the MMIO base, IPG clock, channel count, lock, and per-channel `struct intmux_irqchip_data`. Per-channel data stores saved enable register, channel index, parent IRQ, and irqdomain. Important functions are `imx_intmux_probe()`, `imx_intmux_irq_handler()`, `imx_intmux_irq_map()`, `imx_intmux_irq_select()`, `imx_intmux_irq_mask()`, `imx_intmux_irq_unmask()`, runtime suspend, and runtime resume.

## Control Flow
Probe counts platform IRQs to determine channels, maps registers, enables the IPG clock, creates one 32-entry linear domain per channel using the same fwnode but a `select()` callback that chooses by channel index, disables all sources, chains each channel parent IRQ, then enables runtime PM. The chained handler reads `CHANIPR(channel)` and dispatches all pending source bits into that channel's domain.

## State And Persistence
Each channel enable register `CHANIER` is the main hardware state. Runtime suspend saves `CHANIER` for every channel and disables the IPG clock; resume re-enables the clock and restores saved enables. No pending state is persisted.

## Dependencies And Integration Points
It depends on platform IRQ resources, OF IRQ parsing, clocks, runtime PM, chained IRQs, and `fsl,imx-intmux`. The irqdomain `select()` logic integrates with `interrupts-extended` style lookups where the second cell is the channel index.

## Risks
Channel count comes from platform IRQ count and is limited to 8. The code creates multiple domains with the same fwnode, so selection by `param[1]` is essential. Error unwinding does not remove already-created domains in all partial failure paths, so probe failures after some channels are initialized deserve testing.

## Test Signals
Test all channel parent IRQs, source masking/unmasking, fwspec selection by channel, runtime PM suspend/resume restoring `CHANIER`, clock failure paths, and DTs with 1 to 8 channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-imx-intmux.c -->
