<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c

## Purpose
`pme.c` implements native PCIe Power Management Event signaling for Root Ports and Root Complex Event Collectors. It handles PME interrupts, identifies the requesting device, wakes/resumes that device, marks downstream devices wake-capable, and preserves wake behavior over system suspend.

## Important APIs, Types, and Functions
The main state type is `struct pcie_pme_service_data`, containing a spinlock, service pointer, work item, and `noirq` suspend/removal flag. Public helpers include `pcie_pme_interrupt_enable()` and `pcie_pme_init()`, with `pcie_pme_disable_msi()`/`pcie_pme_no_msi()` declared in `portdrv.h`. Core functions include `pcie_pme_irq()`, `pcie_pme_work_fn()`, `pcie_pme_handle_request()`, `pcie_pme_walk_bus()`, `pcie_pme_probe()`, `pcie_pme_suspend()`, `pcie_pme_resume()`, and `pcie_pme_remove()`.

## Control Flow and State
Probe limits the service to Root Ports/RCECs, allocates state, disables and clears PME, requests the IRQ, marks devices wake-capable, then enables PME interrupts. The IRQ disables PME interrupt generation and schedules non-freezable work. The worker loops while PME status or pending bits exist, clears root PME status, handles requester IDs, and re-enables interrupts unless suspended/removed. Suspend either enables IRQ wake if any downstream device may wake, or disables/clears PME and synchronizes the IRQ. Resume re-enables PME or disables IRQ wake depending on the suspend path.

## Dependencies and Integration Points
PME depends on PCIe port services, runtime PM, wakeup framework, RCEC walking, `pci_check_pme_status()`, `pm_request_resume()`, and `portdrv.c` IRQ assignment. DMI and command-line handling in `portdrv.c`/`pme.c` can force INTx instead of MSI because PME wake from sleep has platform quirks.

## Risks and Test Signals
Risks include spurious interrupts from stale status, missed PMEs while interrupts are disabled, requester IDs from PCIe-to-PCI bridges, races with suspend `noirq`, and MSI wake incompatibilities. Tests should cover root-port PME, RCEC PME, bridged PCI devices, wake from system sleep with MSI and INTx, runtime resume requests, spurious requester IDs, and removal while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/pme.c -->
