# sources/distributed-fs/ceph-client/drivers/usb/core/hcd-pci.c

## Purpose

`hcd-pci.c` is the PCI bus glue for USB host controller drivers. It enables PCI devices, maps controller resources, allocates IRQ vectors for non-xHCI HCDs, creates and registers `struct usb_hcd` objects with the common HCD core, coordinates EHCI companion controllers, and supplies PCI system/runtime PM callbacks.

## Important APIs, Types, and Functions

- Companion coordination: `companions_rwsem`, `is_ohci_or_uhci()`, `for_each_companion()`, `ehci_pre_add()`, `ehci_post_add()`, `non_ehci_add()`, `ehci_remove()`, and PM-only `ehci_wait_for_companions()` coordinate EHCI with UHCI/OHCI controllers in the same PCI slot.
- Probe/remove/shutdown: `usb_hcd_pci_probe()`, `usb_hcd_pci_remove()`, and `usb_hcd_pci_shutdown()` are exported for PCI HCD drivers to use as standard callbacks.
- PowerMac platform hook: `powermac_set_asic()` toggles USB ASIC clocks under `CONFIG_PPC_PMAC`.
- PM gates: `check_root_hub_suspended()`, `suspend_common()`, `resume_common()`, sleep callbacks (`hcd_pci_suspend`, `hcd_pci_freeze`, `hcd_pci_suspend_noirq`, `hcd_pci_poweroff_late`, `hcd_pci_resume_noirq`, `hcd_pci_resume`, `hcd_pci_restore`) and runtime callbacks (`hcd_pci_runtime_suspend`, `hcd_pci_runtime_resume`) feed `usb_hcd_pci_pm_ops`.

## Control Flow

Probe begins by rejecting disabled USB or missing `hc_driver`, enabling the PCI device, and allocating one INTx/MSI vector for pre-USB3 HCDs. It creates an HCD with `usb_create_hcd()`, records AMD resume-bug state, maps either memory BAR 0 for memory-mapped controllers or the first I/O BAR for UHCI-style controllers, and sets bus mastering.

EHCI probe takes `companions_rwsem` for write, stores driver data, unconfigures and locks UHCI/OHCI companion root hubs before adding EHCI, calls `usb_add_hcd()`, clears drvdata on failure, then reconfigures/unlocks companions and records successful high-speed companion pointers. Non-EHCI probe takes the semaphore for read, adds the HCD, and records `hs_companion` if an EHCI controller is present. Successful probe enables controller wakeup and may drop runtime PM usage for run-wake-capable devices.

Remove reverses probe. It bumps runtime PM usage for run-wake devices, invokes a fake IRQ with local interrupts disabled so the driver can notice physical removal, clears EHCI companion pointers or the non-EHCI `hs_companion`, calls `usb_remove_hcd()`, clears drvdata under the companion semaphore, drops the HCD ref, frees IRQ vectors for pre-USB3 HCDs, and disables the PCI device. Shutdown calls the HCD `shutdown()` method when hardware is accessible, frees the primary IRQ, and disables PCI.

PM suspend uses `suspend_common()`: compute wakeup policy, require root hubs to already be suspended, call optional `driver->pci_suspend()`, avoid suspending if root-hub wakeup is pending, synchronize the IRQ when needed, and disable the PCI device. `hcd_pci_suspend_noirq()` saves PCI state, adjusts wakeup if the HCD is dead, prepares PCI sleep, and disables PowerMac ASIC clocks. Resume re-enables PCI, sets bus master, waits for EHCI companions on system resume, calls `driver->pci_resume()`, and reports controller death on failure.

## State and Persistence Behavior

State is live PCI/HCD state: `pci_set_drvdata()`, mapped BAR resources, allocated IRQ vectors, HCD resource fields, `hcd->self.hs_companion`, PCI power state, wakeup enablement, `hcd->amd_resume_bug`, and PowerMac ASIC clock state. No durable persistence exists.

## Dependencies and Integration Points

This file integrates PCI core APIs, Linux PM callbacks, common HCD lifecycle (`usb_create_hcd()`, `usb_add_hcd()`, `usb_remove_hcd()`, `usb_put_hcd()`), PCI resource management, IRQ allocation, EHCI/UHCI/OHCI class codes, xHCI-specific IRQ ownership convention, root-hub configuration via `usb_set_configuration()`, and platform PowerMac firmware hooks.

## Risks and Edge Cases

- EHCI companion ordering is subtle: companions are unconfigured and locked while EHCI grabs ports, then reconfigured after success/failure. Locking or drvdata ordering mistakes can break low/full-speed devices.
- xHCI manages IRQs itself, so generic IRQ allocation/free must remain gated by HCD speed flags.
- PM suspend must happen only after root hubs are suspended; otherwise DMA or downstream traffic may continue while PCI is disabled.
- Wakeup races are explicitly checked before and after `pci_suspend()`. Missing these checks can lose wake events.
- Physical removal can occur before remove; the fake IRQ path gives HCDs a chance to detect inaccessible hardware.
- Shared HCDs and primary IRQ ownership require careful shutdown/remove handling.

## Test Signals

Signals include PCI HCD probe/remove for UHCI/OHCI/EHCI/xHCI-style drivers, EHCI companion handoff with same-slot controllers, PCI BAR conflict and IRQ allocation failure injection, runtime suspend/resume with root hub suspended, system suspend/resume with wakeup pending, controller death during resume, PowerMac clock paths when configured, and hot-unplug/CardBus-style removal.
