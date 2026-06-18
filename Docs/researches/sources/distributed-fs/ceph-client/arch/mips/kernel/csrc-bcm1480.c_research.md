<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c

### Purpose
This file registers the BCM1480 ZBbus cycle counter as a 64-bit clocksource and sched_clock.

### Important APIs, Types, And Functions
It defines `bcm1480_hpt_read()`, exported object `bcm1480_clocksource`, `sb1480_read_sched_clock()`, and initializer `sb1480_clocksource_init()`.

### Control Flow
Initialization reads PLL divider from system config, derives ZBbus frequency in 25/50 MHz increments, registers the clocksource at that rate, and registers a 64-bit sched_clock reader.

### State, Persistence, And Dependencies
State is the SCD ZBbus cycle counter and clocksource registration. Dependencies are BCM1480/SB1250 register macros, raw MMIO, clocksource, sched_clock, and MIPS time setup.

### Integration Points
BCM1480 platform time init uses this as the continuous time source, paired with BCM1480 timer clockevents for interrupts.

### Risks
Frequency derivation assumes system configuration encoding and reference rate. Raw 64-bit reads must be safe on the target bus.

### Test Signals
Clocksource registration, monotonicity, sched_clock stability, frequency calibration against external time, and wrap handling are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-bcm1480.c -->
