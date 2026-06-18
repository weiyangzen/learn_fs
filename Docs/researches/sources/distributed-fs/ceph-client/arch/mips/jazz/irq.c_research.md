<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c

### Purpose
`irq.c` implements Jazz interrupt initialization, R4030 local interrupt masking, platform IRQ dispatch, and the R4030 periodic clock event.

### Important APIs, Types, And Functions
Important functions and objects are `enable_r4030_irq()`, `disable_r4030_irq()`, `r4030_irq_type`, `init_r4030_ints()`, `arch_init_irq()`, `plat_irq_dispatch()`, `r4030_clockevent`, `r4030_timer_interrupt()`, and `plat_time_init()`.

### Control Flow
Boot maps fixed wired TLB entries for Jazz I/O, initializes i8259 CPU IRQs and R4030 IRQ chips, clears pending R4030 sources, and enables CPU interrupt lines. Runtime dispatch prioritizes timer IRQ4, EISA IRQ2, then R4030 local IRQ1. Timer initialization registers a periodic-only clock event and programs the R4030 interval for 100 Hz.

### State, Persistence, And Dependencies
Mutable state is R4030 enable/source registers, CPU status interrupt masks, wired TLB mappings, and the registered clockevent. The spinlock protects R4030 mask changes.

### Integration Points
It integrates MIPS generic IRQ entry, i8259, R4030 hardware registers, `setup_pit_timer()`, Jazz constants, and the generic clockevents layer.

### Risks
The file assumes `HZ == 100`, hard-coded wired mappings, and fixed interrupt priority. An empty local IRQ source panics, so spurious R4030 local interrupts are fatal.

### Test Signals
Boot Jazz, verify wired mappings, timer ticks, EISA interrupt ack, R4030 device IRQ enable/disable, and PIT registration. Stress interrupt masking under concurrent device IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/irq.c -->
