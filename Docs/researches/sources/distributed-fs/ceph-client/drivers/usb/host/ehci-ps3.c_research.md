# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ps3.c

## Purpose
Sony PS3 system-bus EHCI driver. It opens PS3 hypervisor devices, creates DMA/MMIO regions, maps interrupts, configures PS3-specific EHCI internal setup registers after reset, and exposes a complete EHCI `hc_driver`.

## Important APIs, types, and functions
`ps3_ehci_setup_insnreg()` applies PS3 errata fix 316 for reset-lost internal registers. `ps3_ehci_hc_reset()` enables big-endian MMIO, sets caps, calls `ehci_setup()`, then restores the insn registers. `ps3_ehci_probe()` and `ps3_ehci_remove()` manage hypervisor, DMA, MMIO, IRQ, HCD, and memory resources. `ps3_ehci_driver_register()` only registers on PS3 LV1 firmware.

## Control flow
Probe rejects disabled USB, opens the hypervisor device, creates DMA and MMIO regions, maps an I/O IRQ, installs a dummy 32-bit DMA mask, creates the HCD, requests and ioremaps MMIO, stores drvdata, and calls `usb_add_hcd()`. Remove unregisters the HCD, clears drvdata, unmaps/releases MMIO, destroys IRQ and PS3 regions, frees DMA, and closes the HV device. Shutdown is the same as remove.

## State and persistence behavior
State spans PS3 system-bus region descriptors, virtual IRQ, HCD fields, and PS3 EHCI insn registers. The insn register settings must be rewritten after every EHCI reset because hardware resets them.

## Dependencies and integration points
Depends on PS3 firmware feature detection, PS3 system bus, hypervisor region APIs, big-endian MMIO helpers, DMA APIs, and shared EHCI callbacks.

## Risks and edge cases
The probe failure ladder is long and must release resources in reverse order. `BUG_ON()` is used for unexpected PS3 region and remove states. Shutdown equals remove, so double-remove style paths must not occur. Big-endian descriptors are not set, only MMIO.

## Test signals
Boot on PS3 LV1 firmware, no-op registration on non-PS3 firmware, probe failure at each HV/DMA/MMIO/IRQ/HCD step, reset reprogramming of insn registers, root-hub enumeration, remove/shutdown, and IRQ delivery are important signals.
