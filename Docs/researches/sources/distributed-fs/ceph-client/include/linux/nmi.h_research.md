# sources/distributed-fs/ceph-client/include/linux/nmi.h

Purpose: Declares lockup detector, hardlockup/NMI watchdog, softlockup touch, CPU backtrace, perf NMI, and stall-check interfaces with configuration-dependent stubs.

Important APIs, types, and functions: Exports watchdog globals, lockup detector init/reconfigure/cpu hotplug APIs, softlockup touch/reset helpers, hardlockup perf controls, NMI watchdog touch/check/start/stop/probe/enable/disable, backtrace trigger helpers, `nmi_trigger_cpumask_backtrace()`, `nmi_cpu_backtrace()`, sample-period helpers, and stall snapshot/check APIs. Detected source surface: 233 lines; includes `asm/irq.h`, `asm/nmi.h`, `linux/sched.h`; macros `LINUX_NMI_H`, `WATCHDOG_HARDLOCKUP_ENABLED`, `WATCHDOG_HARDLOCKUP_ENABLED_BIT`, `WATCHDOG_SOFTOCKUP_ENABLED`, `WATCHDOG_SOFTOCKUP_ENABLED_BIT`, `lockup_detector_offline_cpu`, `lockup_detector_online_cpu`, `sysctl_hardlockup_all_cpu_backtrace`, `sysctl_softlockup_all_cpu_backtrace`; structs none; enums none; typedefs none; function-like declarations/helpers `arch_perf_nmi_is_available`, `arch_touch_nmi_watchdog`, `hardlockup_config_perf_event`, `hardlockup_detector_disable`, `hardlockup_detector_perf_adjust_period`, `hardlockup_detector_perf_restart`, `hardlockup_detector_perf_stop`, `hw_nmi_get_sample_period`, `lockup_detector_init`, `lockup_detector_offline_cpu`, `lockup_detector_online_cpu`, `lockup_detector_reconfigure`, `lockup_detector_retry_init`, `lockup_detector_soft_poweroff`, `nmi_backtrace_stall_check`, `nmi_backtrace_stall_snap`, `nmi_cpu_backtrace`, `nmi_trigger_cpumask_backtrace`, and 19 more.

Control flow: Scheduler/timer/perf/NMI paths periodically touch watchdog state; lockup detectors compare progress and trigger warnings, panics, or CPU backtraces when thresholds are exceeded.

State and persistence behavior: Global watchdog enable bits, thresholds, panic flags, CPU masks, perf event configuration, and per-CPU watchdog state live in implementation files. This header exposes controls and stubs.

Dependencies and integration points: Depends on scheduler, IRQ/NMI architecture hooks, cpumasks, perf, and CPU hotplug. Used by kernel watchdog, panic diagnostics, and architecture NMI code.

Risks and test signals: Risks are false positives during long IRQ/NMI-off regions, missing watchdog touches, backtrace deadlocks, and config stub divergence. Test CPU hotplug, watchdog sysctls, induced soft/hard lockups, all-CPU backtrace, and perf NMI availability.
