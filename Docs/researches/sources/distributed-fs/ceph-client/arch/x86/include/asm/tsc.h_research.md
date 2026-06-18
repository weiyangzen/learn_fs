# sources/distributed-fs/ceph-client/arch/x86/include/asm/tsc.h

Purpose: declares and inlines x86 timestamp counter access, calibration, reliability, synchronization, and scheduler-clock helpers.

Important APIs/types/functions: `rdtsc()`, `rdtsc_ordered()`, `cycles_t`, `get_cycles()`, `cpu_khz`, `tsc_khz`, `disable_TSC()`, `tsc_early_init()`, `tsc_init()`, `mark_tsc_unstable()`, `unsynchronized_tsc()`, `check_tsc_unstable()`, `native_calibrate_cpu_early()`, `native_calibrate_tsc()`, `native_sched_clock_from_tsc()`, TSC adjust verification helpers, suspend/resume sched-clock state helpers, and `cpu_khz_from_msr()`.

Control flow: `rdtsc()` emits raw unordered RDTSC. `rdtsc_ordered()` uses alternatives to prefer `lfence; rdtsc` or `rdtscp` based on CPU features. `get_cycles()` returns 0 if TSC is unavailable in non-TSC builds, otherwise raw cycles. Boot and resume code use the extern initialization/synchronization helpers.

State/persistence: timing state lives in extern frequency globals, reliability flags, and TSC adjust/async-reset state. The header itself only declares accessors and low-level inline assembly reads.

Dependencies/integration: depends on asm alternative/cpufeature/MSR/processor support. Integrated with clocksource, sched_clock, delay calibration, tracing, and CPU synchronization checks.

Risks/test signals: ordering, feature alternatives, and TSC synchronization affect time monotonicity and scheduler/trace timestamps. Test on CPUs with/without RDTSCP/LFENCE_RDTSC, multi-socket systems, suspend/resume, CPU hotplug, `notsc`, clocksource watchdog, and sched_clock monotonicity checks.
