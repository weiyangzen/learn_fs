## sources/distributed-fs/ceph-client/arch/mips/ralink/Makefile

### Purpose
This Makefile selects common Ralink platform code, timer/IRQ implementation, SoC-specific identification files, early printk, and optional debugfs bootrom exposure.

### Important APIs, Types, And Functions
Base objects are `prom.o`, `of.o`, and `reset.o`. Non-GIC builds add `clk.o` and `timer.o`; GIC builds add `irq-gic.o` and `timer-gic.o`. Other selections include `ill_acc.o`, `irq.o`, SoC files, `early_printk.o`, and `bootrom.o`.

### Control Flow
Build-time control follows Kconfig. MT7621/GIC uses a different timer/IRQ path from older Ralink SoCs.

### State, Persistence, And Dependencies
No runtime state exists. Object inclusion determines which `arch_init_irq()`, `plat_time_init()`, and `prom_soc_init()` implementations are linked.

### Integration Points
The Makefile is the build dispatcher for the Ralink architecture directory.

### Risks
Conflicting selections could link duplicate architecture hooks, so Kconfig dependencies must keep INTC and GIC paths exclusive.

### Test Signals
Inspect linked objects for each SoC config and confirm no duplicate symbol errors across IRQ/timer variants.
