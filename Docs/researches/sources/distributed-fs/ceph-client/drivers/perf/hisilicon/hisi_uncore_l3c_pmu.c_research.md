# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_l3c_pmu.c

Purpose: Implements HiSilicon L3 cache uncore PMUs across v1/v2/v3 hardware, including v3 extension counter banks with separate MMIO/IRQ resources and trace/data filters.

Important APIs, types, and functions: `struct hisi_l3c_pmu` wraps `struct hisi_pmu` and extension bases/IRQs. `hisi_l3c_pmu_get_event_idx()` allocates normal or extension ranges and stores the correct MMIO base in `hw.event_base`. Filter helpers configure request trace tag, core trace tag, data source, and socket filtering. Ops cover event type programming, counter access, multi-bank start/stop, interrupt status aggregation, and filter validation.

Control flow: ACPI IDs select v1/v2/v3 device info. Probe validates SCCL/CCL topology, maps base MMIO, initializes the normal IRQ, initializes extension MMIO/IRQs for v3, expands `num_counters` by extension bank count, names the PMU with SCCL/CCL/sub-id, adds a custom hotplug state, initializes the common PMU, and registers perf. Online/offline callbacks delegate to common CPU migration and then migrate extension IRQ affinities.

State and persistence: Counter allocation spans normal and extension bit ranges in the common used mask. Event MMIO base is per-event, allowing common paths to operate on normal or extension registers. Filter state is hardware MMIO and must be cleared on stop.

Dependencies and integration: Uses platform MMIO/IRQ arrays, ACPI matching, common HiSilicon uncore framework, perf PMU, CPU hotplug, sysfs filters, and IRQ affinity.

Risks and test signals: Extension initialization requires enough IRQ resources and matching extra MMIO resources. `ext` filter validation and deprecated/new `tt_core` mutual exclusion are important. Test v1/v2/v3 event visibility, extension event allocation, aggregate overflow status, extension IRQ affinity migration, and filter cleanup.
