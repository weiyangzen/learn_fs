# sources/distributed-fs/ceph-client/arch/m68k/hp300/time.c

Purpose: implements HP300 timer interrupt and clocksource support for m68k. It programs the platform timer, handles periodic ticks, maintains a monotonic tick count, and registers a continuous clocksource.

Important APIs/types/functions: key functions are `hp300_sched_init`, interrupt handler `hp300_tick`, and clocksource read callback `hp300_read_clk`. Static state includes `hp300_clk`, `clk_total`, and `clk_offset`. Hardware constants describe timer registers under `CLOCKBASE`.

Control flow: `hp300_sched_init` resets the clock chip, writes `INTVAL`, requests `IRQ_AUTO_6` as `"timer tick"`, enables timer interrupts, and registers the clocksource at 250 kHz. `hp300_tick` acknowledges status, reads the timer latch with `movpw`, adds `INTVAL` to `clk_total`, clears `clk_offset`, calls `legacy_timer_tick(1)`, drives heartbeat, restores interrupts, and turns off network/SCSI LEDs. `hp300_read_clk` atomically reads MSB/LSB/MSB until stable, accounts for a pending timer interrupt by setting `clk_offset`, and returns total elapsed timer ticks.

State and persistence: runtime-only state is `clk_total` plus `clk_offset`, protected by disabling local interrupts. Hardware timer registers persist only as programmed device state during boot.

Dependencies/integration: depends on Linux clocksource, IRQ, legacy m68k timer hooks, `timer_heartbeat`, `blinken_leds`, `in_8/out_8`, and HP300 auto-vector IRQ 6. `config.c` installs `hp300_sched_init` into `mach_sched_init`.

Risks: timekeeping depends on stable multi-byte timer reads and pending-interrupt detection; races can produce jitter if `clk_offset` is wrong. `request_irq` failure only logs an error, but the clocksource is still registered. Inline `movpw` and fixed addresses are HP300-specific.

Test signals: boot timer initialization, IRQ delivery at `HZ`, clocksource monotonicity across counter rollover and pending interrupts, LED clearing side effect, behavior when `request_irq` fails, and calibration at `HP300_TIMER_CLOCK_FREQ`.
