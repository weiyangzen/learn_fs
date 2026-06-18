# sources/distributed-fs/ceph-client/arch/m68k/coldfire/sltimers.c

Purpose: Slice Timer based system tick, clocksource, and optional high-frequency profiler for ColdFire parts with SLT hardware.

Important APIs and data: optional `mcfslt_profile_tick()` and `mcfslt_profile_init()` under `CONFIG_HIGHPROFILE`; `mcfslt_tick()`, `mcfslt_read_clk()`, `mcfslt_clk`, and `hw_timer_init()`.

Control flow and state: `hw_timer_init()` computes cycles per jiffy from `MCF_BUSCLK`, writes `STCNT` with `n - 1`, starts timer 0 with run/interrupt/timer enable bits, initializes `mcfslt_cnt`, requests the timer IRQ, registers the clocksource, and optionally starts timer 1 as profiler. The tick handler clears BE/TE status bits, advances `mcfslt_cnt`, and calls `legacy_timer_tick(1)`. Clock reads account for pending TE by adding one jiffy and rereading the down-counter.

Dependencies and integration: legacy m68k timer path, Linux clocksource/profile APIs, IRQ core, and slice timer registers. SoC BSPs assign this through `mach_sched_init`.

Risks and test signals: down-counter off-by-one handling is explicitly documented; changing it can skew time. Pending TE read logic is sensitive to races. Test jiffies rate, clocksource monotonicity across pending interrupts, profiler IRQ, and failed request_irq logging.
