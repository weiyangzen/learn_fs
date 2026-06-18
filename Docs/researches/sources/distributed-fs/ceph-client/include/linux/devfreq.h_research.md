# sources/distributed-fs/ceph-client/include/linux/devfreq.h

Purpose: Defines the generic Dynamic Voltage and Frequency Scaling framework for non-CPU devices, including profiles, devices, governors, notifiers, OPP helpers, PM integration, QoS limits, statistics, and passive governor data.

Important APIs, types, and functions: Key types are `enum devfreq_timer`, `struct devfreq_dev_status`, `struct devfreq_dev_profile`, `struct devfreq_stats`, `struct devfreq`, `struct devfreq_freqs`, `struct devfreq_simple_ondemand_data`, and `struct devfreq_passive_data`. APIs add/remove devfreq devices, devm-manage them, suspend/resume one or all devices, update frequency, get recommended OPPs, register OPP and transition notifiers, and find devfreq devices by DT node/phandle.

Control flow: A device driver supplies a profile with target and status callbacks, initial frequency, polling interval, optional frequency table, cooling flag, and sysfs groups. The devfreq core creates an embedded device, attaches a governor, monitors load by delayed work or governor events, chooses a target frequency, calls the profile `target()`, updates statistics, and notifies listeners before/after transitions. Passive governors can follow a parent devfreq or cpufreq policy.

State and persistence: Runtime state includes the devfreq device, mutex, profile, governor, OPP table reference, delayed work, frequency table, previous frequency, last status, governor/user data, PM QoS requests, scaling limits, suspend counters/frequencies, transition stats, notifier head, and optional thermal cooling device. No persistent storage is defined.

Dependencies and integration points: Depends on device core, notifiers, PM OPP, PM QoS, workqueues, SRCU notifiers, thermal cooling, firmware phandles, and optional cpufreq parent data. Disabled builds return inert stubs.

Risks and test signals: Risks include profile callbacks returning stale current frequency, unsorted frequency tables, QoS/OPP limit mismatches, stats races without `devfreq->lock`, suspend/resume imbalance, notifier leaks, and passive governor cycles. Test add/remove/devm cleanup, all built-in governors, OPP table changes, PM QoS sysfs limits, transition notifier ordering, suspend/resume nesting, thermal cooling registration, and `CONFIG_PM_DEVFREQ=n` builds.
