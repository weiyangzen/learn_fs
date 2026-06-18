# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.c

## Purpose
Provides generic PCI bus glue for xHCI host controllers. It selects vendor/device quirks, initializes MSI/MSI-X or legacy interrupts, creates USB2 and optional USB3 root HCDs, handles PCI runtime/system PM, and exports common probe/remove helpers used by the Renesas firmware-loading driver.

## Important APIs, Types, And Functions
Public namespace exports are `xhci_pci_common_probe()` and `xhci_pci_remove()`. Core callbacks include `xhci_pci_setup()`, `xhci_pci_run()`, `xhci_pci_stop()`, `xhci_pci_suspend()`, `xhci_pci_resume()`, `xhci_pci_poweroff_late()`, and `xhci_pci_shutdown()`. Quirk and IRQ helpers include `xhci_pci_quirks()`, `xhci_try_enable_msi()`, `xhci_cleanup_msix()`, `xhci_msix_sync_irqs()`, `xhci_pme_quirk()`, `xhci_ssic_port_unused_quirk()`, `xhci_sparse_control_quirk()`, and ACPI LPM helpers.

## Control Flow
Module init initializes the generic `hc_driver` with PCI overrides and registers a class-matching PCI driver. Probe skips Renesas IDs when the dedicated Renesas driver is enabled, resets an optional reset controller, prevents runtime suspend during root-hub setup, invokes `usb_hcd_pci_probe()` for the USB2 HCD, creates and adds a shared HCD if needed, initializes xHCI extended capabilities, enables streams when supported, and adjusts runtime PM policy. Start enables MSI/MSI-X with fallback to legacy IRQ before `xhci_run()`. Suspend applies vendor PM quirks before `xhci_suspend()` and synchronizes MSI-X; resume resets optional reset control, performs Intel port switchover and PME quirks, then calls `xhci_resume()`.

## State And Persistence
State is runtime-only in `struct xhci_hcd`, `struct usb_hcd`, PCI device power/IRQ state, and quirk flags. PCI config and vendor MMIO PM tweaks persist only until device reset or power transition. The driver mutates runtime PM allow/forbid state and optional D3hot/D3cold policy but stores no filesystem data.

## Dependencies And Integration Points
Depends on PCI, ACPI, reset controls, USB HCD PCI helpers, generic xHCI setup/run/suspend/resume, tracepoints, AMD/Intel USB quirks, and the PM core. It integrates with `xhci-pci-renesas.c` through exported helpers and with usbcore through the HCD callback table.

## Risks And Test Signals
High-risk areas are vendor quirk matching, interrupt fallback and cleanup, dual-HCD lifetime, command/event behavior across PM transitions, D3cold policy, and shutdown wake quirks. Test signals include allmodconfig/randconfig builds, MSI-X/MSI/legacy IRQ operation, hotplug and remove, suspend/resume/runtime PM across Intel/AMD/ASMedia/VIA/Renesas hardware, Thunderbolt runtime PM, root hub LPM ACPI DSM handling, streams, and xHCI reset-on-resume paths.
