# sources/distributed-fs/ceph-client/drivers/perf/fujitsu_uncore_pmu.c

Purpose: Provides ACPI platform perf PMUs for Fujitsu uncore MAC and PCI blocks. Both variants share generic counter control while exposing different event catalogs and names derived from ACPI UID fields.

Important APIs, types, and functions: `struct uncore_pmu` stores counter count, `struct pmu`, MMIO registers, active events, used bitmap, CPU, IRQ, and device. Counter paths are `fujitsu_uncore_counter_start()`, `fujitsu_uncore_counter_stop()`, `fujitsu_uncore_counter_update()`, and `fujitsu_uncore_init()`. Perf callbacks include `fujitsu_uncore_event_init/add/del/start/stop/read()` and `fujitsu_uncore_pmu_enable/disable()`. ACPI IDs `FUJI200C` and `FUJI200D` select MAC or PCI event groups.

Control flow: Module init registers a CPU hotplug state and the platform driver. Probe reads ACPI UID, allocates state, chooses MAC vs PCI counter count/event groups/name, allocates event and bitmap arrays, maps MMIO, resets hardware, requests IRQ, sets IRQ affinity, adds hotplug instance, and registers perf. Event init rejects sampling and CPU-less task mode, validates group capacity, and pins the event to the selected CPU. Add allocates one of eight counters, start writes event type, enables interrupt, and enables the counter. IRQ reads overflow status, clears it, and updates active events.

State and persistence: State is in device memory and MMIO only. The used bitmap owns counters; `events[idx]` maps counters to perf events; `prev_count` tracks deltas. Remove disables PMU control, unregisters perf, and removes CPU hotplug.

Dependencies and integration: Uses ACPI matching and UID parsing, platform MMIO/IRQ resources, perf PMU APIs, CPU hotplug, IRQ affinity, and sysfs format/events/cpumask groups.

Risks and test signals: The PMU advertises `PERF_PMU_CAP_NO_INTERRUPT` despite requesting overflow IRQs, which should be verified against perf semantics. Group validation counts only number of PMU events, not event-code validity beyond 8-bit masking. Test with both ACPI IDs, event listing, overflow IRQ update, NUMA-local CPU migration on online/offline, and UID-derived names.
