# sources/distributed-fs/ceph-client/include/trace/events/pci.h

Purpose: Defines PCI and PCIe tracepoints for hotplug events and link-state changes. It helps diagnose PCI slot notifications and PCIe link speed/width transitions.

Important APIs/types/functions: `pci_hp_event` records slot name, slot number, device/function, and event code. `pcie_link_event` records bus/device/function, link speed, link width, and link state. Symbolic maps decode hotplug events and PCIe link speeds/widths.

Control flow: PCI hotplug and PCIe link-management code emit these events when slot events arrive or link parameters/state are observed. Tracepoint fields are copied from `struct pci_dev` and PCIe capability data.

State and persistence: No state is owned. It observes kernel PCI device and slot state; durable configuration is in hardware/firmware and PCI core data structures.

Dependencies and integration points: Depends on UAPI PCI register definitions and tracepoints. It integrates with PCI hotplug drivers, PCIe link training/power management, and ftrace/perf hardware diagnostics.

Risks and test signals: Risks include stale pci_dev/slot data during hot-remove, incorrect symbolic speed/width decoding, and missing vendor-specific hotplug reasons. Test PCIe hotplug, link retrain, ASPM changes, surprise removal, and builds across PCI configs.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pci.h` completely for this pass (129 lines, 3442 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pci.h_research.md`.
