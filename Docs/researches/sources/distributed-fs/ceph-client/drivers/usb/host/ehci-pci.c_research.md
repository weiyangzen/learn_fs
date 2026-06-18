# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-pci.c

## Purpose
PCI bus glue for EHCI controllers. It matches generic PCI EHCI class devices, applies vendor/device-specific quirks before and after `ehci_setup()`, handles PCI MWI and suspend/resume reinitialization, and delegates normal PCI HCD management to USB core helpers.

## Important APIs, types, and functions
`ehci_pci_setup()` is the reset/setup hook. `ehci_pci_reinit()` enables PCI MWI and programs Intel Quark thresholds. `ehci_pci_resume()` resumes via common EHCI and reinitializes if needed. `ehci_pci_probe()` bypasses known devices with dedicated drivers. `pci_overrides` installs the reset hook; module init fills `pci_suspend` and `pci_resume` in the generated `hc_driver`.

## Control flow
Probe rejects bypass IDs and calls `usb_hcd_pci_probe()`. During setup, the driver sets `ehci->caps = hcd->regs`, applies pre-setup quirks such as endian MMIO, NVIDIA coherent mask reduction, integrated TT flags, AMD PLL/dummy-QH workarounds, VIA sleep timing, Synopsys/Aspeed flags, and Zhaoxin wakeup handling. It detects an EHCI debug port, calls `ehci_setup()`, then applies post-setup quirks, fixes bogus companion-port counts for some controllers, reads SBRN when available, enables legacy wakeup when needed, and runs PCI reinit. Remove clears MWI and delegates teardown.

## State and persistence behavior
State is mostly quirk bits in `struct ehci_hcd`, PCI config values, DMA mask constraints, `ehci->debug`, SBRN, and MWI state. Workarounds alter hardware thresholds, PCI config bytes, and EHCI schedule behavior for the device lifetime.

## Dependencies and integration points
Depends on PCI core, USB PCI HCD helpers, `pci-quirks.h`, AMD USB quirk helpers, EHCI core, and USB PM ops. It integrates with all generic PCI EHCI controllers via `PCI_CLASS_SERIAL_USB_EHCI`, plus an STMicro host ID.

## Risks and edge cases
Quirk ordering matters because DMA allocation constraints must precede `ehci_setup()`, while some controller bits must follow reset. The generic class match can bind hardware that really needs a specialized driver unless bypassed. Vendor-specific assumptions affect memory safety, wakeup, schedule unlinking, and debug-port access.

## Test signals
Probe/remove on Intel, NVIDIA, AMD/ATI, VIA, Aspeed, Huawei/Synopsys, NetMos, Zhaoxin, and generic controllers; hibernation restore; debug-port detection; large-memory DMA; dummy-QH scheduling; IAA watchdog behavior; and PCI PM wakeup are critical signals.
