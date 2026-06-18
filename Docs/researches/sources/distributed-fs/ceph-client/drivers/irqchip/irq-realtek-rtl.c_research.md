<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c

## Purpose
`irq-realtek-rtl.c` implements the cascaded interrupt controller used by Realtek RTL SoCs. It routes up to 32 SoC interrupt inputs onto a parent CPU interrupt and masks/demultiplexes them in software.

## Important APIs, Types, and Functions
Global state includes `realtek_ictl_base` and a raw spinlock. Routing helpers `IRR_OFFSET()`, `IRR_SHIFT()`, and `write_irr()` program the unusual reversed nibble layout in `IRR0` through `IRR3`. IRQ chip callbacks are `realtek_ictl_mask_irq()` and `realtek_ictl_unmask_irq()`. Domain mapping is `intc_map()`, chained dispatch is `realtek_irq_dispatch()`, and init is `realtek_rtl_of_init()`.

## Control Flow
Init maps MMIO, disables all inputs, clears routing for every source, finds the parent IRQ either from DT or by falling back to MIPS CPU IRQ 2, creates a 32-entry domain, and installs a chained handler. Mapping a child IRQ assigns the level handler and programs its routing value to output line 0. Dispatch reads `GIMR & GISR`, reports spurious if no pending bits exist, and dispatches each set input through the domain.

## State and Persistence
State is volatile: global interrupt mask, global status, and routing registers. The raw spinlock protects mask and routing read/modify/write sequences. No suspend/resume persistence is implemented.

## Dependencies and Integration Points
The driver depends on OF address/IRQ parsing, MIPS CPU interrupt fallback, chained IRQ handling, irqdomain one-cell translation, and `handle_level_irq`.

## Risks and Edge Cases
The route value is hard-coded to output 0 for all mapped sources, so platforms with different wiring need DT/driver changes. The fallback parent IRQ path assumes known hardware topology when DT lacks parent interrupts. Routing register indexing is inverted; mistakes there disconnect or misroute sources.

## Test Signals
Validate DT and fallback parent IRQ paths, all 32 input mappings, `GIMR` masking, spurious interrupt logging when status is empty, and correct IRR nibble programming for low and high hwirq numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c -->
