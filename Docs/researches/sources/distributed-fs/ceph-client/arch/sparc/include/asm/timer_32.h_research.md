# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_32.h

Purpose: SPARC32 timer header for SBUS clock constants, timer counter extraction, timer interrupt declaration, and per-CPU clockevent registration.

Important APIs/types/functions: functions/helpers `timer_value`, `timer_interrupt`, `register_percpu_ce`; macros/constants `_SPARC_TIMER_H`, `SBUS_CLOCK_RATE`, `TIMER_VALUE_SHIFT`, `TIMER_VALUE_MASK`, `TIMER_LIMIT_BIT`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TIMER_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, timekeeping paths rather than through standalone functions.

State and persistence behavior: State is in hardware timer registers supplied to `timer_value()` and per-CPU clockevent devices registered by platform code.

Dependencies and integration points: Includes/dependencies: `linux/clocksource.h`, `linux/irqreturn.h`, `asm-generic/percpu.h`, `asm/cpu_type.h`. Integration points include memory-management, SMP, timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Clocksource monotonicity, timer IRQ handling, sun4m/sun4d timer rate, and SMP per-CPU clockevents are signals.
