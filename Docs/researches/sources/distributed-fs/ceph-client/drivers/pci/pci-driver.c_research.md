# sources/distributed-fs/ceph-client/drivers/pci/pci-driver.c

## Purpose
Implements the PCI bus type and driver binding core. It handles dynamic IDs, device/driver matching, probe/remove/shutdown, NUMA-aware probe execution, runtime/system PM dispatch, DMA/IOMMU setup, uevents, and registration of the PCI bus with the driver core.

## APIs, Types, And Functions
Exports `pci_add_dynid()`, `pci_match_id()`, `__pci_register_driver()`, `pci_unregister_driver()`, `pci_dev_driver()`, `pci_dev_get()`, `pci_dev_put()`, and `pci_bus_type`. Key internals include `struct pci_dynid`, `pci_match_device()`, sysfs `new_id`/`remove_id`, `pci_call_probe()`, `pci_device_probe()`, `pci_device_remove()`, `pci_device_shutdown()`, PCI PM callbacks, `pci_dma_configure()`, and `pci_driver_init()`.

## Control Flow
Driver matching honors binding disallow rules, `driver_override`, dynamic IDs, static ID tables, and `override_only` entries. Probe assigns IRQs, allocates platform IRQ state, takes a device reference, optionally runs probe work on a housekeeping CPU local to the device NUMA node, sets runtime PM state, and records `pci_dev->driver`. Remove runs driver remove with runtime PM barriers, frees IRQs, removes SR-IOV state, unwinds runtime PM, marks D0 state unknown, and drops the reference. PM callbacks route legacy and modern driver callbacks across suspend/resume/hibernate/runtime phases while saving/restoring config state, PTM, PME, bridge power-up actions, and fixups. Bus initialization allocates the probe workqueue and registers `pci_bus_type` and optionally the PCIe port bus.

## State And Persistence
State includes per-driver dynamic ID lists, `pci_dev->driver`, probe flags, runtime PM usage counts, saved PCI config state, current power state, bus type registration, and a global probe workqueue. Sysfs driver attributes mutate dynamic ID state but no disk persistence is used.

## Dependencies And Integration
Depends on the Linux driver core, PCI core helpers, PM core, CPU hotplug/housekeeping masks, IOMMU/DMA APIs, OF/ACPI DMA configuration, SR-IOV, AER/EEH recovery uevents, and PCIe port bus registration. It is the central integration point for all PCI drivers.

## Risks And Test Signals
High-risk areas are dynamic ID parsing and duplicate detection, driver_override matching, probe workqueue CPU selection under hotplug, runtime PM reference balancing, remove ordering versus `runtime_idle`, PM state-save warnings, D3cold bridge resume propagation, DMA default-domain cleanup, and bus registration failure unwind. Test signals include sysfs `new_id/remove_id`, driver override binding, SR-IOV VF autoprobe disabled/enabled, probe failure cleanup, hotplug remove, kexec shutdown bus-master clearing, suspend/resume/hibernate/runtime PM matrices, IOMMU default domain errors, and uevent modalias contents.
