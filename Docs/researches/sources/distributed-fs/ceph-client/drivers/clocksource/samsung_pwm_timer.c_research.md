# sources/distributed-fs/ceph-client/drivers/clocksource/samsung_pwm_timer.c

Purpose: uses Samsung PWM timer channels as a clocksource, sched_clock, and clockevent provider for S3C/S5P-era SoCs. It chooses two PWM channels not reserved for external PWM outputs.

Important APIs, types, and functions: `struct samsung_pwm_clocksource` stores base, IRQs, variant data, chosen event/source channels, prescaler/divider values, and timer clock. Shared helpers include `samsung_timer_set_prescale()`, `samsung_timer_set_divisor()`, `samsung_time_stop()`, `samsung_time_setup()`, `samsung_time_start()`, `samsung_set_next_event()`, `samsung_set_periodic()`, `samsung_clock_event_isr()`, `samsung_clockevent_init()`, `samsung_clocksource_init()`, and `_samsung_pwm_clocksource_init()`. `samsung_pwm_lock` is exported for coordination with PWM users.

Control flow: DT init allocates variant data, parses IRQs and `samsung,pwm-outputs`, maps registers, obtains the `timers` clock, selects the highest-numbered non-output channel for source and the next for event, enables resources, registers the event device, then initializes the source timer and registers sched_clock/clocksource. Legacy board code can call `samsung_pwm_clocksource_init()` directly.

State and persistence: global `pwm` holds singleton state. Timer control registers are protected by `samsung_pwm_lock`. Suspend/resume callbacks stop or reprogram the source and event channels. There is no dynamic removal path for early timer setup.

Dependencies and integration points: integrates with OF timer declarations, common clock framework, clockevents, clocksource, sched_clock, Samsung PWM variant data, and the exported lock used by other Samsung PWM code.

Risks: channel selection must not conflict with output PWM channels. TCON bit layout has channel-specific gaps and channel 4 autoreload differences. `TINT_CSTAT` handling varies by variant. Test signals include correct source/event channel selection on each compatible, no PWM output conflicts, clocksource wrap behavior for 16-bit and 32-bit variants, interrupt clearing, and suspend/resume reprogramming.
