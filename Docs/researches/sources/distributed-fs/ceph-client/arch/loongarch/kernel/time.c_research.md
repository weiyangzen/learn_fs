## sources/distributed-fs/ceph-client/arch/loongarch/kernel/time.c

### Purpose
`time.c` provides LoongArch constant-counter clocksource, per-CPU clockevent, scheduler clock, timer IRQ handling, counter synchronization, and paravirtual time initialization.

### Important APIs, Types, And Functions
Exported globals are `cpu_clock_freq` and `const_clock_freq`. Important functions include `constant_clockevent_init`, `constant_clocksource_init`, `time_init`, `save_counter`, `sync_counter`, `constant_timer_interrupt`, timer state callbacks, `constant_timer_next_event`, `read_const_counter`, and `sched_clock_read`.

### Control Flow
`time_init` chooses constant-counter frequency from CPUCFG or CPU clock, computes initial counter offset, registers the local clockevent and clocksource, and initializes PV time. Clockevent init maps/request the per-CPU timer IRQ once, configures each CPU's `clock_event_device`, syncs the counter, sets `lpj_fine`, and installs cpuhp callbacks that enable timer interrupts on AP start and clear pending interrupts on death. Timer IRQ clears CSR timer interrupt and calls the clockevent handler.

### State, Persistence, And Dependencies
Persistent state includes global frequencies, `init_offset`, per-CPU clockevent devices, timer IRQ installation flags, CSR timer config, and registered clocksource/sched_clock. Dependencies include LoongArch CSRs, CPUCFG constant frequency calculation, generic clockchips/clocksource, cpuhp, and paravirt time.

### Integration Points
`setup.c`/CPU probe populate CPU clock data; `smp.c` calls `sync_counter` and AP clockevent init. Scheduler, timers, VDSO timekeeping, and delay loops consume the registered clocksource/event devices.

### Risks
`timer_irq_installed` and `irq` are static shared state in `constant_clockevent_init`; the first CPU must initialize before APs. Counter synchronization assumes writing `CNTC` with `init_offset` gives a common zero base. Min/max delta must match hardware timer bit width. Periodic mode divides by `HZ` and masks into CSR field.

### Test Signals
Boot timing, clocksource selection, timer interrupts on all CPUs, CPU hotplug, high-resolution timers, periodic/oneshot modes, sched_clock monotonicity, VDSO clock mode, and KVM steal-time interaction are key signals.
