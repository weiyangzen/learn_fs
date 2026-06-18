<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h

Purpose: declares x86 scheduler-clock and CPU-frequency time conversion helpers. Important APIs/types include `native_sched_clock()`, `recalibrate_cpu_khz()`, `no_timer_check`, `using_native_sched_clock()`, `paravirt_set_sched_clock()`, `cyc2ns_data`, `cyc2ns_read_begin()`, and `cyc2ns_read_end()`.

Control flow: sched_clock converts TSC cycles to nanoseconds using a linear equation that preserves continuity across frequency changes; paravirt can replace the sched_clock provider. State includes cycle-to-ns multiplier, shift, and offset data managed elsewhere.

Dependencies include TSC calibration, paravirt clock hooks, interrupt/timer code, and CPU frequency recalibration. Risks include non-monotonic sched_clock, bad frequency recalibration, and paravirt/native provider mismatch. Test signals include sched_clock monotonicity, CPU frequency changes, paravirt clocksource guests, timer watchdogs, and `no_timer_check` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h -->
