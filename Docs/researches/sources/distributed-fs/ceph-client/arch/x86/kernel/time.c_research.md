# sources/distributed-fs/ceph-client/arch/x86/kernel/time.c

## Purpose
`time.c` contains x86 legacy timer initialization glue, profiling PC extraction, late time initialization, and VDSO clocksource sanity checks.

## Important APIs, Types, And Functions
Public functions are `profile_pc()`, `hpet_time_init()`, `time_init()`, and `clocksource_arch_init()`. Internals include `timer_interrupt()`, `setup_default_timer_irq()`, and `x86_late_time_init()`.

## Control Flow
`time_init()` defers real setup through `late_time_init`. Late init selects interrupt mode, initializes platform timers, finalizes interrupt routing, initializes TSC, and enables TPAUSE delay on WAITPKG CPUs. HPET init falls back to PIT and registers IRQ0 for legacy timer or HPET legacy replacement. The timer interrupt invokes the global clock event handler.

## State, Persistence, Dependencies, Integration
State includes `late_time_init`, IRQ0 registration, `global_clock_event`, TSC/delay configuration, and clocksource VDSO mode. Dependencies include x86 init ops, HPET/PIT, clockevents, clocksource, interrupt routing, and CPU features. Generic timekeeping uses these arch hooks.

## Risks And Test Signals
Interrupt-mode ordering is critical around PIT/HPET. IRQ0 registration is needed even without PIT for HPET legacy mode. VDSO clocksources need a 64-bit mask. Test HPET/PIT combinations, PIC/IO-APIC modes, WAITPKG, VDSO and non-VDSO clocksources, bad clocksource masks, and IRQ0 delivery.
