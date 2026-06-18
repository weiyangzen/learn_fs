# sources/distributed-fs/ceph-client/arch/alpha/kernel/time.c

## Purpose
Alpha clocksource, clockevent, RTC timer, QEMU virtual timer, IRQ work, and CPU cycle-frequency calibration code. The source was read as part of `subset-b-000628` and contains 463 lines.

## Important APIs, Types, and Functions
Exports `rtc_lock`, defines `est_cycle_freq`, `arch_irq_work_raise`, `rtc_timer_interrupt`, `common_init_rtc`, `time_init`, and SMP `init_clockevent`. Internal APIs include `rpcc`, per-CPU `cpu_ce`, RTC/QEMU clockevent setup, `qemu_cs`, `clocksource_rpcc`, `validate_cc_value`, `calibrate_cc_with_pit`, and `rpcc_after_update_in_progress`.

## Control Flow
Normal boot calibrates RPCC via PIT or CMOS update windows, validates against CPU-family bounds, compares with HWRPB `cycle_freq`, registers RPCC as a clocksource on single-CPU non-WTINT builds, initializes the platform RTC, and registers a periodic RTC clockevent. QEMU boots instead register a QEMU clocksource, one-shot alarm clockevent, and QEMU timer IRQ. Timer interrupts call the clockevent handler and drain pending irq_work.

## State and Persistence Behavior
Persistent runtime state includes `rtc_lock`, `est_cycle_freq`, per-CPU `clock_event_device` instances, optional per-CPU `irq_work_pending`, RTC CMOS frequency/control registers, PIT channels, QEMU alarm state, and registered clocksource/clockevent objects.

## Dependencies
Depends on RTC CMOS macros, PIT I/O ports, Alpha HWRPB, `__builtin_alpha_rpcc`, clocksource/clockchips core, IRQ work, profile/interrupt infrastructure, and platform hooks `alpha_mv.init_rtc` and `init_rtc_irq`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Cycle calibration is sensitive to broken PIT/RTC hardware, CPU-family bounds, SMP RPCC skew, and WTINT stopping counters. Wrong RTC frequency programming breaks scheduler ticks. QEMU and hardware paths have different clockevent modes.

## Test Signals
Boot Alpha hardware and QEMU, inspect registered clocksource/clockevent, verify jiffies/timer interrupts advance at `CONFIG_HZ`, test irq_work execution from timer interrupt, compare calibrated frequency with HWRPB, and run timekeeping drift tests.
