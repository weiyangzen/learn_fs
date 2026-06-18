# sources/distributed-fs/ceph-client/drivers/perf/qcom_l3_pmu.c

Purpose: Qualcomm L3 cache uncore PMU driver for ACPI-described L3 cache slices. Each slice is exposed as an independent perf PMU named from parent/child ACPI UIDs, with userspace expected to aggregate per-slice counts for socket-wide cache behavior.

Important APIs, types, and functions: `struct l3cache_pmu` embeds `struct pmu`, MMIO base, counter event slots, allocation bitmap, hotplug node, and active CPU mask. `struct l3cache_event_ops` abstracts standard 32-bit counters versus chained 64-bit "long counter" mode selected by config bit `L3_EVENT_LC_BIT`. Perf callbacks are `qcom_l3_cache__event_init`, `event_add`, `event_del`, `event_start`, `event_stop`, `event_read`, `pmu_enable`, and `pmu_disable`; sysfs exposes `format/event`, `format/lc`, named cache events, and `cpumask`.

Control flow: probe requires an ACPI companion, maps the register resource, resets the basic counter and perfmon blocks through `qcom_l3_cache__init`, requests the overflow IRQ, registers a CPU hotplug instance, and finally calls `perf_pmu_register`. Event init rejects sampling and task mode, validates groups do not span unrelated hardware PMUs, and pins `event->cpu` to the exported PMU CPU. Add allocates one counter or an adjacent pair via `bitmap_find_free_region`; start programs event type, counter, interrupt/gang mode, and enables hardware. IRQ handling reads and clears `L3_M_BC_OVSR`, then updates only events with overflow bits.

State and persistence: state is entirely runtime MMIO and in-memory perf state. `used_mask`, `events[]`, `prev_count`, and `count` persist only while events are active. Hotplug migrates perf context and updates `cpumask` when the chosen CPU goes offline. No disk state exists.

Dependencies and integration: depends on Linux perf, ACPI, platform devices, IRQs, CPU hotplug, and MMIO helpers. Integrates with perf tooling through PMU sysfs event/format groups and ACPI ID `QCOM8081`.

Risks: 64-bit mode requires adjacent even/odd counter allocation and uses the odd counter as an overflow counter; mistakes in bitmap order or event grouping would corrupt counts. 32-bit overflow depends on MSB-toggle IRQ behavior and prompt ISR updates. Probe registers hotplug before perf registration; failure cleanup relies on devm and lacks explicit hotplug removal in the error path. Test signals include ACPI probe, sysfs PMU presence, `perf stat -a -e l3cache_*/read-miss/`, long-counter config, overflow-heavy 32-bit runs, and CPU offline migration.
