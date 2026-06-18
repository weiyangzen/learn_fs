# sources/distributed-fs/ceph-client/drivers/perf/marvell_pem_pmu.c

Purpose: This driver exposes Marvell PEM, a PCIe root-complex performance monitor, as a perf PMU. Each event maps to a fixed free-running 64-bit hardware counter for inbound, outbound, and ATS activity.

Important APIs, types, and functions: `enum pem_events` defines fixed event IDs. `eventid_to_offset_table[]` maps event IDs to MMIO offsets. `struct pem_pmu` stores PMU, base, owner CPU, device, and hotplug node. Key functions are `pem_perf_event_init()`, `pem_perf_read_counter()`, `pem_perf_event_update()`, start/add/stop/del, `pem_pmu_offline_cpu()`, probe/remove, and module init/exit. Sysfs helpers expose event aliases, `format/event`, and `cpumask`.

Control flow: module init registers a CPU hotplug state with an offline callback and registers the platform driver. Probe allocates state, maps the platform resource, fills a perf PMU with callback pointers and attr groups, chooses the current CPU, builds a PMU name from the resource address, adds the hotplug instance, and registers the PMU. Event init validates type, raw event ID range, no sampling, no per-task mode, real CPU target, and no mixed-PMU groups. Add sets `hw.idx` directly to the fixed event ID. Start snapshots the current free-running counter into `prev_count`; stop or read computes deltas.

State and persistence: The driver does not allocate programmable counters because all counters are fixed and free-running. It stores only the owner CPU and MMIO base plus perf event-local previous count. No persistent storage is used, and counters are not reset by this driver.

Dependencies and integration points: Supports ACPI ID `MRVL000E`; integrates with platform MMIO, perf core, CPU hotplug `CPUHP_AP_PERF_ARM_MRVL_PEM_ONLINE`, and sysfs. It does not use interrupts and does not advertise an explicit no-interrupt capability in the PMU struct.

Risks: `eventid_to_offset()` indexes the offset table directly, relying on event init and add range checks to prevent invalid IDs. Counters are free-running and deltas are simple unsigned subtraction, so wrap behavior depends on read frequency and 64-bit width. Because hardware counters are not reset, two perf sessions observe deltas from their start snapshot but cannot isolate activity system-wide. Multiple platform instances are named by resource address, which should be unique but depends on firmware resources.

Test signals: Verify PMU names like `mrvl_pcie_rc_pmu_<addr>` and sysfs event aliases for inbound/outbound/ATS counters. Run `perf stat` on fixed events and confirm counts increase under PCIe traffic. Test invalid raw event IDs return `-EINVAL`. Offline the owner CPU and verify context migration and cpumask update.
