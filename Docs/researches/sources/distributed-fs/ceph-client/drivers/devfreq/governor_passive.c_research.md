<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c

Purpose: implements the immutable passive devfreq governor, which derives a child device frequency from either a parent devfreq transition stream or CPUFreq policy transitions.

Important APIs and control flow: `devfreq_passive_get_target_freq()` delegates to driver-provided `devfreq_passive_data.get_target_freq` when present; otherwise it uses required OPP translation or index interpolation for `DEVFREQ_PARENT_DEV`, and required OPP translation or percentage interpolation for `CPUFREQ_PARENT_DEV`. For devfreq parents, `devfreq_passive_register_notifier()` installs a transition notifier and `devfreq_passive_notifier_call()` updates children before parent frequency decreases and after parent frequency increases. For CPUFreq parents, `cpufreq_passive_register_notifier()` registers a CPUFreq transition notifier, builds one `devfreq_cpu_data` entry per related policy, holds CPU OPP tables, and triggers an initial target update. CPUFreq post-change notifications update cached policy frequency and call `devfreq_update_target()`.

State and persistence behavior: driver-supplied `struct devfreq_passive_data` is mutated to store `this`, notifier block, and CPU data list. CPU parent state includes per-policy device pointer, first CPU, OPP table reference, current/min/max kHz values. The governor itself is a global immutable `struct devfreq_governor`.

Dependencies and integration points: depends on devfreq transition notifiers, CPUFreq notifiers/policies, cpumasks, OPP required-opps translation, PM QoS clamped `devfreq_get_freq_range()`, and child drivers such as Exynos bus and MediaTek CCI.

Risks and test signals: CPU interpolation divides by `cpu_max - cpu_min`, so malformed CPU policies with equal bounds are unsafe. Error unwinding after partial CPU data allocation does not call `delete_parent_cpu_data()` in all paths. Notifier callbacks must avoid lock inversions; the devfreq-parent path uses nested locking. Required-OPP absence falls back to index/percentage mappings that may not reflect real hardware ratios. Test signals include parent devfreq scale-up/down ordering, CPUFreq transition handling for multi-policy systems, required-opps translation, fallback interpolation, governor immutability in sysfs, notifier unregister on stop, and CPU OPP table reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_passive.c -->
