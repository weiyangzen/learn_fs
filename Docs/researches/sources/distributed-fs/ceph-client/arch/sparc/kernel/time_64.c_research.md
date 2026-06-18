# sources/distributed-fs/ceph-client/arch/sparc/kernel/time_64.c

Purpose: implements sparc64 tick/STICK/Hummingbird timer operations, clocksource and clockevent registration, scheduler clock, delay loops, RTC platform registration, CPU-frequency clock tick scaling, and timer IRQ handling.

Important APIs/types/functions: `tick_ops`, operation sets `tick_operations`, `stick_operations`, and `hbtick_operations`; `time_init_early()`, `time_init()`, `setup_sparc64_timer()`, `timer_interrupt()`, `sparc64_next_event()`, `sched_clock()`, `read_current_timer()`, `__delay()`, `udelay()`, `sparc64_get_clock_tick()`, cpufreq notifier, and RTC probes for CMOS, BQ4802, Mostek, sun4v, and Starfire.

Control flow: early init chooses `%tick`, `%stick`, or Hummingbird I/O STICK based on `tlb_type` and CPU version, initializes frequency, offset, and VDSO mode, then patches `get_tick` instruction sequences. Full init registers the clocksource, computes clockevent limits, and initializes this CPU's tick hardware. Per-CPU timer setup disables interrupt/protection bits with interrupts masked, copies the template clockevent, and registers it. Timer IRQ clears the appropriate softint, accounts IRQ0, and calls the per-CPU event handler. RTC init chooses Starfire or sun4v synthetic RTCs, otherwise probes OF RTC/Mostek/BQ4802 devices.

State and persistence: runtime state includes `tick_operations`, `sparc64_events`, `tb_ticks_per_usec`, `cmos_regs`, RTC platform resources, per-CPU frequency reference tables, and CPU `clock_tick` scaling. Persistent clock contents are handled by RTC drivers.

Dependencies and integration points: depends on SPARC tick/STICK registers, sun4v restrictions, Open Firmware frequencies/resources, clocksource/clockevents, VDSO clock modes, cpufreq, RTC drivers, Starfire detection, and SMP setup in `smp_64.c`.

Risks: tick compare writes have CPU errata workarounds and must execute at aligned sites. sun4v forbids writing tick/STICK. Hummingbird I/O STICK reads/writes need rollover-safe sequences. `sparc64_next_event()` currently calls `tick_operations.add_compare` instead of `tick_ops`, so alternate operation selection should be reviewed carefully.

Test signals: boot on Spitfire, Hummingbird, Cheetah/STICK, and sun4v; clocksource/VDSO mode selection; timer interrupt delivery on all CPUs; cpufreq transitions scaling `clock_tick`; `udelay` accuracy; RTC device registration; sched_clock monotonicity; and oneshot timer programming near minimum/maximum deltas.
