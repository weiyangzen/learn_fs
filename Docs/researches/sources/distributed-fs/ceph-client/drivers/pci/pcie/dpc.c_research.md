<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c

## Purpose
`dpc.c` implements the Downstream Port Containment service. DPC contains fatal link errors by hardware-disabling the link, logs the containment reason and optional Root Port PIO detail, coordinates with hotplug for DPC-induced link events, and recovers affected devices via PCI error recovery.

## Important APIs, Types, and Functions
Important functions include `pci_save_dpc_state()`, `pci_restore_dpc_state()`, `pci_dpc_recovered()`, `dpc_reset_link()`, `dpc_process_error()`, `pci_dpc_init()`, and `pcie_dpc_init()`. Service callbacks are `dpc_probe()`, `dpc_suspend()`, `dpc_resume()`, and `dpc_remove()`. Local helpers process RP PIO logs, surprise removal, DPC IRQs, and enable/disable control bits.

## Control Flow and State
`pci_dpc_init()` discovers the DPC extended capability and Root Port extensions/log size. Probe requires native AER or DPC-native ownership, requests a threaded IRQ, enables fatal-error DPC and interrupts, logs capabilities, and registers a saved control-word buffer. On IRQ, the hard handler acknowledges interrupt status and wakes the thread when trigger status is set. The thread treats surprise removal specially; otherwise it logs the error, calls `pcie_do_recovery()` with frozen state and `dpc_reset_link()`. Reset waits for link inactive, waits for RP inactive when needed, clears trigger status, waits for the secondary bus, and updates `PCI_DPC_RECOVERED`/`PCI_DPC_RECOVERING`.

## Dependencies and Integration Points
DPC depends on AER availability, PCIe port service registration, `pcie_do_recovery()` from `err.c`, AER parsing helpers from `aer.c`, hotplug synchronization via `pci_dpc_recovered()`, and EDR firmware recovery in `edr.c`. It uses private PCI saved-capability state and TLP log helpers for RP PIO diagnostics.

## Risks and Test Signals
Risks include recovery deadlock or missed wakeups around hotplug, incorrect handling when firmware owns DPC, surprise-removal false positives, invalid RP PIO log sizes, and failures waiting for link/RP inactive. Tests should exercise DPC fatal interrupts, RP PIO logs, hotplug link-down suppression, ACPI EDR paths, suspend/resume of DPC control, surprise removal on hotplug ports, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/dpc.c -->
