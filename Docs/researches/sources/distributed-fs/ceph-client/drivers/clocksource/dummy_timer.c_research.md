# sources/distributed-fs/ceph-client/drivers/clocksource/dummy_timer.c

Purpose: registers per-CPU dummy clockevent devices for systems that need tick broadcast infrastructure without a real local timer.

Important APIs/types/functions: per-CPU `dummy_timer_evt`, `dummy_timer_starting_cpu()`, and `dummy_timer_register()`.

Control flow: an `early_initcall` installs a CPU hotplug state. On each CPU start, the driver initializes a `CLOCK_EVT_FEAT_DUMMY` clockevent with periodic and oneshot feature bits and registers it.

State and persistence: per-CPU `clock_event_device` objects persist statically.

Dependencies and integration points: depends on clockevents and CPU hotplug; built when `ARCH_HAS_TICK_BROADCAST` selects the object.

Risks: this is not a hardware timer and cannot generate interrupts; it is only valid when another broadcast mechanism supplies real ticks. Misuse as a primary timer would stall time events.

Test signals: CPU hotplug registration, tick broadcast behavior on platforms without local timers, and clockevent framework listings showing dummy devices.
