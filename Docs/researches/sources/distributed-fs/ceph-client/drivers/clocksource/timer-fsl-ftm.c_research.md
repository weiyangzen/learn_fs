# sources/distributed-fs/ceph-client/drivers/clocksource/timer-fsl-ftm.c

Purpose: supports Freescale FlexTimer Module hardware using separate FTM instances for a 16-bit clocksource/sched_clock and a periodic/one-shot clockevent. It supports big-endian register access via DT.

Important APIs, types, and functions: `struct ftm_clock_device` stores source/event bases, periodic cycles, prescaler, and endian mode. Important helpers are `ftm_readl()/ftm_writel()`, `ftm_counter_enable()/disable()`, `ftm_irq_acknowledge()/enable()/disable()`, `ftm_reset_counter()`, `ftm_set_next_event()`, `ftm_evt_interrupt()`, `ftm_clockevent_init()`, `ftm_clocksource_init()`, clock setup helpers, `ftm_calc_closest_round_cyc()`, and `ftm_timer_init()`.

Control flow: DT init allocates singleton `priv`, maps event and source register ranges, parses IRQ, reads `big-endian`, enables four named clocks for event/source counter and FTM modules, computes a prescaler so `periodic_cyc` fits in 16 bits, initializes the source, initializes the event, and returns. Source setup programs CNTIN/MOD, resets the counter, registers sched_clock and an up-count MMIO clocksource, then enables the counter. Event setup initializes CNTIN/MOD, resets, requests IRQ, registers the clockevent, and enables the counter. One-shot programming disables the counter, resets, writes `MOD = delta - 1`, starts counting, and enables TOF interrupt.

State and persistence: global `priv` and the hardware registers hold all state. The prescaler value is used by both source and event timers. There is no persistent storage or successful-remove path.

Dependencies and integration points: uses OF clock names, FTM register definitions in `linux/fsl/ftm.h`, clocksource MMIO helpers, sched_clock, clockevents, and IRQF_IRQPOLL.

Risks: prescaler calculation increments `ps` while testing, so off-by-one changes can corrupt event rate. Endianness must match hardware. `delta - 1` underflows if clockevents passes zero. Test signals include big- and little-endian boot, 16-bit clocksource registration, periodic rate accuracy, one-shot shutdown after IRQ, and correct named-clock availability.
