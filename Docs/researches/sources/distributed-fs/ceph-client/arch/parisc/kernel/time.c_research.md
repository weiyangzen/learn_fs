<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c

### Purpose
`time.c` provides PA-RISC timer interrupt handling, clockevent/clocksource setup, sched_clock from CR16, persistent clock access, profile PC adjustment, and optional generic RTC support.

### Important APIs, Types, And Functions
Important state includes `cr16_clock_freq`, `clocktick`, `time_keeper_id`, and per-cpu `parisc_clockevent_device`. Main functions are `timer_interrupt()`, `parisc_timer_next_event()`, `parisc_clockevent_init()`, `profile_pc()`, `read_persistent_clock64()`, `read_cr16_sched_clock()`, `read_cr16()`, and `time_init()`.

### Control Flow
Timer interrupts reprogram periodic events and call the clockevent handler. Clockevent init configures per-CPU oneshot/periodic devices backed by CR16. `time_init()` derives CR16 frequency from PAGE0's 10ms calibration, registers sched_clock, clockevents, optional PAT 64-bit counter discovery, and the CR16 clocksource. RTC support proxies PDC TOD read/set through a platform `rtc-generic` device.

### State, Persistence, And Dependencies
Clock frequency, tick delta, timekeeper CPU, per-CPU clockevent devices, clocksource registration, and optional RTC platform device persist. Dependencies include PDC TOD/PAT calls, PAGE0, generic clockevents/clocksources, RTC core, and SMP CPU IDs.

### Integration Points
Used by IRQ timer handling, scheduler clock, profiling, CPU hotplug, and persistent clock initialization.

### Risks
CR16 is per-CPU, so hotplug and migration-sensitive timing need care. PDC TOD set has a 32-bit seconds limitation. `parisc_find_64bit_counter()` only logs discovery and does not register that counter.

### Test Signals
Boot clocksource selection, periodic and oneshot timer interrupts, high-resolution timers, CPU hotplug timer init, RTC read/set including invalid dates, and profiling around nullified instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c -->
