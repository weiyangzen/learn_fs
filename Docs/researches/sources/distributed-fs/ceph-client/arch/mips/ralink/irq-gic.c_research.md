## sources/distributed-fs/ceph-client/arch/mips/ralink/irq-gic.c

### Purpose
This file provides IRQ initialization for Ralink platforms using the MIPS GIC, notably MT7621.

### Important APIs, Types, And Functions
`get_c0_perfcount_int()` returns `gic_get_c0_perfcount_int()` and is exported GPL. `arch_init_irq()` calls `irqchip_init()`.

### Control Flow
During architecture IRQ init, generic irqchip OF probing initializes CPU/GIC interrupt controllers. Performance-counter interrupt requests delegate to the GIC helper.

### State, Persistence, And Dependencies
No local state exists. Persistent IRQ domains are created by irqchip code. Dependencies include MIPS CPS/GIC support, OF irqchip data, and MIPS time/perf infrastructure.

### Integration Points
Selected under `CONFIG_MIPS_GIC` by the Ralink Makefile. It replaces the legacy Ralink INTC implementation.

### Risks
The platform depends entirely on DT-described irqchips. If GIC is not described or initialized, both device IRQs and performance counters fail.

### Test Signals
Boot MT7621 with GIC DT, validate timer/device interrupts, and confirm perf counter interrupt mapping.
