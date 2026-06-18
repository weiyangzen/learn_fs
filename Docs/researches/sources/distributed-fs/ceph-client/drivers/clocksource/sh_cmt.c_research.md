# sources/distributed-fs/ceph-client/drivers/clocksource/sh_cmt.c

Purpose: implements Renesas/SuperH Compare Match Timer variants as clockevent and clocksource providers. It covers 16-bit, 32-bit, 48-bit, and R-Car Gen2/3/4 CMT layouts with shared or per-channel start/stop registers.

Important APIs, types, and functions: `struct sh_cmt_info` describes model width, channel mask, overflow bits, and accessors; `struct sh_cmt_channel` holds channel MMIO, match values, flags, locks, clockevent, clocksource, and cycle extension state; `struct sh_cmt_device` stores platform resources, clock rate, and channel array. Key routines include register accessors, `sh_cmt_get_counter()`, `sh_cmt_enable()/disable()`, `sh_cmt_clock_event_program_verify()`, `sh_cmt_interrupt()`, clocksource enable/read/suspend/resume, clockevent state/next callbacks, and `sh_cmt_setup()`.

Control flow: platform probe enables runtime PM, resolves model data from OF or platform data, prepares/enables `fck`, computes the effective timer rate, maps registers, allocates channels, and assigns channel 0 to clockevents and channel 1 to clocksource, or one channel to both if only one exists. Clockevent registration requests per-channel IRQs. Clocksource registration uses an enable callback, so hardware starts only when selected. Interrupts clear status, extend total cycles for single-channel source mode, run the clockevent handler unless skipped, and reprogram compare values under lock.

State and persistence: state is held in channel flags, `match_value`, `next_match_value`, `total_cycles`, `cs_enabled`, runtime PM/syscore markings, and hardware compare/counter/control registers. No disk persistence exists. Single-channel mode uses software cycle extension across compare wraps.

Dependencies and integration points: integrates with platform/OF matching, early platform timers on SuperH, PM runtime/genpd, common clock framework, IRQ core, clocksource, clockevents, and R-Car channel clock enable registers.

Risks: compare reprogramming is race-prone because hardware can wrap while software changes CMCOR; the `FLAG_REPROGRAM` and `FLAG_SKIPEVENT` logic is safety-critical. Register width, channel masks, real hardware indexes, and R-Car `CMCLKE` handling vary by model. Test signals include event and source registration on each model, one-channel and two-channel configurations, no missed one-shot deadlines under stress, suspend/resume with genpd, and correct behavior as earlytimer and normal platform driver.
