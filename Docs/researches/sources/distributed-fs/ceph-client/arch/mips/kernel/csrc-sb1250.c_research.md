<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c

### Purpose
This file registers SiByte SB1250 timer 3 as a free-running high-precision clocksource and sched_clock.

### Important APIs, Types, And Functions
It defines `sb1250_hpt_get_cycles()`, `sb1250_hpt_read()`, exported `bcm1250_clocksource`, `sb1250_read_sched_clock()`, and `sb1250_clocksource_init()`.

### Control Flow
Initialization stops timer 3, loads its maximum counter value, starts it in continuous mode, registers the 23-bit clocksource at `V_SCD_TIMER_FREQ`, and registers a 23-bit sched_clock. Reads invert the down-counter into an increasing cycle value.

### State, Persistence, And Dependencies
State is SCD timer 3 registers and clocksource registration. Dependencies are SB1250 register macros, raw MMIO, clocksource, and sched_clock.

### Integration Points
SB1250 timekeeping uses timer 3 as a clocksource while CPUs use other timers for clockevents.

### Risks
Timer 3 is reserved here, so event code must not use it. The 23-bit width wraps quickly and depends on clocksource framework handling.

### Test Signals
Monotonic clocksource tests, sched_clock wrap tests, timer 3 reservation checks, and frequency validation against wall-clock time are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-sb1250.c -->
