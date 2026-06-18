# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pci.c

## Purpose

`ohci-pci.c` is the PCI bus glue for generic USB OHCI controllers. It registers a PCI driver, applies controller-specific quirks before generic setup, and attaches PCI PM callbacks.

## Important APIs, Types, and Functions

Important functions include `ohci_pci_reset()`, `ohci_pci_probe()`, `ohci_pci_resume()`, and quirk callbacks `ohci_quirk_amd756()`, `ohci_quirk_ns()`, `ohci_quirk_zfmicro()`, `ohci_quirk_toshiba_scc()`, `ohci_quirk_nec()`, `ohci_quirk_amd700()`, `ohci_quirk_loongson()`, and `ohci_quirk_qemu()`. `ohci_pci_quirks[]` and `pci_ids[]` are the matching tables.

## Control Flow

Module init initializes the generic OHCI driver with a PCI reset override, installs PCI suspend/resume hooks, and registers `ohci_pci_driver`. Probe delegates most resource setup to `usb_hcd_pci_probe()`. Reset checks the quirk table for the PCI device, runs the quirk callback, calls `ohci_setup()`, and propagates PCI wakeup capability into `OHCI_CTRL_RWC`. NEC unrecoverable-error handling schedules a worker that calls `ohci_restart()`.

## State and Persistence Behavior

Persistent runtime state is in `ohci->flags`, optional NEC work item, modified `hcd->regs` for Loongson rev 0x02, and PCI core power-management state. Hardware quirk effects persist only for the lifetime of the HCD or current power state.

## Dependencies and Integration Points

It depends on PCI core matching/probing, `usb_hcd_pci_probe()`/remove/shutdown/PM helpers, `pci-quirks.h`, AMD PLL/prefetch helpers, and endian Kconfig options. It soft-depends on `ehci_pci` so EHCI companion handling loads first.

## Risks and Test Signals

Risks include quirk table regressions, unsupported big-endian Toshiba SCC builds, Loongson register-offset adjustment, AMD PLL/prefetch interaction with isochronous traffic, and broken suspend wakeup flags. Test signals include PCI OHCI enumeration, quirk-specific boot logs, suspend/resume across listed devices, NEC restart after injected UE, Loongson rev 0x02 register access, and companion EHCI coexistence.
