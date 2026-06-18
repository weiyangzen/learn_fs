# sources/distributed-fs/ceph-client/arch/m68k/68000/timers.c

Purpose: hardware timer and simple RTC support for 68328-family non-MMU systems.

Important functions are `hw_timer_init()`, `hw_tick()`, `m68328_read_clk()`, and `m68328_hwclk()`. Compile-time board choices select clock source, prescaler, and `TICKS_PER_JIFFY`: Dragen2 uses SYSCLK with a large count, Xcopilot has a workaround path, and the default uses the 32 kHz clock.

Control flow: `hw_timer_init()` disables timer 1, requests `TMR_IRQ_NUM` with `IRQF_TIMER`, programs `TCTL`, `TPRER`, and `TCMP`, enables the timer, and registers the `m68328_clk` clocksource. `hw_tick()` acknowledges timer status by clearing `TSTAT`, advances `m68328_tick_cnt`, and calls `legacy_timer_tick(1)`. `m68328_read_clk()` returns the accumulated tick count plus current `TCN` under local IRQ protection.

State is the hardware timer register set and the software accumulator `m68328_tick_cnt`. `m68328_hwclk()` reads `RTCTIME` into a fixed date of 1901-01-01 plus hour/min/sec; setting is ignored.

Dependencies include DragonBall timer/RTC register macros from `MC68VZ328.h`, generic clocksource and IRQ APIs, and machine hooks installed by `m68328.c`. Integration is the architecture `mach_sched_init` and `mach_hwclk` contract.

Risks and test signals: inaccurate prescaler/compare constants distort timekeeping, and failure to request the timer IRQ leaves the system without scheduler ticks. Test with boot logs for timer IRQ request errors, monotonic clocksource reads, `jiffies` advancement, and board-specific HZ timing checks.
