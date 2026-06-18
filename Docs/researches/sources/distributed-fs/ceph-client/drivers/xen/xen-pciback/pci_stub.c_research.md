# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/pci_stub.c

## Purpose
`pci_stub.c` is the host-side PCI capture and lifetime manager for Xen PCI passthrough. It registers the `pciback` PCI driver early, seizes devices listed by the `hide=` module parameter or driver-override binding, initializes Xen pciback config-space metadata, resets and disables the hardware, and later hands exclusive references to `xen-pciback/xenbus.c` for assignment to guest domains.

## Important APIs, Types, And Functions
The central objects are `struct pcistub_device`, which wraps a real `struct pci_dev` plus a kref and current `xen_pcibk_device *pdev`, and `struct pcistub_device_id`, which records BDFs to seize. Exported integration points are `pcistub_get_pci_dev_by_slot()` and `pcistub_put_pci_dev()`. Initialization flows through `pcistub_init()`, `pcistub_init_devices_late()`, `pcistub_probe()`, `pcistub_seize()`, and `pcistub_init_device()`. Cleanup and rebinding use `pcistub_remove()` and `pcistub_device_release()`. AER support is implemented by `xen_pcibk_error_detected()`, `xen_pcibk_mmio_enabled()`, `xen_pcibk_slot_reset()`, `xen_pcibk_error_resume()`, and shared `common_process()`.

## Control Flow
At boot/module load, `xen_pcibk_init()` requires the initial domain, initializes config-space handling, registers/seizes PCI devices, completes deferred device setup, then registers the Xenbus backend. Device seize allocates a `pcistub_device`, saves PCI config state, prepares MSI-X with Xen when available, resets the device, disables it, and marks it assigned. When xenbus requests a BDF, `pcistub_get_pci_dev_by_slot()` atomically marks the seized device in use by a backend instance. Release takes the device lock, resets hardware, restores the saved state, frees dynamic emulated config fields, clears interrupt-control flags, unregisters Xen domain ownership, and drops the kref. PCIe AER callbacks pause removal/reconfiguration with `pcistub_sem`, notify the frontend through the shared pciback page, and may mark the guest failed in Xenstore if no frontend AER handler responds.

## State And Persistence
Persistent runtime state lives in global lists: `pcistub_device_ids`, `pcistub_devices`, and early `seized_devices`. Per-device persistent state is stored in `xen_pcibk_dev_data`, including saved PCI state, permissive/config flags, fake INTx handler status, and IRQ accounting. Sysfs driver attributes (`new_slot`, `remove_slot`, `slots`, `quirks`, `permissive`, `allow_interrupt_control`, `irq_handlers`, `irq_handler_state`) mutate or expose this state. Xenstore is used only for AER failure notification here.

## Dependencies And Integration Points
The file depends on Linux PCI core, krefs, sysfs driver attributes, Xen event/channel and physdev hypercalls, Xen ACPI/PVH GSI helpers, pciback config-space helpers, and Xen domain ownership helpers. It integrates tightly with `pciback_ops.c` for resets and fake IRQ handling, `xenbus.c` for guest assignment, and `conf_space*.c` for virtual PCI config behavior.

## Risks
This code handles physical devices and guest-controlled state, so ordering is critical. Risks include stale saved PCI state, racing AER with device removal, shared IRQ mis-accounting, unsafe `permissive` config writes, device removal while a guest still has BAR access, and mismatched kref/list ownership around `pcistub_put_pci_dev()`. AER waits have a long timeout and depend on frontend cooperation.

## Test Signals
Useful signals are successful binding to `pciback`, sysfs `slots`/`irq_handlers` output, Xenstore backend device assignment, PCI FLR/reset logs, guest attach/detach cycles, MSI/MSI-X prepare/release warnings, AER recovery logs, and absence of leaked assigned devices after guest shutdown or driver unbind.
