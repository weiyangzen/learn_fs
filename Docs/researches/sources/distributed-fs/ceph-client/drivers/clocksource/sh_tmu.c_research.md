# sources/distributed-fs/ceph-client/drivers/clocksource/sh_tmu.c

Purpose: implements the SuperH/Renesas Timer Unit as both a down-counting clocksource and a periodic/one-shot clockevent provider, usually using channel 0 for events and channel 1 for source.

Important APIs, types, and functions: `enum sh_tmu_model` distinguishes SH3 register layout from the normal layout. `struct sh_tmu_channel` contains channel base, IRQ, periodic value, clockevent, clocksource, enable count, and source-enabled flag. Key functions are `sh_tmu_read()/write()`, `sh_tmu_start_stop_ch()`, `sh_tmu_enable()/disable()`, `sh_tmu_set_next()`, `sh_tmu_interrupt()`, clocksource read/enable/suspend/resume, clockevent state/next callbacks, `sh_tmu_channel_setup()`, and `sh_tmu_setup()`.

Control flow: probe enables runtime PM, parses DT channel count or platform data, prepares/enables `fck`, computes `rate = clk / 4`, maps memory, allocates channels, registers channel 0 as clockevent and channel 1 as clocksource. Clockevent registration configures both periodic and oneshot callbacks and requests the channel IRQ. The source enables the channel lazily and reads inverted `TCNT`. For an event, `sh_tmu_set_next()` stops the channel, acknowledges status, enables interrupt, programs reload/count, and restarts.

State and persistence: state is per channel and in hardware TCOR/TCNT/TCR/TSTR registers. `enable_count` allows a channel to remain enabled when shared by source/event contexts or across suspend handling. No disk persistence exists.

Dependencies and integration points: integrates with platform/OF, early SuperH platform timers, PM runtime/genpd, common clock framework, clocksource, clockevents, and IRQ core.

Risks: register offsets differ for SH3 versus standard TMU. Enable-count correctness is critical to avoid disabling a clocksource still in use. The clocksource is a down-counter and must stay programmed with max timeout. Test signals include channel assignment, one-shot and periodic event behavior, clocksource monotonicity, PM suspend/resume with enable_count preserved, valid `#renesas,channels`, and earlytimer retention.
