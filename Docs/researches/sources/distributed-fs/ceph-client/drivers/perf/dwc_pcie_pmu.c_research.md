# sources/distributed-fs/ceph-client/drivers/perf/dwc_pcie_pmu.c

Purpose: Provides a perf PMU for Synopsys DesignWare PCIe Root Port RAS DES vendor capabilities. It supports manually controlled time-based counters and per-lane event counters for PCIe/CCIX link activity, discovered by scanning PCIe VSEC capabilities.

Important APIs, types, and functions: `struct dwc_pcie_pmu` holds the perf PMU, root-port PCI device, RAS DES offset, lane count, one active time-based event, lane event bitmap, CPU hotplug node, and active CPU. `struct dwc_pcie_dev_info` tracks synthetic platform devices created for matching PCI devices. Key paths are `dwc_pcie_des_cap()`, `dwc_pcie_register_dev()`, `dwc_pcie_pmu_probe()`, `dwc_pcie_pmu_event_init()`, `dwc_pcie_pmu_event_add()`, `dwc_pcie_pmu_event_start/stop/del()`, and `dwc_pcie_pmu_event_update()`.

Control flow: Module init scans all PCI devices for matching DWC RAS DES VSECs, creates platform devices, sets up CPU hotplug, registers the platform driver, and installs a PCI bus notifier for hotplug add/delete. Probe reconstructs the PCI device from SBDF platform ID, validates the VSEC, computes link width, names the PMU `dwc_rootport_<sbdf>`, adds CPU hotplug, and registers perf callbacks. Event init validates PMU type, rejects sampling/task events, checks group PMU compatibility, validates lane bounds, and enforces that a group has at most one time-based event and no duplicate lane event/group slots.

State and persistence: State is volatile in kernel memory and PCI config space. Lane event occupancy is tracked in a bitmap indexed by group 6/7 event number; the time-based counter is exclusive via `time_based_event`. Counter values live in RAS DES registers and are read/cleared through PCI config operations.

Dependencies and integration: Integrates with PCI enumeration and hotplug notifier APIs, DesignWare PCIe VSEC ID tables from `<linux/pcie-dwc.h>`, platform devices, perf PMU registration, CPU hotplug migration, and sysfs `events`, `format`, and `cpumask` groups.

Risks and test signals: The driver uses PCI config-space operations for live counter control, so races around hot-unplug and stale `pdev` references are important. Time-based 64-bit reads use a high/low/high loop; tests should exercise wrap and consistency. Signals include platform device creation for each VSEC, `perf list` lane/time events, rejection of invalid lanes and duplicate grouped lane events, hotplug add/remove cleanup, and context migration when the owner CPU goes offline.
