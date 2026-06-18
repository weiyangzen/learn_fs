# sources/distributed-fs/ceph-client/arch/m68k/coldfire/timers.c

Purpose: generic ColdFire hardware timer support using timer 1 for system tick/clocksource and optionally timer 2 for high-profile sampling.

Important APIs and data: `init_timer_irq()`, `mcftmr_tick()`, `mcftmr_read_clk()`, `mcftmr_clk`, `hw_timer_init()`, optional `coldfire_profile_tick()` and `coldfire_profile_init()`. `__raw_readtrr`/`__raw_writetrr` select 16-bit or 32-bit TRR access for newer parts.

Control flow and state: `hw_timer_init()` disables timer 1, computes cycles per jiffy from `MCF_BUSCLK/16`, writes TRR as `n - 1`, starts restart mode, registers the clocksource, programs interrupt priority/autovector mapping, requests the timer IRQ, and optionally initializes profiler timer 2. The tick handler clears TER flags, advances `mcftmr_cnt`, and calls `legacy_timer_tick(1)`. Clocksource reads `mcftmr_cnt + TCN`.

Dependencies and integration: legacy m68k timer path, IRQ core, clocksource API, old SIM interrupt registers, and BSP `mach_sched_init`.

Risks and test signals: timer width differs by SoC; wrong TRR access corrupts period. High-profile timer shares similar priority mapping. Test jiffy frequency, clocksource monotonicity, timer IRQ mapping, profiler IRQ, and 16/32-bit timer builds.
