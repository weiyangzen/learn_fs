## sources/distributed-fs/ceph-client/arch/mips/ralink/irq.c

### Purpose
This file implements the legacy Ralink interrupt controller path for non-GIC SoCs. It maps CPU interrupt lines, creates a 32-entry SoC interrupt domain, masks/unmasks INTC bits, dispatches cascaded interrupts, and exposes timer/perf IRQ mappings.

### Important APIs, Types, And Functions
State includes `rt_intc_regs[]`, `rt_intc_membase`, and `rt_perfcount_irq`. `ralink_intc_irq_unmask()`/`mask()` write enable/disable registers. `ralink_intc_irq_handler()` dispatches the first pending SoC IRQ from `STATUS0`. `plat_irq_dispatch()` handles MIPS IP7/IP5/IP6/IP4/IP2 priorities. `intc_map()` binds virqs to `ralink_intc_irq_chip`. `intc_of_init()` maps the controller, creates a legacy domain, enables global interrupts, and installs the chained handler. `arch_init_irq()` calls `of_irq_init()`.

### Control Flow
OF IRQ initialization first initializes the CPU interrupt controller, then the Ralink INTC node. The INTC setup optionally loads register offsets from DT, maps its parent IRQ, requests/remaps MMIO, disables all interrupts, routes all SoC interrupts to MIPS HW0, creates mappings, enables global INTC, chains the parent handler, and maps hwirq 9 for perf counters.

### State, Persistence, And Dependencies
Persistent state includes INTC MMIO mapping, IRQ domain, chip bindings, mask state, and performance IRQ. Dependencies include MIPS CPU IRQ code, OF address/IRQ parsing, irqdomain, and Ralink register layout.

### Integration Points
Device-tree interrupt specifiers use one-cell hwirq values under the Ralink INTC. MIPS timer code uses `get_c0_compare_int()` and perf uses `get_c0_perfcount_int()`.

### Risks
The chained handler dispatches only the least significant pending bit per parent interrupt; repeated entry must drain more. `request_mem_region()` failure logs but continues to ioremap. Priority in `plat_irq_dispatch()` is fixed and may starve lower-priority sources under storms.

### Test Signals
Validate each CPU interrupt line, multiple simultaneous INTC bits, mask/unmask behavior, DT custom register maps, perf counter IRQ, and spurious interrupt handling.
