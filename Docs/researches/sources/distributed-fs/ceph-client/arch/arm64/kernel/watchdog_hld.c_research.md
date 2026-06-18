## sources/distributed-fs/ceph-client/arch/arm64/kernel/watchdog_hld.c

### Purpose
`watchdog_hld.c` provides ARM64 hard-lockup detector integration using perf/NMI PMU events and cpufreq-aware period adjustment.

### Important APIs, Types, And Functions
It defines `hw_nmi_get_sample_period`, `arch_perf_nmi_is_available`, `watchdog_perf_update_period`, `watchdog_freq_notifier_callback`, and `init_watchdog_freq_notifier`.

### Control Flow
The sample period is computed from the CPU hardware max frequency times `watchdog_thresh`, falling back to a safe 5 GHz estimate when cpufreq data is unavailable. Initialization only advertises perf NMI availability if ARM PMU interrupts are true NMIs. When a cpufreq policy appears, each online CPU in the policy updates its perf watchdog period through `smp_call_on_cpu`.

### State, Persistence, And Dependencies
State is cpufreq notifier registration and perf hardlockup event period updates. No persistent storage is used.

### Integration Points
Connects generic hardlockup detector, cpufreq policy notifications, ARM PMU NMI capability, and per-CPU smp calls.

### Risks
If PMU interrupts are not NMIs, the detector cannot catch hard IRQ-disabled lockups. Missing cpufreq data makes the fallback period conservative and may delay detection on slow CPUs. Policy creation races with event creation are handled by per-CPU updates but remain timing-sensitive.

### Test Signals
Boot with pseudo-NMI PMU support on/off, verify watchdog availability, create cpufreq policies after watchdog start, test CPU hotplug, and inject hard lockups to confirm NMI delivery and expected timeout.
