<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c

## Purpose
Initializes OMAP1 timer infrastructure, preferring the 32 kHz timer when available and falling back to MPU timers for clockevents, clocksource, and sched_clock.

## Important APIs, Types, and Functions
Defines `omap1_timer_init()` plus MPU timer clockevent/clocksource helpers under `CONFIG_OMAP_MPU_TIMER`.

## Control Flow
`omap1_timer_init()` initializes OMAP1 clocks and mux, calls `omap_32k_timer_init()`, and falls back to `omap_mpu_timer_init()` on failure. MPU timer init gets `ck_ref`, halves its rate for PTV, configures timer1 as clockevent with IRQ `INT_TIMER1`, and timer2 as a free-running down-count clocksource and sched_clock.

## State and Persistence Behavior
Static clockevent structure persists after registration. Hardware state includes MPU timer control/load registers and requested timer IRQ.

## Dependencies and Integration Points
Depends on clock framework, clockevents/clocksource/sched_clock, `omap_32k_timer_init()`, IRQ macros, and `omap1_clk_init()`/`omap1_mux_init()`.

## Risks
A missing `ck_ref` triggers `BUG_ON`. Incorrect rate division skews timekeeping. If neither 32k nor MPU timer works, boot timekeeping fails.

## Test Signals
Boot with 32k timer available and unavailable, verify clocksource selection, tick interrupts, oneshot/periodic modes, and stable sched_clock. Run timer interrupt and delay calibration checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c -->
