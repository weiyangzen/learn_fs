
# sources/distributed-fs/ceph-client/arch/x86/include/asm/clock_inlined.h

Purpose: tiny inlined clocksource and clockevent hooks for x86 TSC paths.

Important APIs and control flow: `arch_inlined_clocksource_read()` returns `rdtsc_ordered()`. `arch_inlined_clockevent_set_next_coupled()` writes the next deadline cycle to `MSR_IA32_TSC_DEADLINE`.

State, dependencies, and risks: state is hardware TSC and TSC-deadline MSR state. Dependencies include `asm/tsc.h`, MSR accessors, and clocksource/clockevent core expectations. Risks include using TSC before it is reliable, MSR writes on unsupported CPUs, and ordering assumptions around time reads. Test signals are timekeeping tests, clockevent programming, TSC deadline timer boot, and suspend/resume timing validation.
