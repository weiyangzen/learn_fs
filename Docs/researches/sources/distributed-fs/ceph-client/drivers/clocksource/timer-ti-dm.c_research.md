# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm.c

## Purpose

`timer-ti-dm.c` is the runtime platform driver and exported API provider for TI OMAP dual-mode timers. It lets kernel clients reserve timers, configure clock sources, control counters and interrupts, and use PWM/capture features through `struct omap_dm_timer_ops`.

## APIs And Flow

`struct dmtimer` embeds the public cookie and stores IRQ, functional clock, revision-specific register bases, posted-write state, reservation flag, saved context, capabilities, errata, runtime-PM notifiers, and list node. `dmtimer_read()`/`dmtimer_write()` enforce posted-write pending checks encoded in register constants. Probe parses DT capabilities, maps resources, gets the functional clock, registers CPU PM and clock-rate notifiers, enables runtime PM, initializes non-reserved timers, and links into the global timer list. `_omap_dm_timer_request()` scans the list under spinlock and reserves by any timer, ID, capability, or node.

## State, Dependencies, Risks, Tests

Reservation lives in `timer->reserved`; runtime state uses `atomic_t enabled`; register context is saved/restored across runtime PM and CPU cluster PM for non-always-on timers. Errata i103/i767 forces non-posted mode. Dependencies include platform bus, OF matches, runtime PM, common clocks, CPU PM, OMAP1 support, and `dmtimer-omap` platform data. Risks are posted-mode regressions, reservation races, missing runtime-PM refs, context loss, capability mismatches, and PWM/capture side effects. Test request/free paths, PWM, interrupts, counter reads on errata SoCs, runtime suspend/resume, CPU cluster PM, clock-rate changes, and driver removal.
