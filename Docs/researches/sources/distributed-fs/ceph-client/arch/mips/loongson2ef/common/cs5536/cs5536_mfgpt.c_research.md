# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_mfgpt.c

Purpose: implements CS5536 MFGPT0 timer as a periodic clock event and optional low-rated clocksource.

Important APIs/functions: exports `disable_mfgpt0_counter` and `enable_mfgpt0_counter`; defines `mfgpt_timer_set_periodic`, `mfgpt_timer_shutdown`, `timer_interrupt`, `setup_mfgpt0_timer`, `mfgpt_read`, `clocksource_mfgpt`, and `init_mfgpt_clocksource`.

Control flow: setup configures clockevent parameters, routes comparator 2 through interrupt mapper/gate, reads MFGPT base, registers the clockevent, and requests the timer IRQ. The IRQ handler refreshes variable base, acknowledges comparator status, and calls the event handler. The clocksource emulates a free-running counter from `jiffies * COMPARE + count`, clamping count if an underflow has not yet advanced jiffies.

State and persistence: raw spinlock protects timer access; static `mfgpt_base`, `old_count`, and `old_jifs` track hardware base and monotonic read smoothing. Hardware counter/setup registers persist timer mode.

Dependencies and integration: selected by `CONFIG_CS5536_MFGPT`; depends on CS5536 MSR/IO port definitions, clockevents, clocksource, jiffies, and IRQ framework.

Risks: oneshot mode is intentionally unsupported due to high deviation. Clocksource is not registered on SMP because MFGPT does not scale. Read function has side effects under seqlock retry, documented and lock-protected.

Test signals: periodic tick delivery, suspend/resume timer reenable, clocksource registration only on UP, CPUFreq/system time stability, and IRQ ack behavior.
