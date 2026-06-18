# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-pci.c

## Purpose
`uhci-pci.c` is the PCI bus glue for the shared UHCI driver. It binds PCI class-code UHCI controllers, initializes PCI-specific legacy/wakeup behavior, supplies reset and quirk callbacks to `struct uhci_hcd`, and delegates HCD probing/removal/PM to usbcore PCI helpers.

## Important APIs, Types, And Functions
`uhci_pci_init()` is the HCD `.reset` callback. It stores `io_addr`, counts ports, sets vendor quirks (`oc_low`, `wait_for_hp`, Intel wakeup capability), fills reset/configuration/resume-detect/global-suspend callback pointers, and calls shared `check_and_reset_hc()`. `uhci_pci_configure_hc()` writes `USBLEGSUP` and disables Intel non-PME wakeup. `uhci_pci_resume_detect_interrupts_are_broken()` handles Genesys and Intel OC/resume-detect issues. `uhci_pci_global_suspend_mode_is_broken()` applies a DMI quirk for Asus A7V8X boards. PM callbacks disable/restore PCI legacy IRQ routing and wake bits. `uhci_driver` is the PCI `struct hc_driver`.

## Control Flow
The PCI driver matches any PCI device with class `PCI_CLASS_SERIAL_USB_UHCI`. Probe calls `usb_hcd_pci_probe()` with `uhci_driver`, which invokes `uhci_pci_init()` and then shared `uhci_start()`. Suspend clears PIRQ, optionally enables Intel USBRES wake bits, marks hardware inaccessible, synchronizes IRQs, and handles wakeup races by resuming and returning `-EBUSY`. Resume marks hardware accessible, resets on hibernation restore or checks/reconfigures otherwise, reports lost root-hub power if reset occurred, and polls root-hub status.

## State And Persistence Behavior
PCI-specific runtime state is stored in `struct uhci_hcd` quirk flags and callbacks plus PCI config space (`USBLEGSUP`, `USBRES_INTEL`). No durable driver state exists. Resume may intentionally discard root-hub state and force re-enumeration if the controller was reset or restored from hibernation.

## Dependencies And Integration Points
The file depends on PCI core, usbcore PCI HCD helpers, `pci-quirks.h` UHCI reset helpers, DMI, and the shared UHCI core. `MODULE_SOFTDEP("pre: ehci_pci")` encourages EHCI to bind before UHCI on companion-controller systems.

## Risks And Edge Cases
Vendor quirks materially affect wake behavior. Intel overcurrent and Genesys resume-detect issues can force root-hub polling. The DMI workaround disables EGSM on affected Asus boards with connected devices. `uhci_shutdown()` intentionally avoids locking because it may run in damaged-kernel contexts, but it assumes PCI driver data is still valid. `io_addr` requires IO-port UHCI; this file is built only when PCI and IO ports exist.

## Test Signals
Tests should cover PCI enumeration, legacy handoff, vendor quirks, suspend/resume with remote wakeup, hibernate restore, kexec/shutdown quiescence, EHCI/UHCI companion ordering, and root-hub re-enumeration after reset. Config-space inspection should show expected `USBLEGSUP`/`USBRES_INTEL` transitions.
