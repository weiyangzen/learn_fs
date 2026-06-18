<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c

### Purpose
This file implements per-CPU clockevent devices using SiByte SB1250 general-purpose timers.

### Important APIs, Types, And Functions
Key functions are `sibyte_shutdown()`, `sibyte_set_periodic()`, `sibyte_next_event()`, `sibyte_counter_handler()`, and `sb1250_clockevent_init()`, with per-CPU clockevent/name storage.

### Control Flow
Initialization assigns timer IRQ `K_INT_TIMER_0 + cpu`, rejects CPUs above 2 because timer 3 is reserved for the high-precision clocksource, registers the clockevent, maps timer interrupts to IP4, unmasks, sets affinity, and requests the IRQ. Runtime mode setters program timer config/init registers.

### State, Persistence, And Dependencies
State includes SCD timer registers, interrupt mapper registers, per-CPU clockevent storage, and IRQ affinity. Dependencies are SB1250 register definitions, raw MMIO, and clockevents.

### Integration Points
SB1250 platform time setup uses this for CPU-local ticks while `csrc-sb1250.c` uses timer 3 as a clocksource.

### Risks
Only CPUs 0-2 may use event timers. Request IRQ failures are logged after registration. Timer frequency and IP mapping must match board wiring.

### Test Signals
SB1250 boot, per-CPU periodic/oneshot ticks, IRQ affinity and mapping validation, and coexistence with timer-3 clocksource are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-sb1250.c -->
