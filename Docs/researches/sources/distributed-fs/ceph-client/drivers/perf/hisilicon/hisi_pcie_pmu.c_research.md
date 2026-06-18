# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_pcie_pmu.c

Purpose: Implements the HiSilicon PCIe PMU for Huawei RCiEP PCI devices. It monitors PCIe bandwidth, latency, utilization, and packet/time companion metrics through BAR2 registers and exposes filters for event, threshold, trigger, length mode, root port, and requester BDF.

Important APIs, types, and functions: `struct hisi_pcie_pmu` stores eight active counter events, PCI device, PMU, BAR base, IRQ, identifier, monitored BDF range, and CPU owner. Filter extractors decode `config`, `config1`, and `config2`. Key functions are `hisi_pcie_pmu_get_event_ctrl_val()`, `hisi_pcie_pmu_valid_filter()`, `hisi_pcie_pmu_validate_event_group()`, `hisi_pcie_pmu_get_event_idx()`, `hisi_pcie_pmu_start/stop/add/del/read()`, `hisi_pcie_pmu_irq()`, and PCI probe/remove helpers.

Control flow: Module init registers a fixed CPU hotplug state and PCI driver. Probe enables the PCI device, requests BAR2, maps it, reads BDF range/info/version registers, requests one MSI vector, adds CPU hotplug, and registers perf. Event init chooses normal vs extended counter base from bit 16 of the event code, rejects sampling/task events, validates threshold/trigger limits and requester/root-port filters, validates grouped events while allowing related events with identical control values to share counters, and pins events to `on_cpu`. Start programs event control, enables counter/interrupt, initializes both normal and ext counters to `BIT_ULL(63)`, and updates userspace.

State and persistence: State is runtime-only. `hw_events[idx]` owns hardware counters; related grouped events can share a counter. Hardware counter registers are reset around starts and overflow IRQs. BDF range and identifier are read from hardware and exposed in sysfs.

Dependencies and integration: Uses PCI device IDs, MSI, BAR mapping, PCI topology helpers (`pcie_find_root_port`), perf PMU callbacks, sysfs groups, CPU hotplug, IRQ affinity, and Huawei vendor ID `0xa12d`.

Risks and test signals: BDF validation depends on PCI topology and proper refcounting; related-event sharing can be broken if group leaders differ; unsupported events may make counters unwritable, handled by period verification. Test filter rejection, shared latency/count event groups, overflow MSI accounting, sysfs BDF metadata, CPU hotplug affinity, and module remove cleanup.
