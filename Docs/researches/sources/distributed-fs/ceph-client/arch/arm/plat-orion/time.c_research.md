# sources/distributed-fs/ceph-client/arch/arm/plat-orion/time.c

Purpose: Provides Orion SoC timekeeping using timer 0 as a free-running clocksource/sched_clock/delay source and timer 1 as the interrupt-driven clock event device.

Important functions/data: Static globals hold `bridge_base`, `bridge_timer1_clr_mask`, `timer_base`, and `ticks_per_jiffy`. `orion_read_sched_clock()` and `orion_delay_timer_read()` return the bitwise inverse of the down-counting timer 0 value. `orion_clkevt_next_event`, `orion_clkevt_shutdown`, and `orion_clkevt_set_periodic` implement clockevent operations. `orion_timer_interrupt()` ACKs timer1 and dispatches the event handler. Public `orion_time_set_base()` and `orion_time_init()` wire the platform in.

Control flow: Machine code sets the timer base, then calls `orion_time_init()` with bridge registers, IRQ, clear mask, and TCLK. Initialization computes ticks per jiffy, registers delay and sched_clock readers, programs timer0 to reload from `0xffffffff`, masks timer0 interrupts, initializes the MMIO clocksource, requests the timer1 IRQ, and registers the clockevent with min/max deltas. Clockevent programming masks/unmasks bridge interrupt bits and sets timer1 reload/value/control registers with local IRQs disabled.

State and persistence: Hardware timer control/value/reload and bridge interrupt cause/mask registers hold runtime state. The Linux clockevent structure persists globally. No spinlock is used; local IRQ masking protects register sequences on the boot CPU.

Dependencies/integration: Uses Linux clockchips, clocksource MMIO, sched_clock, interrupt APIs, and ARM delay timer registration. Depends on machine-provided TCLK and bridge clear semantics.

Risks/tests: `timer_base` must be set before init; otherwise early reads dereference NULL. A wrong `bridge_timer1_clr_mask` can fail to ACK interrupts. TCLK errors skew scheduler time and busy-wait delays. Tests should check clocksource monotonicity, periodic and oneshot events, interrupt ACK behavior, delay calibration, and boot on systems with different HZ/TCLK values.
