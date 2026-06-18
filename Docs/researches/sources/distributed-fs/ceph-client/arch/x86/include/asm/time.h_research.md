<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h

Purpose: declares x86 timer initialization interfaces. Important APIs are `hpet_time_init()`, `pit_timer_init()`, and `global_clock_event`.

Control flow: boot timekeeping selects and initializes HPET/PIT clock event sources; generic clockevent code uses `global_clock_event`. State is clockevent device state and hardware timer configuration. Dependencies include HPET, PIT/RTC, and generic clocksource/clockevent subsystems.

Risks include boot hangs from missing timer interrupts, wrong fallback from HPET to PIT, and clockevent misregistration. Test signals include boot timer initialization, no-HPET systems, PIT fallback, suspend/resume timekeeping, and clocksource watchdog output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h -->
