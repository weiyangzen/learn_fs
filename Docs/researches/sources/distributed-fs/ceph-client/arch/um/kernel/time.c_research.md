# sources/distributed-fs/ceph-client/arch/um/kernel/time.c

## Purpose
Implements UML clocksource, clockevent, timer IRQ handling, persistent clock, and optional time-travel simulation modes. It supports normal host POSIX timers, basic time skipping, infinite CPU simulation, and externally coordinated simulated time.

## Important APIs, Types, and Functions
Exports `time_travel_mode`, `time_travel_ndelay()`, `time_travel_add_irq_event()`, `__time_travel_wait_readable()`, and `__time_travel_propagate_time()`. Key internals include `time_travel_ext_req()`, `time_travel_handle_message()`, event-list management, `timer_handler()`, `itimer_*` clockevent callbacks, `timer_read()`, `um_setup_timer()`, `time_init()`, and boot options `time-travel`/`time-travel-start=`.

## Control Flow, State, and Persistence
Time-travel state persists in globals: current simulated ns, start time, event lists, IRQ-delivery list, external scheduler fd, shared-memory scheduler pointers, sequence numbers, pending broadcasts, and timer interval/next event. Clock events schedule either host timers or simulated events; simulated reads may advance time and deliver pending events. External mode exchanges request/wait/update/get/broadcast messages and may share current/free-until time through mapped scheduler shared memory.

## Dependencies and Integration Points
Integrates Linux clockevents/clocksource, IRQ `TIMER_IRQ`, host timer wrappers in `os-Linux/time.c`, signal delivery through `deliver_alarm()`, time-travel-aware virtio/IRQ code, sysfs broadcast control, and suspend idle sleep.

## Risks and Test Signals
Risks include backwards time panics, external protocol sequence mismatches, event-list recursion, IRQ delivery while disabled, and starvation in infinite CPU mode. Test all time-travel modes, external scheduler disconnects, periodic/oneshot timers, idle sleep, broadcast sysfs, suspend, and workloads that poll time in loops.
