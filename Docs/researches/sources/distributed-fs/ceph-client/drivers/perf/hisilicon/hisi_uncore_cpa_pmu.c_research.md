# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_cpa_pmu.c

Purpose: Provides the HiSilicon Coherency Protocol Agent uncore PMU shell over the shared `hisi_uncore_pmu` framework.

Important APIs, types, and functions: Device-specific ops implement counter offsets, 64-bit reads/writes, two packed event-type registers, global counter start/stop, per-counter enable/interrupt mask, interrupt status/clear, and CPA power-management disable/enable. `hisi_cpa_pmu_dev_probe()` initializes topology, MMIO, IRQ, counter metadata, attribute groups, and framework ops.

Control flow: ACPI match `HISI0281` binds the platform driver. Probe requires `sicl_id` and `index_id`, maps resources, reads `CPA_VERSION`, initializes IRQ through the common helper, names the PMU `hisi_sicl%d_cpa%d`, initializes the common PMU, disables CPA power management, adds CPU hotplug, and registers perf. Remove unregisters perf, removes hotplug, and re-enables CPA power management.

State and persistence: Runtime state is in `struct hisi_pmu` plus CPA MMIO registers. Disabling PM is a persistent hardware side effect for the device lifetime and is restored on failure/remove.

Dependencies and integration: Depends on ACPI properties, platform MMIO/IRQ resources, the exported HiSilicon uncore framework, perf PMU registration, CPU hotplug, and `MODULE_IMPORT_NS("HISI_PMU")`.

Risks and test signals: Failure paths must restore PM control when hotplug or perf registration fails. Event encoding is limited to 8-bit event types but sysfs advertises `config:0-15`. Test ACPI topology parsing, PM restore on probe failure/remove, interrupt overflow handling through the common ISR, and advertised CPA events.
