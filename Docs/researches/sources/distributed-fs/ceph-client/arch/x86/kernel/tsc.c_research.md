# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc.c

Purpose: implements x86 Time Stamp Counter discovery, calibration, scheduler-clock conversion, and clocksource registration. It decides whether the TSC can be used as a fast monotonic time source and maintains the global `cpu_khz` and `tsc_khz` values exported to other kernel code.

Important APIs/functions: `tsc_early_init()`, `tsc_init()`, `native_sched_clock()`, `native_sched_clock_from_tsc()`, `native_calibrate_tsc()`, `native_calibrate_cpu_early()`, `mark_tsc_unstable()`, `check_tsc_unstable()`, `unsynchronized_tsc()`, `recalibrate_cpu_khz()`, `tsc_save_sched_clock_state()`, and `tsc_restore_sched_clock_state()`. Internal helpers include PIT/HPET/PMTIMER calibration, CPUID crystal-clock decoding, ART detection, and per-CPU `cyc2ns` scaling.

Control flow: early boot checks for TSC, runs SNP secure TSC setup, derives frequency from CPUID, MSR, or quick PIT calibration, initializes `cyc2ns`, and enables the static branch used by `sched_clock`. Later `tsc_init()` retries calibration if needed, initializes secondary CPU conversion state, evaluates reliability and synchronization, registers an early TSC clocksource, and detects Always Running Timer metadata. `init_tsc_clocksource()` later replaces the early clocksource or schedules delayed refinement against HPET/PMTIMER. Watchdog callbacks can mark both TSC clocksources unstable.

State and persistence: state is mostly boot-lifetime global and per-CPU data: `cpu_khz`, `tsc_khz`, `tsc_unstable`, `tsc_clocksource_reliable`, `clocksource_tsc*`, delayed work state, `cyc2ns` latch data, ART base metadata, and suspend offset `cyc2ns_suspend`. Boot parameters `notsc`, `tsc=...`, and `tsc_early_khz=` influence persistent choices for the boot.

Dependencies and integration: integrates with x86 platform hooks from `x86_platform`, clocksource/timekeeping, sched_clock, vDSO clock mode, cpufreq notifiers, APIC deadline timers, HPET/PIT/PMTIMER, hypervisor and UV checks, TSC_ADJUST synchronization, SNP secure TSC, and topology/package logic.

Risks: calibration is sensitive to firmware, SMI latency, broken PIT/HPET/PM timers, virtualized timers, package topology, TSC_ADJUST firmware writes, cpufreq on SMP, and suspend/resume resets. Incorrect reliability decisions can break timekeeping, vDSO time, scheduler timestamps, and APIC timer calibration.

Test signals: boot logs for detected MHz, fast/refined calibration, watchdog instability, and TSC_ADJUST warnings are primary signals. Relevant validation includes booting SMP and suspend/resume systems, cpufreq changes, virtualized guests, systems without legacy PIC, and clocksource watchdog behavior.
