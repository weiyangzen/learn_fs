<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c

Purpose: provides the older MSR-backed Intel uncore frequency limits driver. It exposes per-logical-die min/max/current frequency controls through the same common uncore sysfs layer used by the TPMI implementation, but operates on `MSR_UNCORE_RATIO_LIMIT` and `MSR_UNCORE_PERF_STATUS` through one online control CPU per die.

Important APIs/types/functions: global `uncore_instances` stores one `struct uncore_data` per logical die, `uncore_cpu_mask` records the selected control CPU for each die, and `uncore_hp_state` stores the dynamic CPU hotplug state. `uncore_read_control_freq()`, `uncore_write_control_freq()`, and `uncore_read_freq()` perform MSR access. `uncore_event_cpu_online()` and `uncore_event_cpu_offline()` manage sysfs entry lifetime and control CPU migration. `uncore_pm_notify()` restores stored limits after suspend/hibernate.

Control flow: module init rejects hypervisors, matches against a large Intel CPU model table, allocates die instances, initializes `uncore-frequency-common`, registers CPU hotplug callbacks, and registers a PM notifier. On CPU online, the first online CPU in a die creates/updates the uncore entry and becomes the control CPU. On offline, if the control CPU goes away, another CPU in the die is selected or the die sysfs entry is removed. Reads and writes run on `data->control_cpu`; writes update `stored_uncore_data` for resume restoration.

State/persistence: the live control state is hardware MSR state. The driver caches only the full ratio-limit MSR after successful writes so that PM resume can restore it. Entries are valid only while a control CPU exists for the die; `control_cpu < 0` produces `-ENXIO`.

Dependencies/integration: uses x86 CPU model matching, topology die/package helpers, CPU hotplug, suspend notifiers, MSR helpers, and the common uncore sysfs code in namespace `INTEL_UNCORE_FREQUENCY`.

Risks: hotplug races are mitigated by the common layer and CPUHP sequencing, but stale `control_cpu` values would break MSR access. `uncore_pm_notify()` returns early on the first invalid/empty entry, which can skip later entries. Writing raw ratio limits accepts any nonzero ratio up to the mask maximum and does not validate min <= max. The driver intentionally avoids virtualized environments.

Test signals: load on supported Intel bare metal should create die-scoped uncore entries as CPUs come online; CPU hotplug should migrate or remove entries; sysfs writes should change MSR 0x620 and survive suspend/resume when `stored_uncore_data` is set; unsupported CPUs and hypervisors should fail probe with `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c -->
