# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.c

## Purpose
Implements the PCI-facing Nitro Enclaves command transport and event handling. It binds the Amazon NE PCI device, maps MMIO registers, manages MSI-X vectors, serializes commands, and registers the misc device after hardware setup.

## APIs, Types, and Functions
Exports `ne_do_request()` and `struct pci_driver ne_pci_driver`. Internal helpers include `ne_submit_request()`, `ne_retrieve_reply()`, `ne_wait_for_reply()`, reply/event IRQ handlers, `ne_event_work_handler()`, MSI-X setup/teardown, PCI enable/disable, probe/remove/shutdown.

## Control Flow and State
Probe allocates `struct ne_pci_dev`, enables PCI, requests regions, maps BAR 3, sets driver data, configures MSI-X reply and event vectors, resets/enables device version, initializes command waitqueue/list/mutexes, sets global `ne_devs.ne_pci_dev`, and registers the misc device. `ne_do_request()` validates command type and payload sizes, locks `pci_dev_mutex`, clears reply flag, writes request bytes and command register, waits up to 120 seconds for reply IRQ, reads reply, clears flag, and converts device `rc` to Linux error. Event IRQ schedules work; work scans all running enclaves, asks `SLOT_INFO`, updates state, sets `has_event`, and wakes the enclave waitqueue when state changes.

## Dependencies and Integration
Depends on PCI/MSI-X, mapped NE MMIO ABI from `ne_pci_dev.h`, the misc-side enclave list and global `ne_devs`, Linux waitqueues/workqueues, and Nitro UAPI command semantics.

## Risks and Test Signals
Risks include long uninterruptible command waits, event work racing with enclave release/removal, global `ne_devs` lifetime, MSI-X vector count assumptions, and device disable timeout. Tests should cover invalid command sizes, reply timeout, negative device reply, event state change propagation, probe rollback at every failure label, remove/shutdown with active enclaves, and concurrent `ne_do_request()` callers.
