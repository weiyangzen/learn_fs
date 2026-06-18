# sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h

Purpose: Defines a tracepoint for PCIe controller LTSSM state transitions. It exposes low-level link-training state-machine movement in host/controller drivers.

Important APIs/types/functions: `pcie_ltssm_state_transition` records device BDF, old state, and new state. Symbolic mapping uses PCIe LTSSM state constants.

Control flow: PCIe controller or endpoint code emits the event when the link-training and status state machine changes. The trace record allows ordering of link bring-up, recovery, and failure states.

State and persistence: No state is stored by the header. It observes controller hardware state and PCI core device identity.

Dependencies and integration points: Depends on PCI register definitions and tracepoints. It integrates with PCIe host controller drivers and low-level link diagnostics.

Risks and test signals: Risks include incomplete LTSSM enum coverage, noisy transitions during unstable links, and reading device identity while link/device is disappearing. Test cold boot link training, reset/retrain, endpoint hotplug, link-down recovery, and controller-specific error injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h` completely for this pass (58 lines, 1329 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h_research.md`.
