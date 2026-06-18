# sources/distributed-fs/ceph-client/drivers/pci/controller/vmd.c

## Purpose
Implements Intel Volume Management Device support. VMD exposes a PCI device that contains an emulated PCI domain and root bus for hidden downstream root ports, with special config access, resource windows, MSI/MSI-X remapping or bypass, ACPI companion lookup, power-management quirks, and teardown.

## Important APIs, Types, And Functions
Core state types are `struct vmd_dev`, `struct vmd_irq_list`, and `struct vmd_irq`. Important functions include `vmd_probe()`, `vmd_enable_domain()`, `vmd_create_irq_domain()`, `vmd_msi_alloc()`, `vmd_irq()`, `vmd_pci_read()`, `vmd_pci_write()`, `vmd_domain_reset()`, `vmd_get_phys_offsets()`, `vmd_get_bus_number_start()`, `vmd_pm_enable_quirk()`, `vmd_remove()`, `vmd_suspend()`, and `vmd_resume()`.

## Control Flow
PCI probe checks Xen constraints, enables the VMD device with `pcim_enable_device()`, maps CFGBAR, sets DMA mask/mastering, chooses first vector offset, and calls `vmd_enable_domain()`. Domain setup derives bus/resource windows, optionally reads physical membar shadow offsets, decides whether MSI remapping is required, allocates VMD vectors and an MSI parent domain, creates an emulated root bus, scans children, resets downstream bridge windows, assigns resources, applies LTR/ASPM quirks, configures real root-port settings, and adds devices.

## State And Persistence
Persistent state includes emulated domain number, bus start, resources, CFGBAR mapping, child bus, IRQ lists, SRCU guards, MSI domain, VMD instance id/name, and config-space spinlock. Hardware state includes VMCONFIG MSI remap bits, MSI-X vectors, bridge windows, and child device power/link state.

## Dependencies And Integration Points
Integrates with PCI core bus/resource scanning, x86 MSI address format, generic MSI domains, ACPI companion lookup hooks, SRCU/RCU irq demux, Xen detection, PCI PM/ASPM/LTR helpers, and Intel PCI IDs.

## Risks
MSI remap versus bypass decisions affect interrupt correctness, especially under virtualization. Shared-vector lists require correct SRCU synchronization during free and demux. Config access is serialized to avoid hardware deadlock. Resource offset/shadow logic is critical for guest passthrough. ACPI hook installation is global and must be bracketed around scan.

## Test Signals
Validate NVMe devices behind VMD, interrupt delivery in remap and bypass modes, suspend/resume vector restoration, remove/shutdown cleanup, Xen guests, ACPI companion binding, VMD client IDs using BIOS PM quirks, and resource assignment with membar shadow offsets.
