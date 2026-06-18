# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm-systimer.c

## Purpose

`timer-ti-dm-systimer.c` is the early system-timer driver for TI OMAP/AM/DM dual-mode timers. It selects suitable DMTimer instances from device tree, configures clockevent and optional clocksource roles, handles AM33xx/AM43 idle behavior, and provides a DRA7 per-CPU workaround for ARM architected timer erratum i940.

## APIs And Flow

`struct dmtimer_systimer` stores MMIO, revision-dependent offsets, clocks, and rate. `struct dmtimer_clockevent` and `struct dmtimer_clocksource` wrap clockevent/clocksource objects. Selection globals track the 32 kHz counter and chosen physical addresses. The first matched timer scans DT for preferred timers requiring `ti,no-reset-on-init`, `ti,no-idle`, assigned clock parents where needed, and no DSP/PWM role. It then initializes the matching node as clockevent, clocksource, DRA7 per-CPU timer, or ignores it.

Clockevent setup resets/enables the timer, sets posted mode for safe event use, requests IRQ, enables overflow/wakeup interrupts, and registers periodic/oneshot callbacks. Clocksource setup starts an autoreload free-running counter, registers sched_clock from the first such timer, and registers a clocksource.

## State, Dependencies, Risks, Tests

Chosen addresses persist in static globals; allocated clockevent/clocksource objects persist for kernel lifetime. AM33xx/AM43 callbacks disable/enable clocks and restore interrupt state. Dependencies include `timer-ti-dm.h`, `ti-sysc` bindings, OF scanning, assigned-clock defaults, common clocks, CPU hotplug, clockevents, clocksource, and sched_clock. Risks are DT omissions, picking DSP/PWM timers, revision-offset mistakes, pending-write loops, and SoC quirks. Test OMAP/AM/DM DTs with and without 32 kHz counter, oneshot/periodic ticks, CPU hotplug on DRA7, and suspend/resume on AM33xx/AM43.
